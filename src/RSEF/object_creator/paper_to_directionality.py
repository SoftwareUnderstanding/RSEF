# TODO fix imports
from ..extraction.somef_extraction.somef_extractor import download_repo_metadata
from ..modelling.git_bidirectionality import is_it_bidir as git_is_it_bidir
from ..modelling.zenodo_bidirectionality import is_it_bidir as zenodo_is_it_bidir
from ..modelling.unidirectionality import is_repo_unidir
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def check_bidir(paper, output_dir):
    return check_paper_directionality(paper, True, output_dir)


def check_unidir(paper, output_dir):
    return check_paper_directionality(paper, False, output_dir)


def _get_identifier(paper):
    """
    Input
    :param paper: PaperObj, will be used to get the identifier
    ----
    Output
    :returns:
    identifier
    """
    if not paper:
        log.error("Paper Object is None")
        return None
    if paper.doi and paper.doi != "0":
        return paper.doi
    elif paper.arxiv:
        return paper.arxiv
    else:
        log.error("Paper Object Has no identifier to use")
        return None


def check_paper_directionality(paper, directionality, output_dir):
    result = {}

    if not (iden := _get_identifier(paper)):
        log.error(
            "check_paper_directionality: No identifier found for this paper")
        return None
    try:
        first_time = True
        if not (pp_urls := paper.implementation_urls):
            log.info(f"This paper {iden}, it does not have any urls")
            return None

        # Check for zenodo directionality
        zenodo_urls = [url.url for url in pp_urls if url.url_type == "zenodo"]
        _zenodo_check_directionality(
            paper, zenodo_urls, directionality, iden, first_time, result, output_dir)

        # Check for git urls
        git_urls = [url.url for url in pp_urls if url.url_type == "git"]
        _git_check_directionality(paper=paper, git_urls=git_urls, directionality=directionality,
                                  iden=iden, first_time=first_time, output_dir=output_dir, result=result)

        if len(result.keys()) > 0:
            bidir_urls = [entry for entry in result[iden]]
            for bidir_url_obj in bidir_urls:
                url_type = "git" if "git" in bidir_url_obj['url'] else "zenodo"
                source_para = [x['location']
                               for x in bidir_url_obj['bidirectional']]
                paper.add_implementation_link(
                    bidir_url_obj['url'], url_type, source_paragraphs=source_para, extraction_method='bidir')

        return paper

    except Exception as e:
        log.error(f"Issue while check the paper's directionality: {e}")
        return None


def _zenodo_check_directionality(paper, zenodo_urls, directionality, iden, first_time, result, output_dir):
    is_bidir = None

    for url in zenodo_urls:
        if directionality:
            is_bidir = zenodo_is_it_bidir(
                paper_obj=paper, zenodo_url=url, output_dir=output_dir)
       
        if is_bidir:
            if first_time:
                result[iden] = []
                first_time = False
            entry = {
                "url": url,
                "bidirectional": is_bidir
            }
            result[iden].append(entry)
    return


def _git_check_directionality(paper, git_urls, directionality, iden, first_time, output_dir, result):
    is_unidir = None
    is_bidir = None

    for url in git_urls:
        # Download repository from SOMEF
        repo_file = download_repo_metadata(url, output_dir)
        if not repo_file:
            log.error(f"Issue while downloading the repository for {iden}")
            continue
        # assessment of bidirectionality
        if directionality:
            is_bidir = git_is_it_bidir(paper, repo_file)
        if not directionality:
            is_unidir = is_repo_unidir(paper, repo_file)
        if is_bidir:
            if first_time:
                result[iden] = []
                first_time = False
            entry = {
                "url": url,
                "bidirectional": is_bidir
            }
            result[iden].append(entry)
        if is_unidir:
            if first_time:
                result[iden] = []
                first_time = False
            result[iden].append(url)
    return


def safe_dic(dict, key):
    try:
        return dict[key]
    except:
        return None
