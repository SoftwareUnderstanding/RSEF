# Research Software Extraction Framework (RSEF)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10306762.svg)](https://doi.org/10.5281/zenodo.10306762) [![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

RSEF extracts the link between a scientific paper and its corresponding software implementations (i.e., code repositories). It accomplishes this by locating URLs of software repositories within scientific papers. Two main types of implementations are extracted:

1. **Unidirectional links**: Papers that point to code repositories. RSEF analyzes the context of the mention to detect whether a candidate is appropriate (e.g., "our code is available at 'URL'").
2. **Bidirectional links**: RSEF extracts the metadata of the target repository to find any reference back to the original paper (e.g., citation files, mentions in README, etc.).

For each candidate link, RSEF indicates how it was found in the original publication, along with the type of connection found (unidirectional or bidirectional). The response is structured according to the following [JSON format](doc/JSONs.md).

## Dependencies

- Python 3.9
- Java 8 or above (please see [Tika requirements](https://pypi.org/project/tika/))

## Installation

Install the required dependencies by running:

```bash
pip install -e .
```

Highly recommended steps:

```bash
somef configure
```

You will be asked to provide:

* A GitHub authentication token [**optional, leave blank if not used**], which SOMEF uses to retrieve metadata from GitHub. If you don't include an authentication token, you can still use SOMEF. However, you may be limited to a series of requests per hour. For more information, see [GitHub Personal Access Tokens](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
* The path to the trained classifiers (pickle files). If you have your own classifiers, you can provide them here. Otherwise, you can leave it blank.

## Usage

```
Usage: rsef [OPTIONS] COMMAND [ARGS]...
```

### Commands

#### **Download**

The `download` command allows a user to download the PDF of a research paper given an identifier (DOI or ArXiv ID). The downloaded files and their metadata will be stored in a `downloaded_metadata.json` file.

```bash
rsef download -h
Usage: rsef download [OPTIONS]

Options:

-i, --input <name> DOI or path to .txt list of DOIs  [required]
-o, --output <path>  Output Directory [default: ./]
-h, --help Show this message and exit.
```

#### **Assess**

The `assess` command analyzes a publication to locate software implementation links. It identifies whether each link is unidirectional or bidirectional.

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


```bash
rsef assess -h
Usage: rsef assess [OPTIONS]

Options:
-i, --input <name> DOI, path to .txt list of DOIs or path to processed_metadata.json [required]
-o, --output <path>  Output csv file  [default: output]
-U, --unidir Unidirectional link search
-B, --bidir  Bidirectional link search
-h, --help Show this message and exit.
```

- The **unidirectional link search** uses the [RepoFromPaper](https://github.com/StankovskiA/RepoFromPaper) submodule to search for the implementation repository link in the paper. RepoFromPaper uses a SciBert Model to classify the paper's text as either a proposal sentence or not. The top 5 highest ranked sentences are then searched for a repository link. If no link is found in the initial search, a footnote/reference search is conducted. RepoFromPaper can either return a link or return an empty response if no link is found.
- The **bidirectional link search** intends to find paper-repo links where both the paper points to the repo and the repo (metadata) points back to the paper. The search may find zero, one, or multiple bidirectional links. 


#### **Analyze**

The `analyze` command processes the output of the `assess` command and generates summary statistics. It provides insights into the number of research papers analyzed, how many contain software links, the breakdown of unidirectional and bidirectional links, and other key metrics.

```bash
rsef analyze -h
Usage: rsef analyze [OPTIONS]

Options:
-i, --input <name> Path to RSEF assess JSON output [required]
-o, --output <path> Output Directory [default: output/output_analysis.json]
-h, --help Show this message and exit.
```


## RSEF Evaluation
Below we detail the evaluation methods and corpora used for RSEF

### **Unidirectional extraction**

Training corpus: [75 implementation sentences and ~2500 non-implementation sentences](https://doi.org/10.5281/zenodo.10701846) from 61 research papers sourced from [PapersWithCode](https://paperswithcode.com/). Evaluation was conducted using [150 research papers](https://doi.org/10.5281/zenodo.10980368) from Arxiv.org.

### **Bidirectional extraction**

Validated with a corpus of **154 papers and repositories**, containing various forms of bidirectional links (e.g., repository mentions in README files, citation files, etc.).

### **Performance Summary**

| Type of extraction |Train corpus | Eval. corpus | Precision | Recall | F1-Measure |
|---|--- |---|---|---|---|
| unidirectional |[Link](https://doi.org/10.5281/zenodo.10701846) | [Link](https://doi.org/10.5281/zenodo.10980368) | 0.94 | 0.95 | 0.94 |
| bidirectional | N/A| [Link](https://github.com/SoftwareUnderstanding/RSEF/blob/main/evaluation/bidirectional/corpus.tsv) | 1 | 0.91 | 0.95 |

## **Cite RSEF**

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

## **License**

This project is licensed under the [MIT License](LICENSE).
