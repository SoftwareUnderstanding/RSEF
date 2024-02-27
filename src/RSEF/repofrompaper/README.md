# RepoFromPaper

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Description

This package is a tool to automatically detect and extract proposed repository links from academic papers. It uses a combination of natural language processing and heuristics to identify and extract the repository links mentioned in a proposal manner from a paper. The tool is designed to be used by researchers and developers who want to quickly find the code associated with a paper.

## Table of Contents

- [RepoFromPaper](#repofrompaper)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

## Installation

The package has only three dependencies which are specified in the setup.py file. To install the package, you can use the following command:

```pip install .```

## Usage

The usage of the package is very simple as it only has one main function. The function takes a string as input and returns a list of best matched sentences and the repository link if found else an empty string. Here is an example of how to use the package. 

The name of the function is `extract_repo_links_from_pdf` and it takes the local path to the PDF as input. Here is an example of how to use the package.

```
from RSEF.repofrompaper.rfp.main import extract_repo_links_from_pdf

pdf_path = "path/to/pdf"
repo_links = extract_repo_links_from_pdf(pdf_path)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. If you have any questions, feel free to contact us.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you have any questions or suggestions, feel free to contact me at [a.stankovski@alumnos.upm.es](mailto:a.stankovski@alumnos.upm.es).
