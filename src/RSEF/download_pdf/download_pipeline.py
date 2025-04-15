import logging
import os
# TODO fix imports
from .unpaywall_pdf_url_extractor import create_unpaywall_url_from_string as paywall_url
from .arxiv_downloader import download_pdf as download_arxiv_pdf
from .unpaywall_pdf_downloader import doi_to_downloaded_pdf

log = logging.getLogger(__name__)

def pdf_download_pipeline(id, output_directory, pdf_link):
    """
    Verifies whether the input is an arXiv DOI or another DOI.
    If it's an arXiv DOI, it uses arXiv to download the paper; otherwise, it uses Unpaywall.
    :param: id (str): Identifier for the paper, which can be an arXiv DOI or another type of DOI.
    :param: output_dir (str): The directory where the downloaded paper will be saved.
    :param: pdf_link (str): The URL of the PDF file.
    ------
    :returns: The path to the downloaded PDF.
    """
    try:
        # Creates Directory if it does not exist
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        # creates a folder within the wanted output directory
        pdf_output_directory = os.path.join(output_directory, "PDFs")
        if not os.path.exists(pdf_output_directory):
            # Creates Directory if it does not exist
            os.mkdir(pdf_output_directory)
    except Exception as e:
        log.error(f"Error while trying to create the directory Err @ PDF download {str(e)}")

    log.debug(f"Attempting to download pdf for {str(id) if id else str(pdf_link)}")
    if (file_path := download_arxiv_pdf(id, pdf_output_directory) and id):
        return file_path
    else:
        url = pdf_link or paywall_url(id)
        if not url:
            log.debug("We are only able to download pdfs via arxiv or doi for now, sorry")
            return None
        file_path = doi_to_downloaded_pdf(url, id, pdf_link, pdf_output_directory)
    if file_path:
        log.info("Success downloading the pdf file")
        return file_path
    else:
        return None
