import asyncio
import collections
import random
import time
import logging
from typing import Dict, Optional
from config import POINTS_PER_WORD, FIRST_FIND_PTS, COMBO_MULTIPLIERS

log = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HARD MODE CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HARD_GRID_SIZE        = 11
HARD_N_WORDS_MIN      = 10
HARD_N_WORDS_MAX      = 15
HARD_DURATION_MIN     = 300   # secs
HARD_DURATION_MAX     = 360   # secs
HARD_POINTS_PER_WORD  = 10    # pts per normal find in hard mode (min)
HARD_FIRST_PTS        = 25    # pts for first find in hard mode (max)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ROUND LEVEL TABLE  (12 rounds)
#  round_num → (duration_secs, words_to_find, grid_size)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROUND_LEVELS = {
    1:  (50,  3,  4),
    2:  (80,  4,  5),
    3:  (110,  5,  6),
    4:  (140, 6,  7),
    5:  (170, 7,  7),
    6:  (200, 8,  8),
    7:  (230, 9,  8),
    8:  (260, 10, 9),
    9:  (290, 11, 9),
    10: (320, 12, 10),
    11: (350, 13, 10),
    12: (380, 14, 11),
}
MAX_ROUNDS = 12


def get_level(round_num: int) -> tuple:
    return ROUND_LEVELS.get(round_num, ROUND_LEVELS[MAX_ROUNDS])


class GameSession:
    def __init__(self, chat_id, theme, grid, words, placed, round_num, img_bytes,
                 is_hard: bool = False):
        self.chat_id      = chat_id
        self.theme        = theme
        self.grid         = grid
        self.words        = words
        self.placed       = placed
        self.round_num    = round_num
        self.img_bytes    = img_bytes
        self.is_hard      = is_hard          # True for /newhard sessions
        self.found_words  : list           = []
        self.finders      : Dict[str,dict] = {}
        self.p_combos     : Dict[int,int]  = {}
        self.p_scores     : Dict[int,int]  = {}
        self.p_names      : Dict[int,str]  = {}
        self.p_found_cnt  : Dict[int,int]  = {}
        self.active       = True
        self.started_at   = time.time()
        self.grid_msg_id  : Optional[int]  = None
        self.msg_ids      : list           = []
        self.hint_msg_id  : Optional[int]  = None
        self._task        : Optional[asyncio.Task] = None

        if is_hard:
            self.duration  = random.randint(HARD_DURATION_MIN, HARD_DURATION_MAX)
            self.grid_size = HARD_GRID_SIZE
        else:
            duration, n_words, grid_size = get_level(round_num)
            self.duration  = duration
            self.grid_size = grid_size

    def valid_guess(self, word: str) -> bool:
        return word in self.words and word not in self.found_words

    def already_found(self, word: str) -> bool:
        return word in self.found_words

    def register(self, word: str, uid: int, name: str) -> int:
        combo = min(self.p_combos.get(uid, 0) + 1, 5)
        self.p_combos[uid] = combo
        is_first = len(self.found_words) == 0
        if self.is_hard:
            # Hard mode: 1st word = 25 pts, scales down to 10 pts by last word.
            # e.g. 15 words: 25, 24, 23, 21, 20, 19, 17, 16, 15, 13, 12, 11, 10, 10, 10
            n_total = max(len(self.words), 1)
            pos     = len(self.found_words)   # 0-indexed, before appending
            if n_total > 1:
                pts = round(HARD_FIRST_PTS - (HARD_FIRST_PTS - HARD_POINTS_PER_WORD)
                            * pos / (n_total - 1))
            else:
                pts = HARD_FIRST_PTS
            pts = max(HARD_POINTS_PER_WORD, min(HARD_FIRST_PTS, pts))
        else:
            # Normal mode: base pts scale up by 1 per round
            bonus = self.round_num - 1          # +0 on R1, +1 on R2, +2 on R3 …
            base_first  = FIRST_FIND_PTS + bonus
            base_normal = POINTS_PER_WORD + bonus
            pts = base_first if is_first else base_normal
        self.found_words.append(word)
        self.finders[word] = {"user_id": uid, "name": name, "pts": pts, "combo": combo}
        self.p_scores[uid]    = self.p_scores.get(uid, 0) + pts
        self.p_names[uid]     = name
        self.p_found_cnt[uid] = self.p_found_cnt.get(uid, 0) + 1
        return pts

    def reset_combo(self, uid: int):
        self.p_combos[uid] = 0

    def complete(self) -> bool:
        return len(self.found_words) >= len(self.words)

    def time_left(self) -> int:
        return max(0, self.duration - int(time.time() - self.started_at))

    def summary(self) -> list:
        return sorted(
            [{"user_id": uid, "name": self.p_names[uid],
              "score": self.p_scores[uid],
              "words": self.p_found_cnt.get(uid, 0)}
             for uid in self.p_scores],
            key=lambda x: -x["score"]
        )

    def get_hint(self, word: str) -> str:
        if len(word) <= 2:
            return word
        middle = " _ " * (len(word) - 2)
        return f"{word[0]}{middle}{word[-1]}"


