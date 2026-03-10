"""Simple in-memory user state for bot flows (awaiting_email, awaiting_feedback)."""

_user_state: dict[int, dict] = {}


def set_state(user_id: int, state: str, **kwargs) -> None:
    _user_state[user_id] = {"state": state, **kwargs}


def get_state(user_id: int) -> dict | None:
    return _user_state.get(user_id)


def pop_state(user_id: int) -> dict | None:
    return _user_state.pop(user_id, None)
