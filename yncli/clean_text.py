import re

# Comprehensive regex to strip emoji pictographs, dingbats, and surrogate pairs
EMOJI_PATTERN = re.compile(
    "["
    "\U00010000-\U0010ffff"
    "\U00002600-\U000027BF"
    "\U00002300-\U000023FF"
    "\U00002B50-\U00002B55"
    "\U0000200D"
    "\U0000FE0F"
    "\U0000FE0E"
    "]+",
    flags=re.UNICODE
)


def fix_double_encoded_utf8(text: str) -> str:
    """
    Attempts to repair UTF-8 bytes that were misdecoded as Latin-1 / Windows-1252.
    For example: 'â”œ' -> '├', 'âžž' -> '->', 'â€"' -> '-'
    """
    if not text:
        return ""
    
    # Common direct replacements
    text = (
        text
        .replace("âžž", "->")
        .replace("â†’", "->")
        .replace("â€\"", "-")
        .replace("â€'", "-")
        .replace("â”œâ”€â”€â”€", "|--")
        .replace("â”œâ”€â”€", "|--")
        .replace("â”œ", "|-")
        .replace("â””â”€â”€â”€", "\\--")
        .replace("â””â”€â”€", "\\--")
        .replace("â””", "\\-")
        .replace("â”‚", "|")
        .replace("â”€", "-")
        .replace("â‰ˆ", "~")
        .replace("âˆš", "sqrt")
        .replace("ðŸ‘¤", "")
        .replace("ð", "")
        .replace("â", "-")
    )
    
    try:
        # Check if text contains typical latin1 mojibake markers
        if "Ã" in text or "Â" in text:
            repaired = text.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
            if repaired:
                text = repaired
    except Exception:
        pass

    return text


def clean_text_for_terminal(text: str) -> str:
    if not text:
        return ""
    # Strip emojis
    cleaned = EMOJI_PATTERN.sub("", text)
    # Fix double-encoded UTF-8
    cleaned = fix_double_encoded_utf8(cleaned)
    # Purge any remaining corrupted artifacts
    for bad in ["Ã°ÂÂÂ", "Ã°", "Ã", "Â", "Ÿ‘‹", "Ÿ˜Š", "Ÿ"]:
        cleaned = cleaned.replace(bad, "")
    return cleaned
