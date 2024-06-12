from ..extraction.somef_extraction.somef_extractor import download_repo_metadata
from ..metadata.api.zenodo_api import *
from ..modelling.git_bidirectionality import is_it_bidir as git_is_it_bidir

logger = logging.getLogger("Zenodo_Bidirectionality")


def is_it_bidir(paper_obj, zenodo_url: str, output_dir):
    """
    Checks if the paper relationship with the repository is bidirectional.

    :param paper_obj: An instance of the Paper class representing the paper.
    :param zenodo_url: A string representing url valid in zenodo

    :returns:

    """
    try:
        record_text, url = get_record(zenodo_url)
        if not record_text:
            return None
        result = []

        if doi_in_zenodo(paper_obj, record_text):
            result.append({
                "location": "ZENODO",
                "id_type": "DOI",
                "identifier": paper_obj.doi,
                "source": "RSEF"
            })

        if arxiv_in_zenodo(paper_obj, record_text):
            result.append({
                "location": "ZENODO",
                "id_type": "ARXIV",
                "identifier": paper_obj.arxiv,
                "source": "RSEF"
            })

        if title_in_zenodo(paper_obj, record_text):
            result.append({
                "location": "ZENODO",
                "id_type": "TITLE",
                "identifier": paper_obj.title,
                "source": "RSEF"
            })

        github_repo = set(get_github_from_zenodo(record_text))
        bidir_git_zenodo = _github_zenodo_bidirectional(paper_obj, list(github_repo), output_dir)
        if bidir_git_zenodo:
            result.append({
                "github_from_zenodo":  bidir_git_zenodo,

            })
        return result


    except Exception as e:
        logger.error(f"Error while trying to get the record from Zenodo: {e}")


def arxiv_in_zenodo(paper_obj, zen_rec_text):
    if arxiv := paper_obj.arxiv:
        return arxiv in zen_rec_text
    return False


def doi_in_zenodo(paper_obj, zen_rec_text):
    if doi := paper_obj.doi:
        if not ("zenodo" in doi):
            return doi in zen_rec_text
    return False


def title_in_zenodo(paper_obj, zen_rec_text):
    if title := paper_obj.title:
        return title.lower() in zen_rec_text.lower()
    return False

def _github_zenodo_bidirectional(paper_obj, list_githubs, output_dir):

    if not list_githubs:
        return None
    bidir_git_zenodo = []
    for github in list_githubs:
        # Download repository from SOMEF
        repo_file = download_repo_metadata(github, output_dir)

        if not repo_file:
            logging.error(f"Issue while downloading the repository for {paper_obj.to_dict}")
            continue
        # assessment of bidirectionality

        is_bidir = git_is_it_bidir(paper_obj, repo_file)
        if is_bidir:
            entry = {
                "url": github,
                "zenodo_git": is_bidir
            }
            bidir_git_zenodo.append(entry)
            print(entry)
    return bidir_git_zenodo
