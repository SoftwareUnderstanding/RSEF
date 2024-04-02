from transformers import AutoTokenizer, AutoModelForSequenceClassification
from .utils.constants import MODEL_PATH, TOKENIZER_PATH

# Model Loading
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

# Export the model and tokenizer
__all__ = ["model", "tokenizer"]