import json
import os.path
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

# from ..modelling.bidirectionality import *
from src.RSEF.object_creator.paper_to_directionality import check_paper_directionality
from src.RSEF.object_creator.pipeline import doi_to_paper
from src.RSEF.object_creator.paper_obj_utils import paperDict_to_paperObj

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_FOLDER = os.path.join(TEST_DIR, "pipeline_folder")


def wipe_directory(directory_path):
    for path in Path(directory_path).glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# -------------------------------------------------Directionality Testing------------------------------------------------
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class test_bidir(TestCase):

    def test_citation_doi1(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "10.1162/qss_a_00167",
            "arxiv": "1235.12456",
            "title": "Software Metadata Extraction Framework (SOMEF)",
            "file_name": "",
            "file_path": "",
            "urls": {"git": [{"url": "https://github.com/KnowledgeCaptureAndDiscovery/somef", "#_appearances": 1}]}

        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/KnowledgeCaptureAndDiscovery/somef"
        self.assertEqual(expected_result, result["10.1162/qss_a_00167"][0]["url"])

    def test_citation_doi2(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "10.1007/978-3-319-68204-4_9",
            "arxiv": "1235.12456",
            "title": "WIDOCO: a wizard for documenting ontologies",
            "file_name": "",
            "file_path": "",
            "urls": {"git": [{"url": "https://github.com/dgarijo/Widoco", "#_appearances": 1}]}
        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/dgarijo/Widoco"
        self.assertEqual(expected_result, result["10.1007/978-3-319-68204-4_9"][0]["url"])

    def test_doi_pipeline(self):
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1016/j.compbiomed.2019.05.002"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = 'https://github.com/mateuszbuda/brain-segmentation'
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_doi_pipeline1(self):
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.18653/v1/2021.findings-emnlp.116"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = 'https://github.com/YunqiuXu/H-KGA'
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_doi_pipeline2(self):
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1051/0004-6361/201935695"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = 'https://github.com/astro-alexis/magnotron-tts'
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_doi_pipeline3(self):
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1109/itsc.2019.8917177"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = 'https://github.com/lukasliebel/MultiDepth'
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_doi_pipeline_no_ids(self):
        wipe_directory("pipeline_folder")
        doi = "10.1109/iwis56333.2022.9920762"
        paper = doi_to_paper(doi, "pipeline_folder")
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        # self.assertIsNone(result)

    def test_doi_pipeline5(self):
        # FAILS DUE TO SOMEF, DOES NOT EXTRACT
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1145/3485447.3511945"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = 'https://github.com/THUDM/SelfKG'
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_doi_pipeline6(self):
        # TODO
        # fails due to pointing to a new version of arxiv. Has a new ID
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1007/978-3-319-26123-2_24"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = 'https://github.com/IlyaTrofimov/dlr'
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_arxiv_related(self):
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1109/itsc.2019.8917177"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = 'https://github.com/lukasliebel/MultiDepth'
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_arxiv_related2(self):
        '''It is not mentioned within the paper'''
        wipe_directory("pipeline_folder")
        doi = "10.18653/v1/2021.naacl-main.458"
        paper = doi_to_paper(doi, "pipeline_folder")
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = paper
        self.assertEqual(result, expected_result)

    def test_arxiv_1(self):
        '''Test to download first OA the best pdf has 403 forbidden'''
        # wipe_directory(PIPELINE_FOLDER)
        doi = "10.1109/iccv48922.2021.00338"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/uncbiag/ICON"
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_arxiv_2(self):
        '''Test to download first OA the best pdf has 403 forbidden'''
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.18653/v1/2020.acl-main.55"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/cl-tohoku/eval-via-selection"
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_arxiv_3(self):
        # TODO add the crossref to fix this openAlex issue
        '''Will fail due to OpenAlex'''
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.24963/ijcai.2022/208"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/Robbie-Xu/CPSD"
        # self.assertEqual(result[doi]["url"], expected_result)
        pass

    def test_arxiv_5(self):
        # TODO
        '''Different Arxiv's'''
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1007/978-3-319-26123-2_24"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/IlyaTrofimov/dlr"
        # self.assertEqual(result[doi]["url"], expected_result)
        pass

    def test_arxiv_6(self):
        ''''''
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.2478/pralin-2018-0002"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/tensorflow/tensor2tensor"
        self.assertEqual(result[doi][0]["url"], expected_result)

    def test_arxiv_7(self):
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.21428/58320208.e46b7b81"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/aklamun/Stablecoin_Deleveraging"
        res_urls = []
        for i in result[doi]:
            res_urls.append(i["url"])
        self.assertTrue(expected_result in res_urls)

    def test_arxiv_8(self):
        '''Test should pass, readme is an absolute mess'''
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1051/0004-6361/202039603"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "http://github.com/mianbreton/RR_code"
        self.assertEqual(expected_result, result[doi][0]["url"])

    def test_arxiv_9(self):
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.18653/v1/2020.emnlp-main.495"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/AI-secure/T3"
        self.assertEqual(expected_result, result[doi][0]["url"])

    def test_doi_2(self):
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1145/3508352.3549415"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/momalab/e3"
        self.assertEqual(expected_result, result[doi][0]["url"])

    def test_doi_3(self):
        # TODO SOMEF ISSUE
        wipe_directory(PIPELINE_FOLDER)
        doi = "10.1145/3318170.3318183"
        paper = doi_to_paper(doi, PIPELINE_FOLDER)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/CodeplaySoftware/SYCL-DNN"
        pass
        # self.assertTrue(expected_result in result[doi])

    # def test_title(self):
    #     from src.RSEF.object_creator.paper_obj_utils import paperDict_to_paperObj
    #     wipe_directory(PIPELINE_FOLDER)
    #     pp_dict = {
    #         "doi": "https://doi.org/10.48550/arXiv.2307.10793",
    #         "arxiv": "2307.10793",
    #         "title": "Addressing Compiler Errors: Stack Overflow or Large Language Models?",
    #         "file_name": "",
    #         "file_path": "",
    #         "urls": [("https://github.com/patwdj/java-compiler-error-help",1)]
    #     }
    #     paper = paperDict_to_paperObj(pp_dict)
    #     result = check_paper_directionality(paper,True, PIPELINE_FOLDER)
    #     print(result)

    def test_title1(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "",
            "arxiv": "1234.56789",
            "title": "WIDOCO: a wizard for documenting ontologies",
            "file_name": "",
            "file_path": "",
            "urls": {"git": [{"url": "https://github.com/dgarijo/Widoco", "#_appearances": 1}]}
        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://github.com/dgarijo/Widoco"
        self.assertEqual(expected_result, result["1234.56789"][0]["url"])

    def test_zenodo_bidir(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "",
            "arxiv": "1234.56789",
            "title": "WIDOCO: a wizard for documenting ontologies",
            "file_name": "",
            "file_path": "",
            "urls": {"zenodo": [{"url": "https://zenodo.org/records/7867989", "#_appearances": 1}]}
        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = "https://zenodo.org/records/7867989"
        self.assertEqual(expected_result, result["1234.56789"][0]["url"])

    def test_zenodo_bidir_wrong_url(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "",
            "arxiv": "1234.56789",
            "title": "WIDOCO: a wizard for documenting ontologies",
            "file_name": "",
            "file_path": "",
            "urls": {"zenodo": [{"url": "https://zenodo.org/records/77989", "#_appearances": 1}]}
        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = paper
        self.assertEqual(result, expected_result)

    def test_zenodo_bidir_no_url(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "",
            "arxiv": "1234.56789",
            "title": "WIDOCO: a wizard for documenting ontologies",
            "file_name": "",
            "file_path": "",
            "urls": {"zenodo": [{"url": "", "#_appearances": 1}]}
        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)

        expected_result = paper
        self.assertEqual(result, expected_result)

    def test_zenodo_bidir_broken_url(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "",
            "arxiv": "1234.56789",
            "title": "WIDOCO: a wizard for documenting ontologies",
            "file_name": "",
            "file_path": "",
            "urls": {"zenodo": []}
        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = paper
        self.assertEqual(result, expected_result)

    def test_zenodo_bidir_broken_url_1(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "",
            "arxiv": "1234.56789",
            "title": "WIDOCO: a wizard for documenting ontologies",
            "file_name": "",
            "file_path": "",
            "urls": {"zenodo": []}
        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)
        expected_result = paper
        self.assertEqual(result, expected_result)

    def test_zenodo_bidir_broken_url_2(self):
        wipe_directory(PIPELINE_FOLDER)
        pp_dict = {
            "doi": "",
            "arxiv": "1234.56789",
            "title": "WIDOCO: a wizard for documenting ontologies",
            "file_name": "",
            "file_path": "",
            "urls": {}
        }
        paper = paperDict_to_paperObj(pp_dict)
        result = check_paper_directionality(paper, True, PIPELINE_FOLDER)

        expected_result = paper
        self.assertEqual(result, expected_result)

    def test_prob_(self):
        wipe_directory(PIPELINE_FOLDER)
        paper = {
            "abstract": "ABSTRACTKMOS (K-Band Multi Object Spectrograph) is a novel integral field spectrograph installedin the VLT’s ANTU unit. The instrument offers an ability to observe 24 2.8′′×2.8′′ sub$",
            "arxiv": "1508.02911",
            "doi": None,
            "file_name": "1508.02911.pdf",
            "file_path": "./output_files/1508.02911/1508.02911.pdf",
            "title": "Exoplanet Transmission Spectroscopy using KMOS",
            "urls": {
                "git": [
                    {
                        "#_appearances": 1,
                        "url": "https://github.com/hpparvi/PyTransit"
                    },
                    {
                        "#_appearances": 1,
                        "url": "https://github.com/hpparvi/PyDE"
                    }
                ]
            }
        }
        pp = paperDict_to_paperObj(paper)
        # result = check_paper_directionality(pp, True, PIPELINE_FOLDER)
        # print(result)

    def test_related_4(self):
        wipe_directory(PIPELINE_FOLDER)
