## downloaded_metadata.json

The `downloaded_metadata.json` file contains an array of objects, each representing a downloaded paper with the following attributes:

| Attribute    | Type    | Description                                        | Example                                             |
|--------------|---------|----------------------------------------------------|-----------------------------------------------------|
| **title**    | String  | The title of the paper                             | `"Traffic Optimization Through Waiting Prediction"` |
| **doi**      | String  | The DOI of the paper                               | `"10.9781/ijimai.2023.12.001"`                      |
| **arxiv**    | String  | The ArXiv identifier of the paper, if available    | `"1906.03720"`                                      |
| **file_name**| String  | The name of the PDF file corresponding to the paper| `"ijimai.2023.12.001"`                              |
| **file_path**| String  | The path to the PDF file                           | `"PDFs\\ijimai.2023.12.001.pdf"`                    |

<br><br>

## processed_metadata.json

The `processed_metadata.json` file contains an array of objects, each representing a processed paper with the following attributes:

### Paper

| Attribute               | Type                      | Description                                                  | Example                                                    |
|-------------------------|---------------------------|--------------------------------------------------------------|------------------------------------------------------------|
| **doi**                 | String                    | The DOI of the paper                                         | `"10.1016/j.compbiomed.2019.05.002"`                       |
| **file_name**           | String                    | The name of the PDF file corresponding to the paper          | `"10-DOT-1016_j-DOT-compbiomed-DOT-2019-DOT-05.pdf"`       |
| **file_path**           | String                    | The path to the PDF file                                     | `"./PDFs/10-DOT-1016_j-DOT-compbiomed-DOT-2019-DOT-05.pdf"`|
| **title**               | String                    | The title of the paper                                       | `"Association of genomic subtypes of lower-grade gliomas"` |
| **arxiv**               | String                    | The ArXiv identifier of the paper, if available              | `"1906.03720"`                                             |
| **implementation_urls** | List of `Implementation`  | A list of `Implementation` objects associated with the paper | See Implementation table below.                            |

<br><br>

### Implementation

| Attribute              | Type                       | Description                                                    | Example                                                       |
|------------------------|----------------------------|----------------------------------------------------------------|---------------------------------------------------------------|
| **identifier**         | String                     | The URL of the implementation                                  | `"https://github.com/mateuszbuda/brain-segmentation"`         |
| **type**               | String                     | The type of URL                                                | `"zenodo"`                                                    |
| **paper_frequency**    | Integer                    | The number of times the URL appears in the paper               | `3`                                                           |
| **extraction_methods** | List of `ExtractionMethod` | A list of `ExtractionMethod` objects used to extract the URL   | See ExtractionMethod table below.                             |

<br><br>

### Extraction Method

| Attribute            | Type   | Description                                           | Values    | Example                           |
|----------------------|--------|-------------------------------------------------------|-----------|-----------------------------------|
| **type**             | String | The type of extraction method                         | regex     | `"regex"`                         |
| **location**         | String | The location in the document where the URL was found  |           | `"DESCRIPTION"`                   |
| **location_type**    | String | The type of location in the document                  |           | `"DOI"`                           |
| **source**           | String | The source used for extraction                        |           | `"SOMEF"`                         |
| **source_paragraph** | String | The paragraph in the source where the URL was found   |           | `"The code is available online."` |

<br><br>

## url_search_output.json

The `url_search_output.json` file contains an array of objects, each representing a paper after searching for unidirectional links, bidirectional links, or both.

The resulting JSON has the same structure as the `processed_metadata.json` but the `type` attribute of the Extraction Method can be "unidir" or "bidir", not only "regex". See table below:

### Extraction Method

| Attribute            | Type   | Description                                             | Included in             | Values                                                                      | Example                              |
|----------------------|--------|---------------------------------------------------------|-------------------------|-----------------------------------------------------------------------------|--------------------------------------|
| **type**             | String | The type of extraction method                           | regex, unidir and bidir | regex, unidir, bidir                                                        | `"regex"`                            |
| **location**         | String | The location in the document where the URL was found    | unidir, bidir           | ZENODO, DESCRIPTION, RELATED_PAPERS for bidir and the paper path for unidir | `"DESCRIPTION"`                      |
| **location_type**    | String | The type of location in the document                    | unidir, bidir           | DOI, ARXIV, CFF, BIBTEX, TEXT for bidir and PAPER for unidir                | `"DOI"`                              |
| **source**           | String | The source used for extraction                          | bidir                   | PAPER, SSKG, SOMEF                                                          | `"SOMEF"`                            |
| **source_paragraph** | String | The paragraph in the source where the URL was found     | unidir                  |                                                                             | `"The code is available online."`    |