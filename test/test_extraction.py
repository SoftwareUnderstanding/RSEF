import json
import os.path
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from src.RSEF.extraction.somef_extraction.somef_extractor import is_github_repo_url, download_repo_metadata, get_related_paper, \
    description_finder, find_doi_citation, find_arxiv_citation

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_FOLDER = os.path.join(TEST_DIR, "pipeline_folder")

def wipe_directory(directory_path):
    for path in Path(directory_path).glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)

def load_json(path):
    with open(path,'r') as f:
        return json.load(f)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-------------------------------------------------Extraction Testing----------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class test_somef_extraction(TestCase):

    def test_github_url(self):
        test = "https://github.com/SoftwareUnderstanding/SSKG"
        ans = is_github_repo_url(test)
        self.assertTrue(ans)

    def test_not_github_url(self):
        test = "https://github.com/SoftwareUnderstandingSSKG"
        ans = is_github_repo_url(test)
        self.assertFalse(ans)

    def test_None_github_url(self):
        test = None
        ans = is_github_repo_url(test)
        self.assertFalse(ans)
    #!-----------------------------------------------
    #Test download_repo_metadata:
    #

    def test_dwnld_repo_meta(self):
        wipe_directory(PIPELINE_FOLDER)
        real_url = "https://github.com/SoftwareUnderstanding/SSKG"
        ans = download_repo_metadata(url=real_url, output_folder_path=PIPELINE_FOLDER)
        self.assertTrue(os.path.exists(ans))

    def test_already_dwnldd_repo_meta(self):
        real_url = "https://github.com/SoftwareUnderstanding/SSKG"
        output_dir = os.path.join(TEST_DIR, "json")
        expected = os.path.join(output_dir, "JSONs\SoftwareUnderstanding_SSKG.json")
        ans = download_repo_metadata(url=real_url, output_folder_path=output_dir)
        self.assertEqual(ans,str(expected))

    def test_d_r_m_not_url(self):
        fake_url = ""
        ans = download_repo_metadata(url=fake_url, output_folder_path=PIPELINE_FOLDER)
        self.assertIsNone(ans)

    def test_d_r_m_none_url(self):
        none_url = None
        ans = download_repo_metadata(url=none_url, output_folder_path=PIPELINE_FOLDER)
        self.assertIsNone(ans)

    def test_d_r_m_output_nonexistent(self):
        wipe_directory(PIPELINE_FOLDER)
        real_url = "https://github.com/SoftwareUnderstanding/SSKG"
        non_existent_dir = os.path.join(PIPELINE_FOLDER,"non_existent")
        ans = download_repo_metadata(url=real_url, output_folder_path=non_existent_dir)
        self.assertTrue(os.path.exists(ans))
    def test_d_r_m_output_path_none(self):
        real_url = "https://github.com/SoftwareUnderstanding/SSKG"
        ans = download_repo_metadata(url=real_url, output_folder_path=None)
        self.assertIsNone(ans)

    def test_d_r_m_somef_fail(self):
        wipe_directory(PIPELINE_FOLDER)
        real_url = "https://github.com/oeg-upm/web-oeg"
        ans = download_repo_metadata(url=real_url, output_folder_path=PIPELINE_FOLDER)
        self.assertIsNone(ans)

    # !-----------------------------------------------
    # Test related paper extraction:
    #
    def test_related_paper(self):
        false_dict = {"related_papers": [{"result": {"value": ";alskdfja2206.05328"}}]}
        ans = get_related_paper(false_dict)
        expected = "2206.05328"
        self.assertEqual(ans[0],expected)
        pass

    def test_related_none(self):
        ans = get_related_paper(None)
        self.assertIsNone(ans)

    def test_no_related(self):
        false_dic = {}
        ans = get_related_paper(false_dic)
        self.assertIsNone(ans)

    def test_empty_related_paper_1(self):
        false_dict = {"related_papers": [{"result": {"value": ""}}]}
        ans = get_related_paper(false_dict)
        self.assertIsNone(ans)

    def test_empty_related_paper_2(self):
        false_dict = {"related_papers": [{"result": {}}]}
        ans = get_related_paper(false_dict)
        self.assertIsNone(ans)

    def test_empty_related_paper_3(self):
        false_dict = {"related_papers": []}
        ans = get_related_paper(false_dict)
        self.assertIsNone(ans)

    #!-----------------------------------------------
    #Test Description extraction:
    #
    def test_description_arxiv(self):
        false_dict = {"description": [{"result": {"value": ";alskdfja2206.05328"}}]}
        ans = description_finder(false_dict)
        expected = "2206.05328"
        self.assertEqual(ans['arxiv'].pop(), expected)

    def test_description_doi(self):
        false_dict = {"description": [{"result": {"value": ";alskdfja2206.05328https://doi.org/10.5281/zenodo.838601"}}]}
        ans = description_finder(false_dict)
        expected = "10.5281/zenodo.838601"
        self.assertEqual(ans['doi'].pop(), expected)

    def test_description_both(self):
        false_dict = {"description": [{"result": {"value": ";alskdfja2206.05328asfhttps://doi.org/10.5555/KVTD-VPWM"}}]}
        ans = description_finder(false_dict)
        expected_doi = "10.5555/KVTD-VPWM"
        expected_arxiv = "2206.05328"
        self.assertTrue((ans['doi'].pop() == expected_doi) and (ans['arxiv'].pop() == expected_arxiv))

    def test_description_none(self):
        # TODO ensure this return is optimal
        ans = description_finder(None)
        res = ((len(ans["doi"]) == 0)  and (len(ans["doi"]) == 0))
        self.assertTrue(res)

    def test_no_description(self):
        false_dic = {}
        ans = description_finder(false_dic)
        self.assertTrue(len(ans['doi']) == 0)

    def test_empty_description_1(self):
        false_dict = {"related_papers": [{"result": {"value": ""}}]}
        ans = description_finder(false_dict)
        self.assertTrue(len(ans['doi']) == 0)
    def test_empty_description_2(self):
        false_dict = {"related_papers": [{"result": {}}]}
        ans = description_finder(false_dict)
        self.assertTrue(len(ans['doi']) == 0)
    def test_empty_description_3(self):
        false_dict = {"related_papers": []}
        ans = description_finder(false_dict)
        self.assertTrue(len(ans['doi']) == 0)

    #!-----------------------------------------------
    #Test find_doi_citation:
    #
    def test_find_doi_citation_cff(self):
        false_dict = {"citation": [{"result": {"format": "cff", "value": "https://doi.org/10.5555/KVTD-VPWM"}}]}
        expected = (['10.5555/KVTD-VPWM'], None)
        ans = find_doi_citation(false_dict)
        self.assertEqual(ans["CFF"][0], expected)

    def test_find_doi_citation_none(self):
        ans = find_doi_citation(None)
        self.assertIsNone(ans)

    def test_find_doi_broken_citation_cff(self):
        false_dict = {"citation": [{"result":{"format":"cff", "value": ""}}]}
        ans = find_doi_citation(false_dict)
        self.assertIsNone(ans)

    def test_find_doi_broken_citation_2_cff(self):
        false_dict = {"citation": [{"result":{"format":"cff"}}]}
        ans = find_doi_citation(false_dict)
        self.assertIsNone(ans)

    def test_find_doi_broken_citation_3(self):
        false_dict = {"citation": [{}]}
        ans = find_doi_citation(false_dict)
        self.assertIsNone(ans)

    def test_find_doi_citation_bib(self):
        false_dict = {"citation": [{"result": {"format": "bibtex","value":"https://doi.org/10.5555/KVTD-VPWM"}}]}
        expected = (['10.5555/KVTD-VPWM'], None)
        ans = find_doi_citation(false_dict)
        self.assertEqual(ans["BIBTEX"].pop(), expected)

    def test_find_doi_broken_citation(self):
        false_dict = {"citation": [{"result": {"format": "RANDOM", "value": ""}}]}
        ans = find_doi_citation(false_dict)
        self.assertIsNone(ans)

    def test_find_doi_text_excerpt(self):
        false_dict = {"citation": [{"result": {"type": "Text_excerpt", "value": "https://doi.org/10.5555/KVTD-VPWM"}}]}
        expected = (['10.5555/KVTD-VPWM'], None)
        ans = find_doi_citation(false_dict)
        self.assertEqual(ans["TEXT"].pop(), expected)

    def test_real_life_example_2_dois(self):
        examp_json = os.path.join(TEST_DIR, "json/somef.json")
        somef_data = load_json(examp_json)
        ans = find_doi_citation(somef_data = somef_data)
        print(ans)
        self.assertTrue(len(ans["CFF"]) > 0)

    #!-----------------------------------------------
    #Test find_arxiv_citation:
    #
    def test_find_arxiv_citation_cff(self):
        false_dict = {"citation": [{"result": {"format": "cff", "value": "https://arxiv.org/abs/2206.05328"}}]}
        expected = (["2206.05328"], None)
        ans = find_arxiv_citation(false_dict)
        self.assertEqual(ans["CFF"].pop(), expected)

    def test_find_arxiv_citation_none(self):
        ans = find_arxiv_citation(None)
        self.assertIsNone(ans)

    def test_find_arxiv_broken_citation_cff(self):
        false_dict = {"citation": [{"result":{"format":"cff", "value": ""}}]}
        ans = find_arxiv_citation(false_dict)
        self.assertIsNone(ans)

    def test_find_arxiv_broken_citation_2_cff(self):
        false_dict = {"citation": [{"result":{"format":"cff"}}]}
        ans = find_arxiv_citation(false_dict)
        self.assertIsNone(ans)

    def test_find_arxiv_broken_citation_3(self):
        false_dict = {"citation": [{}]}
        ans = find_arxiv_citation(false_dict)
        self.assertIsNone(ans)
    def test_find_arxiv_citation_bib(self):
        false_dict = {"citation": [{"result": {"format": "bibtex","value":"ads;fl\n2206.05328"}}]}
        expected = (["2206.05328"], None)
        ans = find_arxiv_citation(false_dict)
        self.assertEqual(ans["BIBTEX"].pop(), expected)

    def test_find_arxiv_broken_citation(self):
        false_dict = {"citation": [{"result": {"format": "RANDOM", "value": ""}}]}
        ans = find_arxiv_citation(false_dict)
        self.assertIsNone(ans)

    def test_find_arxiv_text_excerpt(self):
        false_dict = {"citation": [{"result": {"type": "Text_excerpt", "value": "a;lskdfj;l2206.05328"}}]}
        expected = (["2206.05328"], None)
        ans = find_arxiv_citation(false_dict)
        self.assertEqual(ans["TEXT"].pop(), expected)

    def test_real_life_example_2_arxivs(self):
        examp_json = os.path.join(TEST_DIR, "json/somef.json")
        somef_data = load_json(examp_json)
        ans = find_arxiv_citation(somef_data = somef_data)
        self.assertTrue(len(ans) > 0)


