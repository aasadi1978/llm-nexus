import re


def clean_up(text: str) -> str:
    """
    Clean up the text by removing extra whitespace and newlines.

    Returns:
        str: The cleaned text with extra whitespace and newlines removed.
    """
    try:
        cleaned_text = text.strip().replace('\n', ' ')
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        return cleaned_text
    
    except Exception as e:
        print(f"Error cleaning text: {e}")
        return text
