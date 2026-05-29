import asyncio
import collections
import random
import time
import logging
from typing import Dict, Optional
from config import POINTS_PER_WORD, FIRST_FIND_PTS, COMBO_MULTIPLIERS

log = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GAME CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Normal mode
NORMAL_GRID_SIZE  = 10
NORMAL_N_WORDS_MIN = 10
NORMAL_N_WORDS_MAX = 15
NORMAL_DURATION   = 180   # 3 minutes

# Hard mode
HARD_GRID_SIZE    = 10
HARD_N_WORDS_MIN  = 10
HARD_N_WORDS_MAX  = 15
HARD_DURATION_MIN = 400
HARD_DURATION_MAX = 500
HARD_POINTS_PER_WORD = 10
HARD_FIRST_PTS       = 25

# Kept for any legacy imports (not used in logic anymore)
MAX_ROUNDS = 1


class GameSession:
    def __init__(self, chat_id, theme, grid, words, placed, img_bytes,
                 is_hard: bool = False):
        self.chat_id     = chat_id
        self.theme       = theme
        self.grid        = grid
        self.words       = words
        self.placed      = placed
        self.img_bytes   = img_bytes
        self.is_hard     = is_hard
        self.round_num   = 1       # always 1 — kept so caption helpers don't break
        self.grid_size   = HARD_GRID_SIZE if is_hard else NORMAL_GRID_SIZE
        self.duration    = (
            random.randint(HARD_DURATION_MIN, HARD_DURATION_MAX)
            if is_hard else NORMAL_DURATION
        )

        self.found_words : list           = []
        self.finders     : Dict[str,dict] = {}
        self.p_combos    : Dict[int,int]  = {}
        self.p_scores    : Dict[int,int]  = {}
        self.p_names     : Dict[int,str]  = {}
        self.p_usernames : Dict[int,str]  = {}
        self.p_found_cnt : Dict[int,int]  = {}
        self.active      = True
        self.started_at  = time.time()
        self.grid_msg_id : Optional[int]  = None
        self.msg_ids     : list           = []
        self.hint_msg_id : Optional[int]  = None
        self._task       : Optional[asyncio.Task] = None

    def valid_guess(self, word: str) -> bool:
        return word in self.words and word not in self.found_words

    def already_found(self, word: str) -> bool:
        return word in self.found_words

    def register(self, word: str, uid: int, name: str, username: str = None) -> int:
        combo    = min(self.p_combos.get(uid, 0) + 1, 5)
        self.p_combos[uid] = combo
        is_first = len(self.found_words) == 0

        if self.is_hard:
            n_total = max(len(self.words), 1)
            pos     = len(self.found_words)
            if n_total > 1:
                pts = round(HARD_FIRST_PTS - (HARD_FIRST_PTS - HARD_POINTS_PER_WORD)
                            * pos / (n_total - 1))
            else:
                pts = HARD_FIRST_PTS
            pts = max(HARD_POINTS_PER_WORD, min(HARD_FIRST_PTS, pts))
        else:
            pts = FIRST_FIND_PTS if is_first else POINTS_PER_WORD

        self.found_words.append(word)
        self.finders[word] = {"user_id": uid, "name": name, "pts": pts, "combo": combo}
        self.p_scores[uid]    = self.p_scores.get(uid, 0) + pts
        self.p_names[uid]     = name
        if username:
            self.p_usernames[uid] = username
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
              "username": self.p_usernames.get(uid),
              "score": self.p_scores[uid],
              "words": self.p_found_cnt.get(uid, 0)}
             for uid in self.p_scores],
            key=lambda x: -x["score"]
        )

    def get_hint(self, word: str) -> str:
        if len(word) <= 2:
            return word[0] + " _" * (len(word) - 1)
        if len(word) == 3:
            return word[0] + " _ " + word[-1]
        return word[0] + " _" * (len(word) - 2) + " " + word[-1]


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
#  THEME ROTATION  (per-chat, no repeats until all used)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_theme_history: Dict[int, collections.deque] = {}

def pick_random_theme(chat_id: int, theme_list: list) -> str:
    """Pick a random theme avoiding recently used ones for this chat."""
    n    = len(theme_list)
    hist = _theme_history.setdefault(chat_id, collections.deque(maxlen=n - 1))
    available = [t for t in theme_list if t not in hist]
    if not available:
        hist.clear()
        available = list(theme_list)
    chosen = random.choice(available)
    hist.append(chosen)
    return chosen


# Hard mode keeps its own separate history so normal and hard don't share state
_hard_theme_history: Dict[int, collections.deque] = {}
_hard_word_history : Dict[int, set]               = {}

def pick_hard_theme(chat_id: int, theme_list: list) -> str:
    n    = len(theme_list)
    hist = _hard_theme_history.setdefault(chat_id, collections.deque(maxlen=n - 1))
    available = [t for t in theme_list if t not in hist]
    if not available:
        hist.clear()
        available = list(theme_list)
    chosen = random.choice(available)
    hist.append(chosen)
    return chosen

def pick_hard_words(chat_id: int, theme_key: str, all_words: list,
                    n_min: int, n_max: int) -> list:
    """Pick n_min–n_max words; prefer words not recently used in this chat."""
    eligible  = [w for w in all_words if len(w) >= 3]
    used      = _hard_word_history.setdefault(chat_id, set())
    available = [w for w in eligible if w not in used]
    n         = random.randint(n_min, n_max)
    if len(available) < n:
        used.clear()
        available = list(eligible)
    chosen = random.sample(available, min(n, len(available)))
    used.update(chosen)
    return chosen


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IDLE NUDGE TRACKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_last_activity: Dict[int, float] = {}

def touch_activity(chat_id: int) -> None:
    _last_activity[chat_id] = time.time()

def idle_seconds(chat_id: int) -> float:
    ts = _last_activity.get(chat_id)
    return float("inf") if ts is None else time.time() - ts


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEGACY STUBS  (imported by some modules — kept to avoid ImportError)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_level(round_num: int) -> tuple:
    return (NORMAL_DURATION, NORMAL_N_WORDS_MAX, NORMAL_GRID_SIZE)

def pick_next_round_theme(chat_id: int, current_theme: str, theme_list: list) -> str:
    return pick_random_theme(chat_id, theme_list)