from src.RSEF.extraction.pdf_extraction_tika import raw_read_pdf, read_pdf_list

class test_pdf_extraction_tika(TestCase):
    def test_raw_pdf(self):
        path_file = os.path.join(TEST_DIR, "pdfs/widoco-iswc2017.pdf")
        raw = raw_read_pdf(path_file)
        self.assertIsNotNone(raw)
        pass

    def test_raw_pdf_file_not_found(self):
        made_up_path = "./jeremy/pdfs/widoco-iswc2017.pdf"
        ans = raw_read_pdf(made_up_path)
        self.assertEqual(ans, "")

    def test_raw_pdf_none(self):
        self.assertEqual(raw_read_pdf(None), "")

    #!-----------------------------------------------
    #Test read_list_pdf:
    #
    def test_read_pdf_list(self):
        path_file = os.path.join(TEST_DIR, "pdfs/widoco-iswc2017.pdf")
        raw = read_pdf_list(path_file)
        self.assertIsNotNone(raw)
        pass

    def test_read_pdf_list_file_not_found(self):
        made_up_path = "./jeremy/pdfs/widoco-iswc2017.pdf"
        ans = read_pdf_list(made_up_path)
        self.assertTrue(len(ans) == 0)


    def test_read_pdf_list_none(self):
        self.assertTrue(len(read_pdf_list(None)) == 0)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


