# %%
'''
Script on Cleansing Wikipedia Data that has been extracted from extract_raw_wiki_data.py
'''
#core functionality modules
import os, gc
import logging
import argparse
import warnings

from functools import partial

#text preprocess modules
import re
import urllib
from xml.etree import ElementTree as ET

#dataset related modules
import numpy as np
import pandas as pd


### MODULES DEFINITION ###
#create custom type-checking of incoming ArgParse
def argparse_bool_check(value: str):
    #cast str with value like float into actual float
    try:
        value = float(value)
    #can't be parsed as float, keep as it is
    except ValueError:
        pass

    #cast float-like value (incl int) into str
    if isinstance(value, float) and int(value) == value:
        value = str(int(value))
    #raise ArgumentTypeError if the value isn't in string already
    else:
        if not isinstance(value, str):
            raise argparse.ArgumentTypeError(f"Not the correct value (args: {value})! Expected is cast-able to '1' or '0' or already in string. Please rectify!")
    #check for these combinations of values
    if value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif value.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Value Error! Not the correct value (args: {value})! Please rectify!")


def text_processing_args_checker(value: str):
    if value not in ["all", "text", "title", "neither"]:
        raise argparse.ArgumentTypeError(f"Value Error! Not the correct value (args: {value})! Please rectify!")
    else:
        return value


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


#wrapper fn of text-cleansing
def text_cleansing_wrapper(fn, exception_class_names = []):

    #ensure caught exception class names passed to decorator is a list (if provided)
    if not isinstance(exception_class_names, list):
        raise TypeError("Exception Class Name for Wrapper is not a list!")
    #ensure all values of caught exception class name list is a string
    if not all([isinstance(val, str) for val in exception_class_names]):
        raise ValueError("Found an element of Exception Class Name for Wrapper that is not a string!")

    #lowercase all exception class name
    exception_class_names = [val.lower() for val in exception_class_names]
    if len(exception_class_names) == 0:
        warnings.warn("The wrapper receives 0 `exception_class_names` to be warned! Will return the function value with its input!")

    def text_fn_wrapper(text: str, *args, **kwargs):
        try:
            return fn(text, *args, **kwargs)
        except Exception as e:
            _exc_name = type(e).__name__
            if _exc_name.lower() not in exception_class_names and len(exception_class_names)>0:
                raise Exception(f"Exception Occured of {_exc_name} in {fn.__name__}!") from e
            else:
                _followup_msg = "Returning the input as it is..."
                _text_warn = f"An exception of {_exc_name} occured in {fn.__name__}! {_followup_msg}"
                warnings.warn(_text_warn)
                return text

    return text_fn_wrapper


#create html tags cleanser of a given text
partial_decorator = partial(text_cleansing_wrapper, exception_class_names=["parseerror"])
@partial_decorator
def remove_html_tags(text: str):
    #extracted from "https://stackoverflow.com/a/9662410", w/ additional decorator of error handler
    return (''.join(ET.fromstring(text).itertext())).strip()


#create url decoder of text
@text_cleansing_wrapper
def decode_url(text: str):
    # return (urllib.parse.unquote(text)).encode('utf8', errors='ignore').decode().strip()
    return (urllib.parse.unquote(text)).strip()

#create encoder check of text
@text_cleansing_wrapper
def check_text_by_encoder(text: str, encoder: str="utf8"):
    return text.encode(encoder, errors='ignore').decode().strip()

#create excessive whitespace removal of text
@text_cleansing_wrapper
def remove_excessive_whitespace(text: str):
    return re.sub("(\s)(\s+)", r"\1", text).strip()

#create non-alphanumeric removal of text
@text_cleansing_wrapper
def remove_non_alphanumeric(text: str):
    return re.sub("[^a-z0-9\s]", "", text, flags=re.I).strip()

# def cleanse_wiki_text(text: str):
#     return remove_html_tags(decode_url_and_remove_non_ascii(text))

# def normalize_wiki_title(text: str):
#     return remove_non_alphanumeric(remove_excessive_whitespace(text.lower()))


