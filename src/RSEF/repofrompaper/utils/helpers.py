import re


def clean_final_link(link: str) -> str:
    """Clean the link by removing trailing dots and .git from the end of the link and removing spaces from the link."""
    if not link:
        return link

    # If link ends with a dot remove it
    if link[-1] == '.':
        link = link[:-1]

    # If the link ends with .git remove it
    if link[-4:] == '.git':
        link = link[:-4]

    link = link.replace(' ', '')
    return link


def clean_final_sentence(sentence: str) -> str:
    """Cleans the sentence to allow better inference."""
    # Remove newline characters
    sentence = sentence.replace('\n', ' ')

    # Use regular expression to replace multiple spaces with a single space
    sentence = re.sub(r'\s+', ' ', sentence)

    # Remove leading and trailing spaces
    sentence = sentence.strip()

    # Remove extra spaces in links
    sentence = sentence.replace(". com", ".com").replace(
        "/ ", "/").replace(" /", "/")

    # Replace badly read h�ps with https
    sentence = sentence.replace("h�p", "http")

    # Replace word breaks
    sentence = sentence.replace("- ", "-")

    return sentence
