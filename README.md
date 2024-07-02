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

The download command allows for a user to download the pdf with its metadata given an Identifier: ArXiv or DOI.  Alongside the PDFs folder there will be a `downloaded_metadata.json` which will have the Title, DOI, ArXiv and filename/filepath for each paper downloaded. RSEF uses [Unpaywall](https://api.unpaywall.org) to download open access publications. 

```
rsef download -h 
Usage: rsef download [OPTIONS]

Options:

-i, --input <name> DOI or path to .txt list of DOIs  [required]

-o, --output <path>  Output Directory [default: ./]

-h, --help Show this message and exit.
```

### Assess

The assess command locates code implementations in a publication, given its identifier (ArXiv id or DOI). For each of the candidate code repository links found in the target publication, the `assess` command will find whether there is a unidirectional or bidirectional link. This command accepts different inputs:

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

The resulting information after executing the command will be saved in ```output/url_search_output.json```. See [the JSON output specification](doc/JSONs.md) to understand the structure and fields in the JSON result.

Usage: 
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

- The **unidirectional link search** uses the [RepoFromPaper](https://github.com/StankovskiA/RepoFromPaper) submodule to search for the implementation repository link in the paper. RepoFromPaper uses a SciBert Model to classify the paper's text as either a proposal sentence or not. The top 5 highest ranked sentences are then searched for a repository link. If no link is found in the initial search, a footnote/reference search is conducted. RepoFromPaper can either return a link or return an empty response if no link is found.
- The **bidirectional link search** intends to find paper-repo links where both the paper points to the repo and the repo (metadata) points back to the paper. The search may find zero, one, or multiple bidirectional links. 


<!--
### Prediction

For assessment of the program against its corpus. The corpus can be found within [corpus.csv](./predicition/corpus.csv) and the f1 score obtained bidirectional:  [corpus_eval_bidir.json](./predicition/corpus_eval_bidir.json) and the same for the unidirectional (_unidir)
-->


## RSEF Evaluation
Below we detail the evaluation methods and corpora used for RSEF

### Unidirectional extraction

For the training corpus for our models, we included [75 implementation sentences and approximately 2500 non-implementation sentences](https://doi.org/10.5281/zenodo.10701846) from 61 research papers sourced from the [PapersWithCode platform](https://paperswithcode.com/). To evaluate the performance of our method, we assembled a [separate evaluation corpus](https://doi.org/10.5281/zenodo.10980368) consisting of 150 software engineering research papers obtained from [Arxiv.org](https://arxiv.org/). These papers were carefully selected to ensure heterogeneity and avoid repetitiveness, representing a diverse range of implementation mention styles, authored by various authors. We manually tagged these papers to create a validation set specifically for evaluating our methodology. Importantly, none of the papers included in this validation set were used for training the models, ensuring the integrity of our evaluation process.

### Bidirectional extraction

The bidirectional search of RSEF has been validated with a corpus made of 154 papers and repositories, including  several types of bi-directionality paper-repository links (e.g., repositories including just the title, Arxiv URLs or DOIs in the README file, using citation files, repositories in different code platforms, etc.). Two annotators were selected to manually annotate the presence of bi-directionality. In case of two different annotations in the corpus, a third annotator decided the final value.

A summary of the performance of each method for each evaluation corpora can be seen in the table below:

| Type of extraction |Train corpus | Eval. corpus | Precision | Recall | F1-Measure |
|---|--- |---|---|---|---|
| unidirectional |[Link](https://doi.org/10.5281/zenodo.10701846) | [Link](https://doi.org/10.5281/zenodo.10980368) | 0.94 | 0.95 | 0.94 |
| bidirectional | N/A| [Link](https://github.com/SoftwareUnderstanding/RSEF/blob/main/evaluation/bidirectional/corpus.tsv) | 1 | 0.91 | 0.95 |

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
The unidirectional evaluation makes use of [RepoFromPaper](https://github.com/StankovskiA/RepoFromPaper), which has the following NSLP2024 workshop paper:
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
