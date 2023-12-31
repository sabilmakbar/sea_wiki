'''
Script on Generating Wikipedia Data that are dumped into https://dumps.wikimedia.org/
More info can be read on https://huggingface.co/datasets/wikipedia
-------------------
Check here to see available indexed data: https://dumps.wikimedia.org/backup-index.html
Also check here to see language meta from its code: https://meta.wikimedia.org/wiki/List_of_Wikipedias
'''

import os, gc
import logging
import argparse

from itertools import chain

import pandas as pd
from datasets import load_dataset

from sea_loader_batched.wiki_loader import Wikipedia


def set_logger():
    # Set up the logger
    logging.basicConfig(
        level=logging.INFO,  # Set the desired logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s [%(levelname)s]: %(message)s',  # Customize the log message format
        datefmt='%Y-%m-%d %H:%M:%S'  # Customize the date/time format
    )

    # Create a file handler to write logs into a file
    file_handler = logging.FileHandler('app.log')

    # Set the log level for the file handler
    file_handler.setLevel(logging.INFO) 

    # Create a formatter for the file handler (customize the log format for the file)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)

    logger = logging.getLogger("Wiki Dataset Generation")
    logger.addHandler(file_handler)

    return logger


#only executed if called directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--lang-id", help="Lang ID from Wikipedia Data to extract")

    parser.add_argument("--date-ver", help="Date of Wikipedia Data (YYYYMMDD) generation to extract")

    #default: all
    parser.add_argument("--split-extr", help="""Split extraction config for choosing
                        subsets of data to process. It follows python list slicing string args""",
            default=":")

    #default: all
    parser.add_argument("--force-rerun-split", help="""Flag to identify whether to check existing
                        splits or forcing to re-create it""",
            default=False)

    parser.add_argument("--save-dir-path", help="""Relative dir path of saved Wikipedia CSV data
                        to the `extract_raw_wiki_data.py` script dir""",
            default=os.path.dirname(os.path.abspath(__file__)))

    args = parser.parse_args()


    dset_name = "sea_loader_batched/wiki_loader.py"

    logger = set_logger()
    logger.info("Parsing arguments...")

    lang_id = args.lang_id
    date_ver = args.date_ver
    generated_split_extraction = args.split_extr
    force_rerun_split_generation = args.force_rerun_split
    save_dir = args.save_dir_path

    logger.info("Checking and creating the splits from Wikipedia Splitted Files...")
    lang, _splitted_files_dict = Wikipedia(language=lang_id, date=date_ver, subset_file_to_process=generated_split_extraction,
                    force_rerun_split=force_rerun_split_generation).check_and_create_splits()
    splitted_files = list(chain(*_splitted_files_dict.values()))

    logger.info("Loading the Wikipedia dataset in splitted fashion...")

    _total_split_data = len(splitted_files)
    for idx in range(len(splitted_files)):
        logger.info(f"Loading dataset on split {idx+1} out of {_total_split_data}...")
        df = load_dataset(dset_name, language=lang_id, date=date_ver, beam_runner='DirectRunner',
                            split="train", subset_file_to_process=idx).to_pandas()
        logger.info("Loading done!")
        logger.info(f"#Data collected: {df.shape[0]}")
        logger.info("Saving dataset raw form...")
        df.to_csv(f"{save_dir}/wiki_{lang_id}_{date_ver}_raw_dataset_splitted_idx_{idx+1}.csv.gz", index=False, compression="gzip")

        del df
        gc.collect()
