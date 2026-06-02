from __future__ import annotations

import json
import random
from pathlib import Path

import FalangoEssentialSystems as FES

class PlayerCPUAdaptive(FES.Player):
    def __init__(self, isInverted: bool, history_path: Path | None = None) -> None:
        super().__init__(isInverted)
        self.history_path = history_path or (Path(__file__).resolve().parent / "data" / "ai_history.json")
        self.history = self._load_history()
        self.last_player_finger = self.history.get("last_player_finger", "")

    def _default_history(self) -> dict:
        return {
            "totals": {finger: 0 for finger in FES.fingerNames},
            "transitions": {finger: {f: 0 for f in FES.fingerNames} for finger in FES.fingerNames},
            "games": {"total": 0, "player_wins": 0, "cpu_wins": 0},
            "last_player_finger": "",
        }

    def _load_history(self) -> dict:
        if not self.history_path.exists(): return self._default_history()
        try:
            with self.history_path.open("r", encoding="utf-8") as handle: data = json.load(handle)
            if "totals" not in data or "transitions" not in data: return self._default_history()
            return data
        except (OSError, json.JSONDecodeError): return self._default_history()

    def _save_history(self) -> None:
        self.history["last_player_finger"] = self.last_player_finger
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as handle: json.dump(self.history, handle, indent=2)

    def record_player_choice(self, finger: str) -> None:
        if finger not in FES.fingerNames: return
        self.history["totals"][finger] += 1
        if self.last_player_finger: self.history["transitions"][self.last_player_finger][finger] += 1
        self.last_player_finger = finger
        self._save_history()

    def record_game_result(self, winner_id: int) -> None:
        self.history["games"]["total"] += 1
        if winner_id == 1: self.history["games"]["player_wins"] += 1
        elif winner_id == 2: self.history["games"]["cpu_wins"] += 1
        self._save_history()

    def _weighted_choice(self, weights: dict[str, int]) -> str:
        total = sum(weights.values())
        if total <= 0: return random.choice(FES.fingerNames)
        pick = random.randint(1, total)
        running = 0
        for finger, weight in weights.items():
            running += weight
            if running >= pick: return finger
        return random.choice(FES.fingerNames)

    def chooseFinger(self) -> None:
        totals = self.history.get("totals", {})
        transitions = self.history.get("transitions", {})
        weights: dict[str, int] = {}
        for finger in FES.fingerNames:
            base = totals.get(finger, 0) + 1
            if self.last_player_finger: base += transitions.get(self.last_player_finger, {}).get(finger, 0) * 2
            weights[finger] = base
        self.chosenFinger = self._weighted_choice(weights)
    
    def chooseRandomFingerFromList(self, list: list[str]): return random.choice(list)
