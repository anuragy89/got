import asyncio
import time
import logging
from typing import Dict, Optional
from config import ROUND_DURATION, POINTS_PER_LETTER, FIRST_FINDER_BONUS, COMBO_MULTIPLIERS

log = logging.getLogger(__name__)


class GameSession:
    def __init__(self, chat_id, theme, grid, words, placed, round_num, img_bytes):
        self.chat_id     = chat_id
        self.theme       = theme
        self.grid        = grid
        self.words       = words          # list[str]
        self.placed      = placed         # list[{word, cells}]
        self.round_num   = round_num
        self.img_bytes   = img_bytes
        self.found_words : list          = []
        self.finders     : Dict[str,dict]= {}   # word → {user_id, name, pts, combo}
        self.p_combos    : Dict[int,int] = {}
        self.p_scores    : Dict[int,int] = {}
        self.p_names     : Dict[int,str] = {}
        self.p_found_cnt : Dict[int,int] = {}
        self.active      = True
        self.started_at  = time.time()
        self.grid_msg_id : Optional[int] = None
        self._task       : Optional[asyncio.Task] = None

    # ── word checking ──
    def valid_guess(self, word: str) -> bool:
        return word in self.words and word not in self.found_words

    def already_found(self, word: str) -> bool:
        return word in self.found_words

    def register(self, word: str, uid: int, name: str) -> int:
        combo = min(self.p_combos.get(uid, 0) + 1, 5)
        self.p_combos[uid] = combo
        mult = COMBO_MULTIPLIERS.get(combo, 1.0)
        pts  = int(len(word) * POINTS_PER_LETTER * mult)
        if not self.found_words:
            pts += FIRST_FINDER_BONUS
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
        return max(0, ROUND_DURATION - int(time.time() - self.started_at))

    def summary(self) -> list:
        return sorted(
            [{"user_id": uid, "name": self.p_names[uid],
              "score": self.p_scores[uid],
              "words": self.p_found_cnt.get(uid, 0)}
             for uid in self.p_scores],
            key=lambda x: -x["score"]
        )


class SessionManager:
    def __init__(self):
        self._sess   : Dict[int, GameSession] = {}
        self._cools  : Dict[int, float]       = {}

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

    def set_cooldown(self, cid: int):
        from config import COOLDOWN_SECONDS
        self._cools[cid] = time.time() + COOLDOWN_SECONDS


sessions = SessionManager()
