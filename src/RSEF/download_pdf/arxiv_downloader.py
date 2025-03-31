import os.path

import requests
import logging
from ..utils.regex import str_to_arxivID

log = logging.getLogger(__name__)

# Deprecated but keep around to view old usage
# def filter_arxiv(file_path):
#     # Read the csv file
#     df = pd.read_csv(file_path)
#     # Filter the dataframe
#     df_arxiv = df[df['doi'].str.contains('arxiv') == True]
#     df_not_arxiv = df[df['doi'].str.contains('arxiv') == False]
#     # Save the filtered dataframe
#     df_not_arxiv.to_csv('dois_not_arxiv.csv', index=False)
#     df_arxiv = df_arxiv.drop(['name'], axis=1)
#     # Create new column with the arxiv id
#     df_arxiv['arxiv_id'] = df_arxiv['doi'] \
#         .str.split('/arxiv.').str[-1]
#     # lets create new urls for the arxiv, in the form of https://arxiv.org/pdf/{arxiv_id}.pdf
#     df_arxiv['arxiv_url'] = 'https://arxiv.org/pdf/' + df_arxiv['arxiv_id'] + '.pdf'
#
#     return df_arxiv['arxiv_url']


def download_pdf(url, output_dir):
    """
    @param url: arxiv url
    @param output_dir: path to output, existence checked by download_pipeline
    ------
    :returns path to the pdf file
    """
    if(url := convert_to_arxiv_url(input_string=url)) is None:
        return None
    try:
        r = requests.get(url)
        if r.status_code != 200:
            log.debug("Failed to download PDF from URL: %s (Status Code: %s)", url, r.status_code)
            return None
        output_path = os.path.join(output_dir, url.split('/')[-1])
        with open(output_path, 'wb') as f:
            f.write(r.content)
        return output_path
    except Exception as e:
        log.error("Issue when trying to download Arxiv PDF %s", str(e))
        return None


def convert_to_arxiv_url(input_string):
    """
    @Param input_string: possible ID to be converted to arxiv URL
    :returns String: arxiv URL or None
    """
    arxiv = str_to_arxivID(input_string)
    if arxiv is not None:
        arxiv_url = 'https://arxiv.org/pdf/' + arxiv.strip() + '.pdf'
        return arxiv_url
    return None

