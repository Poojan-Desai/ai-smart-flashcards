# Minimal SM-2 inspired scheduling
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class CardState:
    interval: int = 1
    repetition: int = 0
    ease: float = 2.5  # SM-2 default

def schedule(score: int, state: CardState):
    # score: 1 (hard) .. 5 (easy)
    if score < 3:
        state.repetition = 0
        state.interval = 1
    else:
        if state.repetition == 0:
            state.interval = 1
        elif state.repetition == 1:
            state.interval = 6
        else:
            state.interval = int(round(state.interval * state.ease))
        state.repetition += 1
        state.ease += (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02))
        if state.ease < 1.3:
            state.ease = 1.3
    next_review = datetime.utcnow() + timedelta(days=state.interval)
    return state, next_review
