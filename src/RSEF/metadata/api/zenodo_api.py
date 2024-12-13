from ...utils.regex import str_to_doiID, GITHUB_REGEX, ZENODO_SINGLE_RECORD_REGEX
import requests
import logging
import re

logger = logging.getLogger("ZenodoAPI")

BASE_URL = "https://zenodo.org/api/records"


def _get_record(rec_id: str) -> (str, str):
    url = f"{BASE_URL}/{rec_id}"
    logger.debug(f"Final URL: `{url}`")
    try:
        return requests.get(url).text, url
    except Exception as e:
        logger.error(f"Error while trying to request Zenodo {e}")
        return "", ""


def get_record(rec_id_or_doi: str):
    logger.debug(f"Fetching Zenodo record metadata for `{rec_id_or_doi}`")
    if not rec_id_or_doi:
        raise ValueError(f"Not a valid DOI: {rec_id_or_doi}")
    if ("doi.org" or "dx.doi.org") in rec_id_or_doi:
        try:
            record_url = get_redirect_url(rec_id_or_doi)
            match = re.search(r"[0-9]+", record_url)
            # fail if no match, it should not happen
            rec_id = match.group(0)
        except (ValueError, RuntimeError):
            logger.error(f"zenodo_get_record: error with url: `{rec_id_or_doi}`. Skipping...")
            return
    else:
        match = re.search(r"[0-9]+", rec_id_or_doi)
        rec_id = match.group(0)

    return _get_record(rec_id)


def get_redirect_url(doi: str) -> str:
    """Given a DOI or DOI URL, resolve it to the final valid Zenodo URL."""
    if doi_clean := str_to_doiID(doi):
        doi_url = f"https://doi.org/{doi_clean}"
    else:
        error_msg = f"Invalid DOI: {doi}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        logger.debug(f"Resolving DOI for `{doi_url}`")
        current_url = doi_url

        while True:
            response = requests.get(current_url, allow_redirects=False)
            logger.debug(f"Response headers: {response.headers}")
            
            # Check for redirection
            if "Location" in response.headers or "location" in response.headers:
                location = response.headers.get("Location") or response.headers.get("location")
                logger.debug(f"Redirecting to: {location}")
                current_url = location

                # If the URL matches a Zenodo pattern, return it immediately
                if re.match(ZENODO_SINGLE_RECORD_REGEX, current_url):
                    logger.debug(f"Found valid Zenodo link: {current_url}")
                    return current_url
            else:
                # No further redirection; return the final URL
                logger.debug(f"No more redirections, returning: {current_url}")
                return current_url
    except requests.exceptions.RequestException as e:
        error_msg = f"An error occurred: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def get_github_from_zenodo(zenodo_response: str) -> list:
    if zenodo_response:
        list_git = re.findall(GITHUB_REGEX, zenodo_response)
        return list_git
    else:
        return []


