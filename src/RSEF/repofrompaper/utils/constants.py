# Regex
GITHUB_REGEX = r'(?:https?://(?:www\.)?)?github\.com\s*/\s*[a-zA-Z0-9_. -]+\s*/\s*[a-zA-Z0-9_.-]+'
CODE_GOOGLE_REGEX = r'(?:https?://(?:www\.)?)?code\.google\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+'
GITLAB_REGEX = r'(?:https?://(?:www\.)?)?gitlab\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+'
REPO_REGEXES = [GITHUB_REGEX, GITLAB_REGEX]

# Paths
MODEL_PATH = 'oeg/SciBERT-Repository-Proposal'
TOKENIZER_PATH = 'allenai/scibert_scivocab_uncased'
DOWNLOADED_PATH = '/downloaded_metadata.json'
PROCESSED_PATH = '/processed_metadata.json'
ASSES_PATH = '/url_search_output.json'

# Limits
FOOTNOTE_NUM_LIMIT = 30  # Numbers higher than this are not considered as footnotes
