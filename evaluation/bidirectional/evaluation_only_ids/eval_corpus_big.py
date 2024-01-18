import pandas as pd
import json
import re

ARXIV_REGEX = r'.*(\d{4}\.\d{4,5}).*'

def str_to_arxivID(string):
    try:
        match = re.search(ARXIV_REGEX, string)
        if match:
            return match.group(1)
        return None
    except:
        return None

def calculate_metrics(json_path, tsv_path, output_path):
    # Read Corpus TSV
    tsv_data = pd.read_csv(tsv_path, dtype=str, sep='\t')

    with open(json_path, 'r') as f:
        json_data = json.load(f)

    # Initialize counters
    TruePositive = 0
    TrueNegative = 0
    FalseNegative = 0
    FalsePositive = 0
    fails = {"FalseNeg": [], "FalsePos": []}

    for index, row in tsv_data.iterrows():
        corp_arxiv = str_to_arxivID(row['paper_arxiv_id'])
        if corp_arxiv is None:
            continue
        
        prediction = row['BiDirectional_ids'] == 'TRUE'  # Assuming the value in TSV is 'True' or 'False'
        if corp_arxiv == "2006.09044":
            print(prediction)
        # Check against JSON data
        test = json_data.keys()
        if corp_arxiv in test: # SSKG considers it bidirectional
            if prediction:
                TruePositive += 1
            else:
                FalsePositive += 1
                fails["FalsePos"].append(corp_arxiv)
        else: # SSKG does not consider it bidirectional
            if prediction:
                FalseNegative += 1
                fails["FalseNeg"].append(corp_arxiv)
            else:
                TrueNegative += 1

    # Calculate precision, recall, and f1 score
    precision = TruePositive / (TruePositive + FalsePositive) if (TruePositive + FalsePositive) > 0 else 0
    recall = TruePositive / (TruePositive + FalseNegative) if (TruePositive + FalseNegative) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Prepare result
    result = {
        "_failed Repos": fails,
        "f1_score": f1_score,
        "precision": precision,
        "recall": recall
    }

    # Write result to JSON file
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=4)

    return result

# Example usage
tsv_path = "../corpus.tsv"
json_file_path = "./bidir.json"
output_json_path = 'output_metrics.json'
calculate_metrics(json_file_path, tsv_path, output_json_path)
