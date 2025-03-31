import os.path
import subprocess
import logging
from ..extraction.pdf_extraction_tika import get_possible_title as use_tika_title

log = logging.getLogger(__name__)

def extract_pdf_title(pdf_path):

    if (title:= use_pdf_title(pdf_path)):
        print("This is the extracted title " + title)
        return title
    else:
        log.warning("pdf_title was not able to extract the title will fallback to Tika")
        title = use_tika_title(pdf_path)
    print("This is the extracted title " + title)
    return title



def use_pdf_title(pdf):
    """
    @Param pdf: Name of the pdf file for the title to be found
    :returns
    Title as string if found. Else None
    """
    pdf = os.path.abspath(pdf)
    if not os.path.exists(pdf):
        log.info(f"PDF file not found at path: {pdf}")
        return None
    # Runs the pdftitle module as a subprocess and communicate with it
    try:
        command = ['pdftitle', '-p', pdf]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        stdout, _ = process.communicate(input=pdf)
        # Extracts and returns the pdf title from stdout
        pdf_title = stdout.strip()
        if pdf_title == "":
            log.debug("Issue extracting Pdf title")
            return None
        return pdf_title
    except Exception as e:
        log.error(str(e), exc_info=True)
        pass
        return None


