from transformers import RobertaForSequenceClassification, RobertaTokenizer
from RSEF.repofrompaper.utils.constants import MODEL_PATH, TOKENIZER_PATH

# Model Loading
model = RobertaForSequenceClassification.from_pretrained(MODEL_PATH)
tokenizer = RobertaTokenizer.from_pretrained(TOKENIZER_PATH)

# Export the model and tokenizer
__all__ = ["model", "tokenizer"]