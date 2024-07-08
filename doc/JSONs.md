# RSEF JSON Result specification
Below we detail the structure of the JSON file produced by RSEF

## downloaded_metadata.json

File generated after using the `download` command. The `downloaded_metadata.json` file contains an array of objects, each representing a downloaded paper with the following attributes:

| Attribute    | Type    | Description                                        | Example                                             |
|--------------|---------|----------------------------------------------------|-----------------------------------------------------|
| **title**    | String  | The title of the paper                             | `"Traffic Optimization Through Waiting Prediction"` |
| **doi**      | String  | The DOI of the paper                               | `"10.9781/ijimai.2023.12.001"`                      |
| **arxiv**    | String  | The ArXiv identifier of the paper, if available    | `"1906.03720"`                                      |
| **file_name**| String  | The name of the PDF file corresponding to the paper| `"ijimai.2023.12.001"`                              |
| **file_path**| String  | The path to the PDF file                           | `"PDFs\\ijimai.2023.12.001.pdf"`                    |

<br>

## processed_metadata.json
File obtained after using the `assess` command. 
The `processed_metadata.json` file contains an array of objects, each representing a processed paper with its corresponding implementation. The file has the following attributes:

### Paper

| Attribute               | Type                      | Description                                                  | Example                                                    |
|-------------------------|---------------------------|--------------------------------------------------------------|------------------------------------------------------------|
| **doi**                 | String                    | DOI of the assessed paper                                         | `"10.1016/j.compbiomed.2019.05.002"`                       |
| **file_name**           | String                    | Name of the PDF file corresponding to the paper          | `"10-DOT-1016_j-DOT-compbiomed-DOT-2019-DOT-05.pdf"`       |
| **file_path**           | String                    | Path to the downloaded PDF file                                     | `"./PDFs/10-DOT-1016_j-DOT-compbiomed-DOT-2019-DOT-05.pdf"`|
| **title**               | String                    | Title of the paper                                       | `"Association of genomic subtypes of lower-grade gliomas"` |
| **arxiv**               | String                    | ArXiv identifier of the paper, if available              | `"1906.03720"`                                             |
| **implementation_urls** | List of `Implementation`  | A list of `Implementation`s  associated with the paper | See Implementation table below.                            |

<br>

### Implementation

| Attribute              | Type                       | Description                                                    | Example                                                       |
|------------------------|----------------------------|----------------------------------------------------------------|---------------------------------------------------------------|
| **identifier**         | String                     | URL of the implementation                                  | `"https://github.com/mateuszbuda/brain-segmentation"`         |
| **type**               | String                     | Type of URL (e.g., zenodo, github, etc.)                                               | `"zenodo"`                                                    |
| **paper_frequency**    | Integer                    | The number of times the URL appears in the paper               | `3`                                                           |
| **extraction_methods** | List of `ExtractionMethod` | A list of `ExtractionMethod` objects used to extract the URL   | See ExtractionMethod table below.                             |

<br>

### Extraction Method

| Attribute            | Type   | Description                                             | Extraction technique            | Values                                                                      | Example                              |
|----------------------|--------|---------------------------------------------------------|-------------------------|-----------------------------------------------------------------------------|--------------------------------------|
| **type**             | String | The type of extraction method                           | unidir, bidir | `unidir`, `bidir`                                                        | `"unidir"`                            |
| **location**         | String | Location in the document where the URL was found    | unidir, bidir           | **unidir:** paper path.<br/>**bidir:** ZENODO, TITLE DESCRIPTION, RELATED_PAPERS (all sections in the README file) | `"DESCRIPTION"`                      |
| **location_type**    | String | The type of location in the document                    | unidir, bidir           | **unidir:** PAPER, <br/>**bidir:** DOI, ARXIV, CFF, BIBTEX, TEXT                | `"DOI"`                              |
| **source**           | String | The source used for extraction                          | unidir, bidir                   | PAPER, RSEF, SOMEF                                                          | `"SOMEF"`                            |
| **source_paragraph** | String | The paragraph in the source where the URL was found     | unidir                  |                                                                             | `"The code is available online."`    |

#### Location types
```"PAPER"```: the location is in the assessed paper (coupled with `source_parargraph`)

```"DOI"```: There was a bidirectional match from a file in the analyzed code repository against the Digital Object Identifier of the paper. 

```"ARXIV"```: There was a bidirectional match from a file in the analyzed code repository against the Arxiv id of the paper. 

```"CFF"```There was a bidirectional match from the Citation File Format of the analyzed code repository against the paper (through its title or DOI). 

```"BIBTEX"```There was a bidirectional match from the Bibtext snippet in the analyzed code repository against the paper (through its title or DOI). 

```"TEXT"```There was a bidirectional match from the README of the analyzed code repository against the paper (through its title or DOI). 

#### Sources:
```"PAPER"``` is present in unidirectional relationships and means that the url has been found in the paper's PDF.

```"RSEF"```means that RSEF has checked that a paper has a record in Zenodo, and that the paper's DOI, Arxivid or title is mentioned in the Zenodo record. This is only for bidirectional relationships.

```"SOMEF"```means that for a GitHub repository found in the paper, the repository has been examined using SOMEF to search for citations or references to the paper. The analysis found a relationship between the paper and the repository, confirming a bidirectional relationship. This is only for bidirectional relationships.
<br>

## example.json

The `example.json` file contains an array of objects, each representing the RSEF output of a paper after searching for unidirectional and bidirectional links.
