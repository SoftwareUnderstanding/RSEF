import json
import logging
import pandas
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def doi_to_downloaded_pdf(url, doi, output_dir):
    '''
    @Param url: unpaywall url, we will get a json where we can find where to freely access the paper
    @Param doi: DOI for the paper
    @Param output_dir: output directory to where the pdf will be saved
    '''
    # Input verification
    if not os.path.exists(output_dir):
        return None
    if not (file_name := _doi_to_pdf_name(doi)):
        return None
    # Get the unpaywall json
    if not (upaywll := _unpaywall_response_to_json(url)):
        return None
    # See if there is a best location
    if bst_oa_loc := safe_dic(upaywll, "best_oa_location"):
        response = _try_all_location_urls(bst_oa_loc)
        pdf = response_to_pdf_binary(response)
        # if best location has failed
        if not pdf:
            pdf = try_other_locations(upaywll)
    # There is no best location
    else:
        pdf = try_other_locations(upaywll)
    # Check if no pdf has been found
    if not pdf:
        logging.error(f"Failed to download the pdf for {str(doi)} with {str(url)}")
        print("-------------------------------")
        return None
    # if success
    try:
        pdf_filepath = os.path.join(output_dir, file_name)
        with open(pdf_filepath, 'wb') as f:  # here download the pdf
            f.write(pdf)
            print("PDF was downloaded successfully")
            print("-------------------------------")
            logging.info('written pdf successfully')
        return pdf_filepath
    except Exception as e:
        logging.error(f"Exception! Failed to download the pdf for {str(doi)} with {str(url)}, {str(e)}")
        print("-------------------------------")
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
        logging.error(error_msg)
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
        logging.error(f"Issue while trying to get the unpaywall response {str(e)}")
        logging.error(f"Failed to download the pdf")
        print("-------------------------------")
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
        logging.error(f"Unknown Issue when determining the content type {str(e)}")
        return "Error"


def safe_dic(dic, key):
    try:
        return dic[key]
    except Exception as e:
        logging.error(f"Issue when opening the Dictionary {str(e)}")
        return None