def _text_normalizer_constructor(
        remove_non_alphanumeric_bool: bool, remove_excessive_whitespace_bool: bool,
        remove_html_tags_bool: bool, decode_url_bool: bool, encoder_check_bool: bool,
        encoder: str="utf8"):

    _lambda_fn_1 = partial(check_text_by_encoder, encoder=encoder) if encoder_check_bool else lambda x: x
    _lambda_fn_2 = lambda x: remove_non_alphanumeric(_lambda_fn_1(x)) if remove_non_alphanumeric_bool else _lambda_fn_1(x)
    _lambda_fn_3 = lambda x: remove_excessive_whitespace(_lambda_fn_2(x)) if remove_excessive_whitespace_bool else _lambda_fn_2(x)
    _lambda_fn_4 = lambda x: remove_html_tags(_lambda_fn_3(x)) if remove_html_tags_bool else _lambda_fn_3(x)
    _lambda_fn_5 = lambda x: decode_url(_lambda_fn_4(x)) if decode_url_bool else _lambda_fn_4(x)

    return _lambda_fn_5


def _args_to_text_constructor_fn(**kwargs):

    def _decode_options(opt: str):
        # return decoded options with format `text_opt`, `title_opt`
        # possible values are ["all", "text", "title", "neither"]
        if opt == "all":
            return True, True
        elif opt == "text":
            return True, False
        elif opt == "title":
            return False, True
        else:
            return False, False

    kwargs_title, kwargs_text = {}, {}

    kwargs_title["encoder"] = kwargs["text_encoder_choice_title"]
    kwargs_text["encoder"] = kwargs["text_encoder_choice_text"]

    for key, val in kwargs.items():
        if key not in [
            "remove_non_alphanumeric_option", "remove_excessive_whitespace_option",
            "remove_html_tags_option", "decode_url_option", "encoder_check_option"]:
            continue
        new_key = "_".join(key.split("_")[:-1]) + "_bool"
        text_opt_val, title_opt_val = _decode_options(val)
        kwargs_text[new_key], kwargs_title[new_key] = text_opt_val, title_opt_val

    return _text_normalizer_constructor(**kwargs_text), _text_normalizer_constructor(**kwargs_title)


def _text_processing_wrapper(text: str, _fn, mode: str="text"):
    if mode not in ["text", "title"]:
        raise ValueError(f"Provided `mode` isn't either 'text' or 'title'! Received: {mode}")
    return _fn(text.lower()) if mode=="title" else _fn(text)


