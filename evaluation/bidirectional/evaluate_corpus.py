import csv
import json
#from oldPipeline import pipeline_bidir
import pandas as pd


def evalutate_corpus():
    TruePositive = 0
    TrueNegative = 0
    FalseNegative = 0
    FalsePositive = 0

    fails = {"FalseNeg": [], "FalsePos":[] }
    csv_file = "../corpus.csv"
    json_bidirs = "./bidir.json"
    csv = pd.read_csv(csv_file)
    print(csv)
    with open(json_bidirs) as json_file:
        dict_bidirs = json.load(json_file)

    for index, row in csv.iterrows():
        doi = row['DOI/arxiv_in_github']
        if doi in dict_bidirs:
            prediction = row.get("biDirectional")
            if prediction:
                TruePositive += 1
            else:
                FalsePositive += 1
                fails["FalsePos"].append(doi)
        else:
            prediction = row.get("biDirectional")
            if not prediction:
                TrueNegative += 1
            else:
                FalseNegative += 1
                fails["FalseNeg"].append(doi)
    precision = TruePositive / (TruePositive + FalsePositive)
    recall = TruePositive / (TruePositive + FalseNegative)
    f1_score = 2*((precision * recall)/(precision + recall))

    result = {"precision": precision, "recall": recall, "f1_score": f1_score, "_failed Repos": fails}
    return result

def evalutate_corpus():
    TruePositive = 0
    TrueNegative = 0
    FalseNegative = 0
    FalsePositive = 0

    fails = {"FalseNeg": [], "FalsePos":[] }
    csv_file = "../corpus.csv"
    json_bidirs = "./bidir.json"
    csv = pd.read_csv(csv_file)
    print(csv)
    with open(json_bidirs) as json_file:
        dict_bidirs = json.load(json_file)

    for index, row in csv.iterrows():
        doi = row['DOI_oa']
        if doi in dict_bidirs:
            prediction = row.get("biDirectional")
            if prediction:
                TruePositive += 1
            else:
                FalsePositive += 1
                fails["FalsePos"].append(doi)
        else:
            prediction = row.get("biDirectional")
            if not prediction:
                TrueNegative += 1
            else:
                FalseNegative += 1
                fails["FalseNeg"].append(doi)
    precision = TruePositive / (TruePositive + FalsePositive)
    recall = TruePositive / (TruePositive + FalseNegative)
    f1_score = 2*(( precision* recall)/(precision + recall))

    result = {"precision": precision, "recall": recall, "f1_score": f1_score, "_failed Repos": fails}
    return result


def evalutate_corpus_uni():
    TruePositive = 0
    TrueNegative = 0
    FalseNegative = 0
    FalsePositive = 0

    fails = {"FalseNeg": [], "FalsePos":[] }
    csv_file = "corpus_unidir.csv"
    json_bidirs = "./unidir.json"
    csv = pd.read_csv(csv_file)
    print(csv)
    with open(json_bidirs) as json_file:
        dict_bidirs = json.load(json_file)

    for index, row in csv.iterrows():
        doi = row['DOI']
        if doi in dict_bidirs:
            prediction = row.get("uniDir")
            if prediction:
                TruePositive += 1
            else:
                FalsePositive += 1
                fails["FalsePos"].append(doi)
        else:
            prediction = row.get("uniDir")
            if not prediction:
                TrueNegative += 1
            else:
                FalseNegative += 1
                fails["FalseNeg"].append(doi)
    precision = TruePositive / (TruePositive + FalsePositive)
    recall = TruePositive / (TruePositive + FalseNegative)
    f1_score = 2*(( precision* recall)/(precision + recall))

    result = {"precision": precision, "recall": recall, "f1_score": f1_score, "_failed Repos": fails}
    return result
def corpus_result_json(output_folder):
    result = evalutate_corpus()
    with open(output_folder + "/" + "corpus_eval_bidir.json", 'w+') as out_file:
        json.dump(result, out_file, sort_keys=True, indent=4,
                      ensure_ascii=False)

def corpus_uni_result_json(output_folder):
    result = evalutate_corpus_uni()
    with open(output_folder + "/" + "corpus_eval_uni.json", 'w+') as out_file:
        json.dump(result, out_file, sort_keys=True, indent=4,
                      ensure_ascii=False)


corpus_uni_result_json('./')

corpus_result_json('./')
