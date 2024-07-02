[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10306762.svg)](https://doi.org/10.5281/zenodo.10306762) [![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
  
# Research Software Extraction Framework (RSEF)

RSEF extracts the link between a scientific paper and its corresponding software implementations (i.e., code repositories). It accomplishes this by locating URLs of software repositories within the scientific papers. Two main types of implementations are extracted:
1. **Unidirectional links**: Papers that point to code repositories. RSEF analyzes the context of the mention to detect whether a candidate is appropriate (e.g., "our code is available at 'URL'")
2. **Bidirectional links**: RSEF extracts the metadata of the target repository to find any reference back to the original paper (e.g., citation files, mentions in README, etc.)

For each candidate link, RSEF indicates how it was found in the original publication, along with the type of connection found (unidirectional or bidirectional). The response is structured according to the following [JSON format](doc/JSONs.md).  

## Dependencies

- Python 3.9

- Java 8 or above (please see [Tika requirements](https://pypi.org/project/tika/))

## Installation

Install the required dependencies by running:

```
pip install -e .
```

Highly recommended steps:

```
somef configure
```

You will be asked to provide:

* A GitHub authentication token [**optional, leave blank if not used**], which SOMEF uses to retrieve metadata from GitHub. If you don't include an authentication token, you can still use SOMEF. However, you may be limited to a series of requests per hour. For more information, see [https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)

* The path to the trained classifiers (pickle files). If you have your own classifiers, you can provide them here. Otherwise, you can leave it blank

  

## Usage

```
Usage: rsef [OPTIONS] COMMAND [ARGS]...

RRRRRRRRR     SSSSSSSSS    EEEEEEEEE  FFFFFFFFF  
RRR    RRR   SSS     SSS   EEE        FFF  
RRR    RRR   SSSS          EEE        FFF
RRRRRRRRR     SSSSSSSSS    EEEEEEE    FFFFFFF  
RRR    RRR          SSSS   EEE        FFF  
RRR     RRR   SSS    SSS   EEE        FFF  
RRR      RRR   SSSSSSSS    EEEEEEEEE  FFF  
  
Research Software Extraction Framework (RSEF)\n
Find and assess Research Software within Research papers.

Usage:
1. (assess) Assess doi for unidirectionality or bidirectionality
2. (download) Download PDF (paper) from a doi or list

Options:
--version Show the version and exit.
-h, --help  Show this message and exit.

Commands:
	assess
	download
```

### Download

The download command allows for a user to download the pdf with its metadata given an Identifier: ArXiv or DOI.  Alongside the PDFs folder there will be a `downloaded_metadata.json` which will have the Title, DOI, ArXiv and filename/filepath for each paper downloaded. RSEF uses unpaywall to download open access publications. 

```
rsef download -h 
Usage: rsef download [OPTIONS]

Options:

-i, --input <name> DOI or path to .txt list of DOIs  [required]

-o, --output <path>  Output Directory [default: ./]

-h, --help Show this message and exit.
```

### Assess

The assess command allows for a user to determine whether a given Identifier, in this case ArXiv or DOI, is bidirectional or not. This command accepts different inputs:

1. A single DOI/ArXiv

2. A list of identifiers given as a ```.txt```

3. A path to downloaded_metadata.json file

4. A path to processed_metadata.json file

5. A path to results.json file, obtained by executing 
doiExtractor tool (https://github.com/oeg-upm/DOI-Extractor-OEG).
This results.json file has the following format:
```
[
    {
        "title": title of the paper,
        "doi": DOI of the paper,
        "primary_location": URL of the paper's PDF if exists in OpenAlex
    },
]
```
The resulting information after executing the command will be saved in ```output/url_search_output.json```.


```text
rsef assess -h
Usage: sskg assess [OPTIONS]

Options:

-i, --input <name> DOI, path to .txt list of DOIs or path to processed_metadata.json [required]

-o, --output <path>  Output csv file  [default: output]

-U, --unidir Unidirectional link search

-B, --bidir  Bidirectional link search

-h, --help Show this message and exit.
```

- The unidirectional link search uses the RepoFromPaper submodule to search for the implementation repository link in the paper. The RepoFromPaper submodule utilizes a SciBert Model to classify the paper's text as either a proposal sentence or not. The top 5 highest ranked sentences are then searched for a repository link. If no link is found in the initial search, a footnote/reference search is conducted. RepoFromPaper can either return a link or return an empty response if no link is found.
- The bidirectional link search intends to find paper-repo links where both the paper points to the repo and the repo (metadata) points back to the paper. The bidir search targets 'Git' and 'Zenodo' links. The search may find zero, one, or multiple bidirectional links. 
- If repository links are found in the paper, the links and search methods (unidir/bidir) are added to the `ImplementationUrl` list in the `PaperObj` of the paper. The list of implementation urls is initially created using regex link search method when the paper object is created. Both the unidir and bidir search methods return the `PaperObj`, with the updated `ImplementationUrl` list if links were found.


<!--
### Prediction

For assessment of the program against its corpus. The corpus can be found within [corpus.csv](./predicition/corpus.csv) and the f1 score obtained bidirectional:  [corpus_eval_bidir.json](./predicition/corpus_eval_bidir.json) and the same for the unidirectional (_unidir)
-->


## RSEF Evaluation

RSEF has been validated with a corpus made of 154 papers and repositories, including  several types of bi-directionality paper-repository links (e.g., repositories including just the title, Arxiv URLs or DOIs in the README file, using citation files, repositories in different code platforms, etc.)

Two annotators were selected to manually annotate the presence of bi-directionality. In case of two different annotations in the corpus, a third annotator decided the final value.

This corpus, in TSV format, can be found in the [evaluation/bidirectional folder](https://github.com/SoftwareUnderstanding/RSEF/blob/main/evaluation/bidirectional/corpus.tsv).

In case you want to run the evaluation, you will have to use the script presents in the evaluation_only_ids folder.
  
```
python eval_corpus_big.py
```

A file name **output_metrics.json** will be generated with the results of the evaluation. You can find metrics such as precision, recall, f1-score and the list of false negatives.

The results of the evaluation using our corpus are:
- **precision:** 1.0
- **recall:** 0.918918918918919
- **f1-score:** 0.9577464788732395

## Cite RSEF
Please refer to our Mining Software Repositories 2024 paper:
```
@InProceedings{garijo_2024_bidirectional,
    author="Garijo, Daniel and Arroyo, Miguel and Gonzalez, Esteban and Treude, Christoph and Tarocco, Nicola",
    title="Bidirectional Paper-Repository Tracing in Software Engineering",
    booktitle="21st International Conference on Mining Software Repositories",
    year="2024",
    publisher="ACM",
    address="Cham",
    doi="10.1145/3643991.3644876",
    url= {https://dgarijo.com/papers/msr_2024.pdf}
}
```
The unidirectional evaluation makes use of [RepoFromPaper](https://github.com/StankovskiA/RepoFromPaper), which has the following workshop paper:
```
@article{stankovski2024,
  title		   = {RepoFromPaper: An Approach to Extract Software Code Implementations from Scientific Publications},
  author	   = {Stankovski, Aleksandar and Garijo, Daniel},
  year         = {2024},
  booktitle    = {To appear in Natural Scientific Language Processing and Research Knowledge Graphs (NSLP 2024) },
  url          = {https://dgarijo.com/papers/stankovsi_2024.pdf}
}
```

## License

This project is licensed under the [MIT License](LICENSE).  