### MAIN CODE ###
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--raw-csv-path", help="Relative location of csv file containing raw Wikipedia data")

    parser.add_argument("--drop-hard-dupl", help="""Flag whether to drop hard duplicates
                        (exact values of data of relevant text fields, Titles & Desc)""",
          default=True, type=argparse_bool_check)

    parser.add_argument("--drop-soft-dupl", help="""Flag whether to drop soft duplicates
                        (duplicates after cleansed and normalized relevant text fields, Titles & Desc)""",
          default=True, type=argparse_bool_check)

    parser.add_argument("--save-dir-path", help="""Relative dir path of saved Wikipedia CSV data
                        to the `dedup_raw_wiki_data.py` script dir""",
            default=os.path.dirname(os.path.abspath(__file__)))

    ### THE FOLLOWING ARGUMENTS ONLY TEMPORARILY ALTER THE TEXT DATA ONLY FOR SOFT-DEDUP CHECK ###
    ### THE INITIAL TEXT DATA WON'T BE OVERWRITTEN AFTER BEING PREPROCESSED ###
    ### UNLESS YOU ARE SPECIFYING IN ARGS `overwrite-initial-title-data` AND `overwrite-initial-text-data` ###

    ### ARGS TO OVERWRITTE INITIAL TEXT DATA WITH PROCESSED ONES ###
    parser.add_argument("--overwrite-initial-title-data", help="""Flag whether to overwrite title
                        init data w/ processed data (True) or keep it as it is (False)""",
          default=False, type=argparse_bool_check)

    parser.add_argument("--overwrite-initial-text-data", help="""Flag whether to overwrite text
                        init data w/ processed data (True) or keep it as it is (False)""",
          default=False, type=argparse_bool_check)

    ### INSTANTIATOR ARGS FOR CONSTRUCTING TEXT PROCESSING FN TO BE APPLIED ###
    parser.add_argument("--remove-non-alphanumeric-option", help="""Identifier which columns to be preprocessed
                        using `remove_non_alphanumeric` for soft duplicates detection
                        (Choices are "all", "text", "title", "neither")""",
          default="neither", type=text_processing_args_checker)

    parser.add_argument("--remove-excessive-whitespace-option", help="""Identifier which columns to be preprocessed
                        using `remove_excessive_whitespace` for soft duplicates detection
                        (Choices are "all", "text", "title", "neither")""",
          default="all", type=text_processing_args_checker)

    parser.add_argument("--remove-html-tags-option", help="""Identifier which columns to be preprocessed
                        using `remove_html_tags` for soft duplicates detection
                        (Choices are "all", "text", "title", "neither")""",
          default="all", type=text_processing_args_checker)

    parser.add_argument("--decode-url-option", help="""Identifier which columns to be preprocessed
                        using `decode_url` for soft duplicates detection
                        (Choices are "all", "text", "title", "neither")""",
          default="all", type=text_processing_args_checker)

    ### ARGS TO CHOOSE ENCODER CHECKING AND ITS CONFIG INITIALIZATION ###
    parser.add_argument("--encoder-check-option", help="""Identifier which columns to be preprocessed
                        using `check_text_by_encoder` for soft duplicates detection
                        (Choices are "all", "text", "title", "neither")""",
          default="all", type=text_processing_args_checker)

    parser.add_argument("--text-encoder-choice-title", help="""Identifier of title encoder type
                        to be applied into `check_text_by_encoder` for soft duplicates detection""",
          default="utf8", type=str)

    parser.add_argument("--text-encoder-choice-text", help="""Identifier of text encoder type
                        to be applied into `check_text_by_encoder` for soft duplicates detection""",
          default="utf8", type=str)


    _EXPECTED_COLNAMES = ["id", "url", "title", "text"]

    logger = set_logger()
    logger.info("Parsing arguments...")

    args = parser.parse_args()

    # class dotdict(dict):
    #     """dot.notation access to dictionary attributes"""
    #     __getattr__ = dict.get
    #     __setattr__ = dict.__setitem__
    #     __delattr__ = dict.__delitem__
    
    # args = dotdict({
    #     "raw_csv_path":"",
    #     "drop_hard_dupl": True,
    #     "drop_soft_dupl": True,
    #     "save_dir_path": os.path.dirname(os.path.abspath(__file__)),
    #     "overwrite_initial_title_data": False,
    #     "overwrite_initial_text_data": False,
    #     "remove_non_alphanumeric_option":"neither",
    #     "remove_excessive_whitespace_option": "neither",
    #     "remove_html_tags_option":"neither",
    #     "decode_url_option":"neither",
    #     "encoder_check_option":"all",
    #     "text_encoder_choice_title":"utf8",
    #     "text_encoder_choice_text":"utf8"
    # })

    _TEXT_PROCESSING_FN, _TITLE_PROCESSING_FN = _args_to_text_constructor_fn(
        remove_non_alphanumeric_option = args.remove_non_alphanumeric_option,
        remove_excessive_whitespace_option = args.remove_excessive_whitespace_option,
        remove_html_tags_option = args.remove_html_tags_option,
        decode_url_option = args.text_encoder_choice_title,
        encoder_check_option = args.encoder_check_option,
        text_encoder_choice_title = args.text_encoder_choice_title,
        text_encoder_choice_text = args.text_encoder_choice_text
    )

    raw_data_path = args.raw_csv_path
    drop_hard_dupl = args.drop_hard_dupl
    drop_soft_dupl = args.drop_soft_dupl
    save_dir = args.save_dir_path

    overwrite_initial_title_data = args.overwrite_initial_title_data
    overwrite_initial_text_data = args.overwrite_initial_text_data


    df = pd.read_csv(raw_data_path)
    if len(set(df.columns).difference(set(_EXPECTED_COLNAMES))) != 0 or len(set(_EXPECTED_COLNAMES).difference(set(df.columns))) != 0:
        raise ValueError(f"The data schema expected, consist of columns: {', '.join(df.columns.to_list())} doesn't match with expected column values of {', '.join(_EXPECTED_COLNAMES)}!")

    if (not drop_hard_dupl) and (not drop_soft_dupl):
        raise AssertionError("The script won't run with both `drop-hard-dupl` and `drop-soft-dupl` args turned off!")
    elif (not drop_hard_dupl):
        warnings.warn("The args of `drop_hard_dupl` isn't turned off! Possibly the data will contain one template value of Wikipedia (usually no contribution text!)")

    #will save id identifier colname first (popping first list val)
    id_colname = _EXPECTED_COLNAMES.pop(0)

    # if any of the data has duplicate values from columns checked (url, title, or text),
    # it means the data integrity is questionable
    # i.e. copied from other article or filled with template text
    # hence, we will delete those duplicated datasets

    #hard duplicate drop (drop all duplicate values that has exact same text on expected unique colnames)
    if drop_hard_dupl:

        for colname in _EXPECTED_COLNAMES:
            logger.info(f"Checking data integrity on column {colname} on removing hard-duplicate(s)...")
            dupl_text_df = df[df.duplicated(subset=colname,keep=False)]
            shape_of_dupl_data = dupl_text_df.shape[0]

            if shape_of_dupl_data > 0:
                logger.info(f"Found {shape_of_dupl_data} data duplicated! Will be dropped")
                df.drop_duplicates(subset=colname, keep=False, inplace=True)


        #check id/idx of the cleansed data, whether it has duplicate
        # (the duplication of id/idx should came from the very first extraction, not from the cleansing)

        if df[df.duplicated(subset=id_colname,keep=False)].shape[0] > 0:
            logger.info("Duplicated ID found! Re-assigning ID to the new ones based on `df.reset_index` method!")
            df[id_colname] = df.reset_index().index

    #soft duplicate drop (drop all except one duplicate values that has exact same text on expected unique colnames)
    #keep the data that has longest value of its raw form
    if drop_soft_dupl:

        idx_to_keep = set(df.index.to_list())
        #clean from text & title only, url isn't needed for this process
        _EXPECTED_COLNAMES.remove("url")

        for colname in _EXPECTED_COLNAMES:
            #Construct Text Cleanser Fn for soft-duplicate cleansing
            _PROCESSING_FN = _TEXT_PROCESSING_FN if colname == "text" else _TITLE_PROCESSING_FN
            text_processing_fn = partial(_text_processing_wrapper, _fn=_PROCESSING_FN, mode=colname)
            logger.info(f"Checking data integrity on column {colname} on removing soft-duplicate(s)...")
            _df = df.copy(deep=True)

            #Setting up DF cols as String so it can be text-processed
            _df = _df[[colname]]
            _df[colname] = _df[colname].astype("str")
            logger.info(f"Cleansing the data based on {colname}")

            #applying text processing
            _df[colname+"_raw_len"] = _df[colname].apply(len)
            _df[colname+"_cleansed"] = _df[colname].apply(lambda row_text: text_processing_fn(text=row_text))

            #overwrite its text data if set as true
            if overwrite_initial_title_data and colname == "title":
                df[colname] = _df[colname+"_cleansed"]
            elif overwrite_initial_text_data and colname == "text":
                df[colname] = _df[colname+"_cleansed"]

            #choose the data to keep by "ranking" it according to len of its raw text (greatest to keep)
            logger.info(f"Ranking and grouping the data based on {colname}")
            _df["rk"] = _df.groupby(colname+"_cleansed")[colname+"_raw_len"].rank(method="min", ascending=False)
            shape_of_dupl_data = _df[_df["rk"]>1].shape[0]

            if shape_of_dupl_data > 0:
                logger.info(f"Found {shape_of_dupl_data} data duplicated! Will be dropped")
                _idx_to_keep = _df[_df["rk"]==1].index.to_list()
                if len(_idx_to_keep)+shape_of_dupl_data != df.shape[0]:
                    raise AssertionError("Mismatch of data number!")
                idx_to_keep = idx_to_keep.intersection(set(_idx_to_keep))
            else:
                logger.info(f"No soft-duplicate found in colname {colname}. Continuing")

            del _df
            gc.collect()

        logger.info(f"The final data kept is {len(idx_to_keep)} from {df.shape[0]}")
        df = df.loc[list(idx_to_keep),:]

    logger.info("Saving dataset cleansed form...")
    #input path splitted by ("/") for the last entry should return filename
    #whereas the filename splitted by (".") except the last value should return the filename w/o ".csv" extension

    _override_suffix_identifier = ""
    if overwrite_initial_title_data or overwrite_initial_text_data:
        _override_suffix_identifier = "_overwritten"
        if overwrite_initial_text_data:
            _override_suffix_identifier = "_text"+_override_suffix_identifier
        if overwrite_initial_title_data:
            _override_suffix_identifier = "_title"+_override_suffix_identifier

    _save_file_name = ".".join(raw_data_path.split("/")[-1].split(".")[:-1]) + "_dedup_cleansed" + _override_suffix_identifier + ".csv"
    _save_file_name = _save_file_name.replace("_raw", "")
    df.to_csv(f"{save_dir}/{_save_file_name}", index=False)
