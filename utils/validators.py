def is_valid_text(text: str, min_len: int = 1) -> bool:
    return isinstance(text, str) and len(text.strip()) >= min_len