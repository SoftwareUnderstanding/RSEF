from datetime import datetime
import json
import logging
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

log = logging.getLogger(__name__)

def download_pdf_link(pdf_link, pdf_filepath):
    """Attempts to download a PDF from a direct link."""
    try:
        response = requests.get(pdf_link, timeout=10, stream=True)
        response.raise_for_status()

        with open(pdf_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)

        log.info('PDF downloaded successfully from direct link')
        return pdf_filepath

    except requests.exceptions.RequestException as e:
        log.error(f"Error downloading PDF from direct link: {pdf_link}, {e}")
        return None

def doi_to_downloaded_pdf(url, doi, pdf_link, output_dir):
    '''
    @Param url: unpaywall url, we will get a json where we can find where to freely access the paper
    @Param doi: DOI for the paper
    @Param pdf_link: Direct PDF link (if available)
    @Param output_dir: output directory where the PDF will be saved
    '''
    # Input verification
    if not os.path.exists(output_dir):
        return None
    if not (file_name := _doi_to_pdf_name(doi)) and not pdf_link:
        return None

    pdf_filepath = os.path.join(output_dir, file_name or f"{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
    if pdf_link: # If a direct PDF link is available, try downloading it first
        if downloaded_pdf := download_pdf_link(pdf_link, pdf_filepath):
            return downloaded_pdf
    
    # Get the Unpaywall JSON response
    if not (upaywall := _unpaywall_response_to_json(url)):
        log.debug(f"Failed to download the PDF for {str(doi)} with {str(url)}")
        return None
    
    # See if there is a best location
    if bst_oa_loc := safe_dic(upaywall, "best_oa_location"):
        response = _try_all_location_urls(bst_oa_loc)
        pdf = response_to_pdf_binary(response)
        if not pdf:
            pdf = try_other_locations(upaywall)
    else:
        pdf = try_other_locations(upaywall)
    
    # Check if no PDF has been found
    if not pdf:
        log.debug(f"Failed to download the PDF for {str(doi)} with {str(url)}")
        return None
    
    # Save the downloaded PDF
    try:
        with open(pdf_filepath, 'wb') as f:
            f.write(pdf)
            log.info('PDF written successfully from Unpaywall')
        return pdf_filepath
    except Exception as e:
        log.error(f"Exception! Failed to save the PDF for {str(doi)} with {str(url)}, {str(e)}")
        return None


def try_other_locations(jayson: json):
    """
    Used if the best_oa fails will attempt to get the first OA
    @Param Jayson: unpaywall response json
    :returns:
    list of urls if response status code is 200
    """
    try:
        if not (locations := safe_dic(jayson, "oa_locations")):
            return None

        for location in locations:
            response = _try_all_location_urls(location)
            if pdf_binary := response_to_pdf_binary(response):
                return pdf_binary
        return None
    except Exception as e:
        error_msg = f"Backup Error: An error occurred - {str(e)}"
        log.error(error_msg)
        return None


def _try_all_location_urls(location: dict):
    '''
    @Param location: receives location from unpaywall url
    :returns:
    response if status code == 200
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    if url := safe_dic(location,"url_for_pdf"):
        response = requests.get(url, headers= headers)
        if response.status_code == 200:
            return response
    if url := safe_dic(location, "url"):
        response = requests.get(url, headers= headers)
        if response.status_code == 200:
            return response
    return None


def response_to_pdf_binary(response: requests):
    if not response:
        return None
    if response.status_code != 200:
        return None
    type = detect_content_type(response)
    if type == "Unknown":
        return None
    elif type == "PDF":
        return response.content
    elif type == "HTML":
        pdf_binary = _html_resp_to_pdf_binary(response, response.url)
        if pdf_binary:
            return pdf_binary.content


def _html_resp_to_pdf_binary(response, html_url):
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        if pdf := _html_resp_to_binary_from_form(soup_obj=soup, html_url=html_url):
            return pdf
        if pdf := _html_resp_to_pdf_binary_from_direct_link(soup_obj=soup, html_url=html_url):
            return pdf

        return None
    except:
        return None


def _html_resp_to_binary_from_form(soup_obj, html_url):
    # TODO
    return


def _html_resp_to_pdf_binary_from_direct_link(soup_obj, html_url):
    """
    @Param soup_obj: soup object from _html_resp_to_pdf_binary
    ----------
    :returns:
    PDF binary

    Takes soup object and finds a link to a pdf, returns a request to that url
    """
    try:
        for link in soup_obj.find_all('a'):
            # Check if the link contains '.pdf' in the href attribute
            if link.get('href') and '.pdf' in link.get('href'):
                pdf_link = link.get('href')
                # Make sure the link is an absolute URL
                if not pdf_link.startswith('http'):
                    pdf_link = urljoin(html_url, pdf_link)
                try:
                    pdf = requests.get(pdf_link)
                    if detect_content_type(pdf) == "PDF":
                        return pdf
                except requests.RequestException:
                    continue


        # If no PDF link is found, return None
        return None

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None


def _doi_to_pdf_name(doi: str):
    """
    @Param doi: string of doi ID
    ----------
    :returns:
    String that works within UNIX/macOS filesystems. Windows(NTFS) not tested

    Takes a doi and returns a file_name
    replaces / with %
        and  . with !
    """
    if not doi:
        return None
    else:
        # characters within doi that is allowed -._;()/
        name = doi.replace('http://doi.org/', '').replace('https://doi.org/', '') \
                   .replace('/', '%').replace('.', '!') + '.pdf'
        return name


def _unpaywall_response_to_json(url: str):
    """
    Receives unpaywall url
    :returns:
    JSON response from unpaywall containing a best location and other locations
    """
    try:
        r = requests.get(url)
        idk = str(r.content)
        idk = idk[2:-1]
        idk = idk.replace('\\', '')
        json_idk = json.loads(idk)
        return json_idk
    except Exception as e:
        log.error(f"Failed to download the PDF: Issue while trying to get the unpaywall response {str(e)}")
        return None


def detect_content_type(response):
    """
    Receives response and determines if it is a PDF or HTML
    :returns:
    String HTML, PDF or unknown depending on the type of response
    """
    try:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            return "HTML"
        elif "application/pdf" in content_type:
            return "PDF"
        else:
            return "Unknown"

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return "Error"
    except Exception as e:
        log.error(f"Unknown Issue when determining the content type {str(e)}")
        return "Error"


def safe_dic(dic, key):
    try:
        return dic[key]
    except Exception as e:
        log.error(f"Issue when opening the Dictionary {str(e)}")
        return None