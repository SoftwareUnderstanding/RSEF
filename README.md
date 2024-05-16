[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10306762.svg)](https://doi.org/10.5281/zenodo.10306762)
  
# Research Software Extraction Framework (RSEF)

  
## Introduction

This tool verifies the link between a scientific paper and a software repository. It accomplishes this by locating the URL of the software repository within the scientific paper. It then extracts the repository's metadata to find any URLs associated with scientific papers and checks if they lead back to the original paper. If a bidirectional link is established, it marks it as "bidirectional".

  

There is also a "unidirectional" metric, which finds a repository url and see's within the repository if the paper is named.

## Dependencies

- Python 3.9

- Java 8 or above (please see [Tika requirements](https://pypi.org/project/tika/))

## Installation

Install the required dependencies by running:

```

pip install -e .

```

Highly recommended steps:

```text

somef configure

```

You will be asked to provide:

* A GitHub authentication token [**optional, leave blank if not used**], which SOMEF uses to retrieve metadata from GitHub. If you don't include an authentication token, you can still use SOMEF. However, you may be limited to a series of requests per hour. For more information, see [https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)

* The path to the trained classifiers (pickle files). If you have your own classifiers, you can provide them here. Otherwise, you can leave it blank

  

## Usage

```text

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
3. (process)  Process downloaded pdf to find urls and abstract

Options:
--version Show the version and exit.
-h, --help  Show this message and exit.

Commands:
	assess
	download
	process
 
```

### Download

The download command allows for a user to download the pdf with its metadata given an Identifier: ArXiv or DOI.  Alongside the PDFs folder there will be a `download_metadata.json` which will have the Title, DOI, ArXiv and filename/filepath for each paper downloaded.
```
rsef download -h 
Usage: rsef download [OPTIONS]

Options:

-i, --input <name> DOI or path to .txt list of DOIs  [required]

-o, --output <path>  Output Directory [default: ./]

-h, --help Show this message and exit.
```

### Processed

The process command allows to extract the abstract and github and zenodo urls from a paper or a list of papers. This command accepts different inputs:
1. A path to downloaded_metadata.json file

2. A path to results.json file, obtained by executing 
doiExtractor tool (https://github.com/oeg-upm/DOI-Extractor-OEG)

3. A path to a .pdf file 

4. A path to a folder fith PDFs

The output of the execution  is saved in a json named ```processed_metadata.json```. In addition when passing the path to results.json file, this command will download the papers in the PDFs folder and create a `download_metadata.json`.
```
rsef process -h
Usage: rsef process [OPTIONS]

Options:

-i, --input <path>  path to downloaded_metadata.json, to a PDF or to a folder with PDFs

-j --json <path> path to results.json, obtained by executing doiExtractor tool

-o, --output <path>  Output Directory [default: ./]

-h, --help Show this message and exit.
```

### Assess

The assess command allows for a user to determine whether a given Identifier, in this case ArXiv or DOI,  is bidirectional or not.

The command allows for the user to input a single DOI/ArXiv, a list of identifiers given as a ```.txt```, or a ```processed_metadata.json```. The resulting information after executing the command will be saved in ```url_search_output.json```.


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
## Structure


The src/RSEF is divided into the following directories:

1. Download_pdf

2. Metadata

3. Extraction

4. Object_creator

5. RepoFromPaper 

6. Modelling

7. Prediction

8. Utils


### Download_pdf

Pertains to all the downloading of pdfs.

Downloaded_obj is a representation of downloaded papers which have not been processed yet. 

Contains:

	- Title 
	- DOI
	- ArXiv
	- file_path
	- file_name

These objects are normally saved into a `downloaded_metadata.json`

  

### Metadata


Encompasses all petitions to OpenAlex and other api's for fetching the paper's metadata or general requests.

MetadataObj contains the metadata from  OpenAlex: doi, arxiv and its title.

### Extraction



Tika scripts to open a pdf and extract its urls are also found witin this module.

PaperObj is created once the downloadedObj's pdf has been processed to locate all its urls. 
Contains: 
- DOI
-  arXiv
- Abstract
- Title
- File_path
- File_name
- URLs

Finally, the necessary functions downloading a repository and extracting its metadata with SOMEF

  
### Object Creator

This is the pipeline broken down into its main parts. Please look at [pipeline.py](./object_creator/pipeline.py) to view the execution process.

  
### RepoFromPaper

Contains the code for the RepoFromPaper (RFP) package. RFP uses a combination of natural language processing and heuristics to identify and extract the repository links mentioned in a proposal manner from a paper.

As input it receives the local file path of the paper and returns the repository URL if found.

### Modelling

Contains all assessment of bi-directionality and uni-directionality.

Receives a paperObj and a repository_metadata json.

  

### Prediction

For assessment of the program against its corpus. The corpus can be found within [corpus.csv](./predicition/corpus.csv) and the f1 score obtained bidirectional:  [corpus_eval_bidir.json](./predicition/corpus_eval_bidir.json) and the same for the unidirectional (_unidir)


## Tests

Tests can be found in the `./tests` folder

## Evaluation

This software has been evaluate it with a corpus created expressly.

This corpus, composed by 154 papers-repositories, includes  several types of bi-directionality paper-repository links (e.g., repositories including just the title, Arxiv URLs or DOIs in the README file, using citation files, repositories in different code platforms, etc.)

Two annotators were selected to manually annotate the presence of bi-directionality. In case of two different annotations in the corpus, a third annotator decided the final value.

This corpus, in TSV format, can be found in the [evaluation/bidirectional folder](https://github.com/SoftwareUnderstanding/RSEF/blob/main/evaluation/bidirectional/corpus.tsv).

The RAW version of the corpus can be found [here](https://github.com/SoftwareUnderstanding/RSEF/blob/main/evaluation/bidirectional/corpus_arxiv_bidirectional_12_23.xlsx).

In case you want to run the evaluation, you will have to use the script presents in the evaluation_only_ids folder.
  
```text
python eval_corpus_big.py
```

A file name **output_metrics.json** will be generated with the results of the evaluation. You can find metrics such as precision, recall, f1-score and the list of false negatives.

The results of the evaluation using our corpus are:
**precision:** 1.0
**recall:** 0.918918918918919
**f1-score:** 0.9577464788732395

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

## License

This project is licensed under the [MIT License](LICENSE).  
