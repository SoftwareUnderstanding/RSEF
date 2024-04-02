#TODO find appropiate names
from . import __version__
import click
import os
import logging
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VALID_EXTENSIONS = ['.txt', '.json']


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    """
    RRRRRRRRR   SSSSSSSSS  EEEEEEEEE   FFFFFFFFF\n
    RRR   RRR  SSS    SSS  EEE         FFF\n
    RRR   RRR  SSS         EEE         FFF\n
    RRRRRRRRR  SSSSSSSSS   EEEEEEE     FFFFFFF\n
    RRR RRR         SSSS   EEE         FFF\n
    RRR  RRR  SSS    SSS   EEE         FFF\n
    RRR   RRR  SSSSSSSSS   EEEEEEEEE   FFF\n

    Research Software Extraction Framework (RSEF)\n
    Find and assess Research Software within Research papers.\n

    Usage:\n
    1. (assess)     Assess doi for unidirectionality or bidirectionality\n
    2. (download)   Download PDF (paper) from a doi or list\n
    3. (process)    Process downloaded pdf to find urls and abstract\n

    """
    pass

# #TODO
# @cli.command()
# def configure():
#     """This creates a ~/.soca/configure.ini file"""
#     #TODO defaults check
#     url = click.prompt("URL to database",default = "http://localhost:8086")
#     bucket = click.prompt("Bucket", default = "my-bucket")
#     org = click.prompt("Organisation",default = "org_name")
#     token = click.prompt("Token", default = "")
#     if len(token) == 0:
#         click.echo("No token given, please enter token or press enter")
#         token = click.prompt("Token", default = "")
#     try:
#         from soca.commands import create_config
#
#         create_config.create_config(url,bucket,token,org)
#         click.secho(f"Success", fg="green")
#     except Exception as e:
#         click.secho(f"Error: "+str(e),fg="red")
#         exit(1)

@cli.command()
@click.option('--input', '-i', required=True, help="DOI, path to .txt list of DOIs or path to processed_metadata.json",
              metavar='<name>')
@click.option('--output', '-o', default="output", show_default=True, help="Output csv file", metavar='<path>')
@click.option('--unidir', '-U', is_flag=True, default = False, help="Unidirectionality")
@click.option('--bidir', '-B', is_flag=True, default = False, help="Bidirectionality")
def assess(input, output, unidir, bidir):
    from .object_creator.pipeline import dois_txt_to_unidir_json, dois_txt_to_bidir_json, single_doi_pipeline_unidir, \
        single_doi_pipeline_bidir, papers_json_to_unidir_json, papers_json_to_bidir_json
    if unidir:
        if input.endswith(".txt") and os.path.exists(input):
            dois_txt_to_unidir_json(dois_txt=input,output_dir=output)
        if input.endswith(".json") and os.path.exists(input):
            papers_json_to_unidir_json(papers_json=input, output_dir=output)
            return
        else:
            repo_link = single_doi_pipeline_unidir(doi=input,output_dir=output)
            return repo_link

    elif bidir:
        if input.endswith(".txt") and os.path.exists(input):
            dois_txt_to_bidir_json(dois_txt=input,output_dir=output)
        if input.endswith(".json") and os.path.exists(input):
            papers_json_to_bidir_json(papers_json=input, output_dir=output)
        else:
            single_doi_pipeline_bidir(doi=input, output_dir=output)
            return
    else:
        print("Please select a directionality to measure")
        print("-U is to assess Uni-directionality")
        print("-B is to assess Bi-directionality")
    pass



@cli.command()
@click.option('--input', '-i', required=True, help="DOI or path to .txt list of DOIs", metavar='<name>')
@click.option('--output', '-o', default="./", show_default=True, help="Output Directory ", metavar='<path>')
def download(input, output):
    from .object_creator.create_downloadedObj import doi_to_downloadedJson, dois_txt_to_downloadedJson
    from .utils.regex import str_to_doiID
    if input.endswith(".txt") and os.path.exists(input):
        dois_txt_to_downloadedJson(dois_txt=input, output_dir=output)
    else:
        try:
            doi_to_downloadedJson(doi=input, output_dir=output)
        except Exception as e:
            print(e)
        return
@cli.command()
@click.option('--input', '-i', required=True, help="DOI, path to .txt list of DOIs or path to downloaded_metadata.json",
              metavar='<name>')
@click.option('--output','-o', default="./", show_default=True, help="Output Directory ", metavar='<path>')
def process(input, output):
    from .object_creator.downloaded_to_paperObj import dwnlddJson_to_paperJson, dwnldd_obj_to_paper_json
    from .object_creator.create_downloadedObj import pdf_to_downloaded_obj

    if os.path.isdir(input):
        _aux_pdfs_to_pp_json(input= input, output= output)
        return
    if input.endswith(".json") and os.path.exists(input):
        dwnlddJson_to_paperJson(input, output)
    if input.endswith(".pdf") and os.path.exists(input):
        #TODO
        dwnldd = pdf_to_downloaded_obj(pdf= input, output_dir= output)
        dwnldd_obj_to_paper_json(download_obj= dwnldd,output_dir= output)
        return
    else:
        print("Error")
        return


def _aux_pdfs_to_pp_json(input, output):
    from .object_creator.create_downloadedObj import pdf_to_downloaded_obj
    from .object_creator.downloaded_to_paperObj import dwnldd_obj_to_paper_dic
    import json
    try:
        result = {}
        for pdfFile in os.listdir(input):
            print(pdfFile)
            try:
                if os.path.isfile(pdfFile) and pdfFile.endswith(".pdf"):
                    dwnldd = pdf_to_downloaded_obj(pdf=pdfFile, output_dir=output)
                    pp_dic = dwnldd_obj_to_paper_dic(downloaded_obj=dwnldd)
                    try:
                        result.update(pp_dic)
                    except Exception as update_error:
                        logging.error(f"Error updating result with pp_dic: {str(update_error)}")
                        continue
                        print(pp_dic)
                        print(pdfFile)
            except Exception as file_error:
                logging.error(f"Error processing file: {str(file_error)}")
                continue
        output_path = output + "/" + "processed_metadata.json"
        with open(output_path, 'w+') as out_file:
            json.dump(result, out_file, sort_keys=True, indent=4,
                      ensure_ascii=False)
        return output_path
    except Exception as e:
        logging.error(f"an error occurred: {str(e)}")
        print(str(e))