from src.RSEF.extraction.pdf_title_extraction import extract_pdf_title, use_pdf_title, use_tika_title
class test_title_extraction_pdf(TestCase):

    def test_normal_case(self):
        path_file = os.path.join(TEST_DIR, "pdfs/widoco-iswc2017.pdf")
        title = use_pdf_title(path_file)
        self.assertEqual("WIDOCO: A Wizard for Documenting Ontologies", title)
    def test_no_pdf(self):
        title = use_pdf_title("")
        self.assertIsNone(title)

    def test_tika_title_normal_pdf(self):
        path_file = os.path.join(TEST_DIR, "pdfs/widoco-iswc2017.pdf")
        title = use_pdf_title(path_file)
        print(title)
        self.assertEqual("WIDOCO: A Wizard for Documenting Ontologies", title)

    def test_tika_title_seperator_pdf(self):
        path_file = os.path.join(TEST_DIR,"pdfs/test_with_weird_seperation.pdf")
        title = use_pdf_title(path_file)
        self.assertEqual("AVIS: Autonomous Visual Information Seeking with Large Language Models", \
                          title)

    def test_tika_title_3(self):
        path_file = os.path.join(TEST_DIR,"pdfs/possible_fail.pdf")
        title = use_pdf_title(path_file)
        expected = "Intensity-modulated radiotherapy versus stereotactic body radiotherapy for prostate cancer (PACE-B): 2-year toxicity results from an open-label, randomised, phase 3, non-inferiority trial"
        self.assertEqual(title, expected)

    def test_tika_title4(self):
        #Found a failure, this paper has a header in the title page
        path_file = os.path.join(TEST_DIR,"pdfs/poss_fail2.pdf")
        title = use_pdf_title(path_file)
        expected = "DYNAMIC CARDIAC MRI RECONSTRUCTION USING COMBINED TENSOR NUCLEAR NORM AND CASORATI MATRIX NUCLEAR NORM REGULARIZATIONS"
        self.assertNotEqual(title,expected)

    def test_pdf_title(self):
        #test_tika_title3 fails but works with pdf_title
        path_file = os.path.join(TEST_DIR, "pdfs/poss_fail2.pdf")
        title = use_pdf_title(path_file)
        expected = "Dynamic Cardiac MRI Reconstruction Using Combined Tensor Nuclear Norm and Casorati Matrix Nuclear Norm Regularizations"
        self.assertEqual(expected, title)

    def test_title_extract(self):
        path_file = os.path.join(TEST_DIR,"pdfs/unicode_fail.pdf")
        title = extract_pdf_title(path_file)
        expected = "Data governance through a multi-DLT architecture in view of the GDPR"
        self.assertEqual(title, expected)


from src.RSEF.extraction.pdf_extraction_tika import ranked_git_url

from src.RSEF.object_creator.downloaded_to_paperObj import dwnlddJson_to_paperJson

class test_github_url_extraction_pdf(TestCase):

    def test_problematic_pdf_urls_1(self):
        path_file = os.path.join(TEST_DIR, "pdfs/2305.16120v1.pdf")
        pdf_data = read_pdf_list(path_file)
        git_urls = ranked_git_url(pdf_data)
        print(git_urls)


    def test_process(self):
        path_file = os.path.join(TEST_DIR, "json/false_dowloaded.json")
        paper = dwnlddJson_to_paperJson(dwnldd_json=path_file, output_dir=PIPELINE_FOLDER)
        print(paper)