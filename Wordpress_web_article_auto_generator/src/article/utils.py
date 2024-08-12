import re

from bs4 import BeautifulSoup


def extract_title_from_content(content: str) -> tuple[str, str]:
    """Extracts title post content"""
    soup = BeautifulSoup(content, "html.parser")
    title = soup.find("h1").text
    content = content.replace(title, "")
    return title, content


def is_html(text: str) -> bool:
    """Checks if text is HTML"""
    soup = BeautifulSoup(text, "html.parser")
    return bool(soup.find())


def clean_text(text):
    """Removes useless data to make gpt-model easier to use"""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    # Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)
    # Remove phone numbers (various formats)
    text = re.sub(r"\b\d{10}\b", "", text)  # Simple 10 digit numbers
    text = re.sub(
        r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "", text
    )  # (123) 456-7890, 123-456-7890, 123.456.7890, 123 456 7890
    text = re.sub(r"\d{1,2}[-.\s]?\d{1,2}[-.\s]?\d{2,4}", "", text)  # International numbers with country code
    # Remove special characters and numbers
    text = re.sub(r"[^A-Za-zА-Яа-я\s]", "", text)
    # Remove HTML entities
    text = re.sub(r"&[a-z]+;", "", text)
    # Remove hashtags and mentions
    text = re.sub(r"#\S+", "", text)
    text = re.sub(r"@\S+", "", text)
    # Remove unnecessary punctuation
    text = re.sub(r"[“”\"\'•]", "", text)
    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    # Remove extra newlines and tabs
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\t+", " ", text)
    # Remove repeated characters (e.g., "sooooo good")
    text = re.sub(r"(.)\1{2,}", r"\1", text)
    # Remove special sequences (e.g., "Lorem Ipsum")
    text = re.sub(r"lorem ipsum", "", text, flags=re.IGNORECASE)
    # Convert text to lower case (optional, depending on the use case)
    text = text.lower()
    return text