class SessionManager:
    def __init__(self):
        self._sess  : Dict[int, GameSession] = {}
        self._cools : Dict[int, float]       = {}

    def get(self, cid: int) -> Optional[GameSession]:
        return self._sess.get(cid)

    def put(self, s: GameSession):
        self._sess[s.chat_id] = s

    def remove(self, cid: int):
        s = self._sess.pop(cid, None)
        if s and s._task:
            s._task.cancel()

    def active(self, cid: int) -> bool:
        s = self._sess.get(cid)
        return bool(s and s.active)

    def cooldown(self, cid: int) -> bool:
        return time.time() < self._cools.get(cid, 0)

    def cooldown_left(self, cid: int) -> int:
        return max(0, int(self._cools.get(cid, 0) - time.time()))

    def set_cooldown(self, cid: int, secs: int = 15):
        self._cools[cid] = time.time() + secs


sessions = SessionManager()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HARD MODE ROTATION
#  Separate per-chat history for /newhard so
#  themes and word pools don't repeat until
#  all are exhausted.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_hard_theme_history : Dict[int, collections.deque] = {}
_hard_word_history  : Dict[int, set]               = {}


def pick_hard_theme(chat_id: int, theme_list: list) -> str:
    """Pick a hard-mode theme, avoiding repeats until all used."""
    hist = _hard_theme_history.setdefault(
        chat_id, collections.deque(maxlen=len(theme_list) - 1)
    )
    available = [t for t in theme_list if t not in hist]
    if not available:
        hist.clear()
        available = list(theme_list)
    chosen = random.choice(available)
    hist.append(chosen)
    return chosen


def pick_hard_words(chat_id: int, theme_key: str, all_words: list,
                    n_min: int, n_max: int) -> list:
    """
    Pick n_min–n_max words from this theme for hard mode.
    Words already used (across all hard sessions for this chat) are
    avoided until the full pool is exhausted, then the used set resets.
    Only words with 3+ letters are eligible.
    """
    eligible = [w for w in all_words if len(w) >= 3]
    used = _hard_word_history.setdefault(chat_id, set())
    available = [w for w in eligible if w not in used]
    n = random.randint(n_min, n_max)
    if len(available) < n:
        # Pool exhausted — reset and use full list
        used.clear()
        available = list(eligible)
    chosen = random.sample(available, min(n, len(available)))
    used.update(chosen)
    return chosen
#  Uses all 20 themes before repeating any.
#  Per-chat history stored in a deque of size 19.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_theme_history: Dict[int, collections.deque] = {}
_THEME_COOLOFF = 39   # keep last 39 so all 40 themes play before repeat


def pick_random_theme(chat_id: int, theme_list: list) -> str:
    """Pick a random theme avoiding recently used ones for this chat."""
    hist = _theme_history.setdefault(chat_id, collections.deque(maxlen=_THEME_COOLOFF))
    available = [t for t in theme_list if t not in hist]
    if not available:
        available = list(theme_list)   # all used — reset
    chosen = random.choice(available)
    hist.append(chosen)
    return chosen


def pick_next_round_theme(chat_id: int, current_theme: str, theme_list: list) -> str:
    """Pick a theme for the next round — always different from current round."""
    hist = _theme_history.setdefault(chat_id, collections.deque(maxlen=_THEME_COOLOFF))
    available = [t for t in theme_list if t not in hist and t != current_theme]
    if not available:
        available = [t for t in theme_list if t != current_theme]
    if not available:
        available = list(theme_list)
    chosen = random.choice(available)
    hist.append(chosen)
    return chosen


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IDLE NUDGE TRACKER
#  Records last game activity per group so the
#  nudge job knows when a group has gone quiet.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_last_activity: Dict[int, float] = {}


def touch_activity(chat_id: int) -> None:
    """Call when a game starts or ends in a group."""
    _last_activity[chat_id] = time.time()


def idle_seconds(chat_id: int) -> float:
    """Seconds since last game activity. Returns inf if group never played."""
    ts = _last_activity.get(chat_id)
    return float("inf") if ts is None else time.time() - ts
