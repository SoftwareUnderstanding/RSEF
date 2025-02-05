from torch.nn.functional import softmax
from heapq import heappush, heappop
from . import model, tokenizer
from typing import List
import re

def get_top_sentences(sentences: List[str], top_k: int = 5) -> List[str]:
    """'Find the top k sentences from the given list of sentences using the model."""
    top_sentences = []  # Using a min heap to efficiently keep track of top sentences

    for sentence in sentences:
        # Remove sentences with more than 1 link
        if len(re.findall(r'(http?://\S+)', sentence)) > 1:
            continue

        try:
            inputs = tokenizer(sentence, return_tensors="pt")
            outputs = model(**inputs)
            logits = outputs.logits
            scores = softmax(logits, dim=1).detach().numpy()[0]
            positive_score = scores[1]

            # Keep sentences with a score higher than 0.9
            if positive_score < 0.9:
                continue
            
            # If the heap is not full or the current sentence has a higher score than the smallest score in the heap
            if len(top_sentences) < top_k or positive_score > top_sentences[0][0]:
                heappush(top_sentences, (positive_score, sentence))

                # If the heap size exceeds top_k, remove the smallest element
                if len(top_sentences) > top_k:
                    heappop(top_sentences)
        except Exception as e:
            continue

    # Extract sentences from the heap in descending order of score
    sorted_sentences = [sentence for _, sentence in sorted(
        top_sentences, key=lambda x: x[0], reverse=True)]

    return sorted_sentences
