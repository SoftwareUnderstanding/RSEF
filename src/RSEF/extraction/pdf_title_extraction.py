import os.path
import subprocess
import fitz
import logging
from ..extraction.pdf_extraction_tika import get_possible_title as use_tika_title

log = logging.getLogger(__name__)

COMMON_HEADER_WORDS = {"journal", "volume",
                       "issue", "doi", "applied", "received"}
MIN_WORD_COUNT = 3
MIN_TITLE_LENGTH = 10


def extract_pdf_title(pdf_path):
    """
    Extracts the title from a PDF file using different methods.
    """
    if (title := use_pdf_title(pdf_path)):
        log.debug(f"Title extracted using pdftitle: {title}")
        return title
    elif (title := extract_title_pymupdf(pdf_path)):
        log.debug(f"Title extracted using PyMuPDF: {title}")
        return title
    else:
        log.warning(
            "pdf_title was not able to extract the title will fallback to Tika")
        title = use_tika_title(pdf_path)
    log.debug("This is the extracted title " + title)
    return title


def use_pdf_title(pdf):
    """
    @param pdf: Name/path of the PDF file to extract the title from
    @return: Title string if found and valid, else None
    """
    pdf = os.path.abspath(pdf)
    if not os.path.exists(pdf):
        log.info(f"PDF file not found at path: {pdf}")
        return None

    try:
        command = ['pdftitle', '-p', pdf]
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        stdout, _ = process.communicate(input=pdf)
        pdf_title = stdout.strip()

        if not pdf_title:
            log.debug("Issue extracting PDF title")
            return None

        words = pdf_title.lower().split()
        if len(words) < MIN_WORD_COUNT:
            log.debug("PDF title too short to be valid")
            return None
        if len(pdf_title) < MIN_TITLE_LENGTH:
            log.debug("PDF title too short to be valid")
            return None
        if any(word in COMMON_HEADER_WORDS for word in words):
            log.debug("PDF title contains likely metadata junk words")
            return None

        return pdf_title

    except Exception as e:
        log.error(str(e), exc_info=True)
        return None


def extract_title_pymupdf(pdf_path):
    """
    Extracts the title from the first page of a PDF using PyMuPDF,
    joining up to 5 consecutive lines with font size > 12 and sufficient content.
    """
    doc = fitz.open(pdf_path)
    first_page = doc[0]

    FONT_SIZE_THRESHOLD = 12
    MIN_WORD_COUNT = 3
    MIN_CHAR_LENGTH = 10
    MAX_LINES = 5

    best_lines = []
    current_lines = []
    current_font_size = None

    for block in first_page.get_text("dict")["blocks"]:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            line_text = ""
            line_font_sizes = []

            for span in line["spans"]:
                size = span["size"]
                text = span["text"].strip()

                if size <= FONT_SIZE_THRESHOLD or not text:
                    continue

                line_text += text + " "
                line_font_sizes.append(size)

            line_text = line_text.strip()

            if (
                not line_text
                or len(line_text) < MIN_CHAR_LENGTH
                or len(line_text.split()) < MIN_WORD_COUNT
            ):
                continue

            avg_size = sum(line_font_sizes) / len(line_font_sizes)

            if current_font_size is None or abs(current_font_size - avg_size) < 0.1:
                current_lines.append(line_text)
                current_font_size = avg_size
            else:
                if len(current_lines) > len(best_lines) and len(current_lines) <= MAX_LINES:
                    best_lines = current_lines.copy()
                current_lines = [line_text]
                current_font_size = avg_size

        # Handle leftovers at end of block
        if len(current_lines) > len(best_lines) and len(current_lines) <= MAX_LINES:
            best_lines = current_lines.copy()
        current_lines = []
        current_font_size = None

    candidate = " ".join(best_lines)
    if candidate.endswith("."):
        candidate = candidate[:-1]

    return candidate if candidate else None
