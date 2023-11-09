import os
import argparse
import logging

import pandas as pd


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

    parser.add_argument("--load-dir-path", help="""Relative load dir path of saved batch Wikipedia CSV data
                    to the `concat_data.py` script dir""",
        default=os.path.dirname(os.path.abspath(__file__)))

    parser.add_argument("--save-dir-path", help="""Relative save dir path of concatted Wikipedia CSV data
                    to the `concat_data.py` script dir""",
        default=os.path.dirname(os.path.abspath(__file__)))

    args = parser.parse_args()


    logger = set_logger()
    logger.info("Parsing arguments...")

    load_dir = args.load_dir_path
    save_dir = args.save_dir_path

    csv_list_files = [os.path.join(load_dir, _filename) for _filename in os.listdir(load_dir) if _filename.endswith(".csv")]

    for idx, path in enumerate(csv_list_files):
        logger.info(f"Processinng data {idx+1} out of {len(csv_list_files)}")
        if idx == 0:
            df = pd.read_csv(path)
        else:
            df = pd.concat([df, pd.read_csv(path)], ignore_index=True)
    
    logger.info("Loading done!")
    logger.info(f"#Data collected: {df.shape[0]}")
    logger.info("Saving dataset raw form after concatted...")
    df.to_csv(f"{save_dir}.csv", index=False)
