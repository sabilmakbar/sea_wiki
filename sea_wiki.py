"""The Southeast Asia Lan Wiki Loader"""

import os
import re

from functools import reduce

import numpy as np
import pandas as pd

import datasets


_CITATIONS = """\
@ONLINE{wikidump,
    author = "Wikimedia Foundation",
    title  = "Wikimedia Downloads",
    url    = "https://dumps.wikimedia.org"}

@ONLINE{wikipedia-hf,
    title  = "Huggingface Wikipedia Dataset",
    url    = "https://huggingface.co/datasets/wikipedia"}"""

_REPO_URL = "https://huggingface.co/datasets/sabilmakbar/sea_wiki"

_LICENSE = (
    "This work is licensed under the Creative Commons Attribution-ShareAlike "
    "3.0 Unported License. To view a copy of this license, visit "
    "http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to "
    "Creative Commons, PO Box 1866, Mountain View, CA 94042, USA."
)


_SEA_WIKI_RAW_DESCRIPTION = """\
Southeast Asia Wikipedia Data Repository contains Wikipedia Data from Wikipedia HF that focuses
on extraction in all available Languanges and Local Languages across South East Asia, which some of them
are considered as low-resource languages or extremely low-resource languages"""

_SEA_WIKI_DEDUP_DESCRIPTION = """\
This is a derivative of South East Asia Wikipedia Data Repository which is already pre-processed
by identifying and dropping duplicates to prevent boilerplate texts occuring in dataset"""

_AVAILABLE_DUMP_VERSION_DATE = ["20231101"]

# map from alpha-3 country codes to ISO-639 3 lang codes
# alpha-3 codes: https://www.iban.com/country-codes
# ISO-639 codes: https://iso639-3.sil.org/code_tables/639/data
_COUNTRY_TO_LANG_MAPPER = {
    "brn": ["ms"],
    "idn": ["ace", "ban", "bjn", "bug", "gor", "id", "jv", "mad", "map-bms", "min", "ms", "nia", "su", "tet"],
    "khm": ["km"],
    "lao": ["lo"],
    "mmr": ["my", "shn", "mnw"],
    "mys": ["ms", "ta"],
    #"ceb" lang is available, but not supported yet due to size
    "phl": ["war", "tl", "ilo", "bcl", "pam", "cbk-zam", "pag", "ceb"],
    "sgp": ["ms", "ta"],
    "tha": ["th", "mnw", "shn"],
    "tls": ["tet"],
    "vnm": ["vi"]}

_AVAILABLE_DUMP_LANGUAGES = reduce(np.union1d, list(_COUNTRY_TO_LANG_MAPPER.values()))

_LATEST_DUMP_VERSION_DATE = sorted(_AVAILABLE_DUMP_VERSION_DATE)[-1]


def _construct_dset_url_from_dset_version_and_lang(date_ver: str, lang: str, mode: str):
    _mode_to_folder_mapper = {"dedup": "sea_wiki_dedup_data", "raw": "sea_wiki_raw_data"}
    _mode_to_file_suffix_mapper = {"dedup": "dataset_dedup_cleansed.csv", "raw": "raw_dataset.csv"}

    return os.path.join(_mode_to_folder_mapper[mode], f"wiki_{lang}_{date_ver}_{_mode_to_file_suffix_mapper[mode]}")


class SEAWikiConfig(datasets.BuilderConfig):
    """BuilderConfig for SEAWiki."""

    def __init__(self, description: str=None, features: list=['url', 'title', 'text'],
                 data_url: str=None, date_stamp: str=_LATEST_DUMP_VERSION_DATE, country: str=None,
                 lang: str=None, mode = "dedup", **kwargs):
        """BuilderConfig for SEAWiki.

        Args:
          description: `string`, description of dataset
          features: `list[string]`, list of the features that will appear in the
            feature dict. Should not include "label" if it's a supervised.
          data_url: `string`, url to download the data.
          date_stamp: `string`, wikidump date_stamp for data available in repo.
          lang: `string`, language to be loaded.
          **kwargs: keyword arguments forwarded to super.
        """
        # validate configs
        if mode not in ["dedup", "raw"]:
            raise ValueError(f"Error occured! Expected values are 'dedup' or 'raw' for arg `mode`, received {mode}!")

        if ((lang is None and country is None) or date_stamp is None) and data_url is None:
            raise ValueError("Expected `data_url` is provided or both `date_stamp` and `lang` or `country` are provided!")

        _mode_to_desc_mapper = {"dedup": _SEA_WIKI_DEDUP_DESCRIPTION, "raw": _SEA_WIKI_RAW_DESCRIPTION}

        if date_stamp is not None and date_stamp not in _AVAILABLE_DUMP_VERSION_DATE:
            raise ValueError("Provided `date_stamp` dataset versioning doesn't match! Please re-check")

        if lang is not None and lang not in _AVAILABLE_DUMP_LANGUAGES:
            raise ValueError("Provided `lang` doesn't match! Please re-check")
        
        if country is not None and country not in _COUNTRY_TO_LANG_MAPPER.keys() and lang is None:
            raise ValueError("Provided `country` doesn't match! Please re-check")

        super(SEAWikiConfig, self).__init__(**kwargs)
        self.features = features
        self.lang = lang
        self.country = country

        # prioritize kwargs data_url
        if data_url is not None:
            self.data_url = data_url
        # prioritize lang provided over country
        elif lang is not None:
            self.data_url = _construct_dset_url_from_dset_version_and_lang(date_ver=date_stamp, lang=lang, mode=mode)
        # if only country provided, create dict of langs
        elif country is not None:
            self.data_url = {lang: _construct_dset_url_from_dset_version_and_lang(date_ver=date_stamp, lang=lang, mode=mode) for lang in _COUNTRY_TO_LANG_MAPPER[country]}

        # auto-construct desc if not provided
        if description is None:
            self.description = _mode_to_desc_mapper[mode] + "\n" + f"Extracted from file path {self.data_url}"

        #define citations & info URL internally in config class
        self.citation = _CITATIONS
        self.url = _REPO_URL


class SEAWiki(datasets.GeneratorBasedBuilder):
    """The SEAWiki Dataset."""

    # if name isn't provided, will create a dataset of all languages
    DEFAULT_CONFIG_NAME = "seawiki_dedup_all"
    BUILDER_CONFIG_CLASS = SEAWikiConfig

    # construct data-url with countries a list of spoken langs as value
    _newest_data_raw_all_langs = [_construct_dset_url_from_dset_version_and_lang(
        date_ver=_LATEST_DUMP_VERSION_DATE, lang=lang, mode="raw") for lang in _AVAILABLE_DUMP_LANGUAGES]
    _newest_data_dedup_all_langs = [_construct_dset_url_from_dset_version_and_lang(
        date_ver=_LATEST_DUMP_VERSION_DATE, lang=lang, mode="dedup") for lang in _AVAILABLE_DUMP_LANGUAGES]

    # construct data-url with countries as key-dict, being country code as key and list of spoken langs as value
    _newest_data_raw_with_countries_all_langs = {
        country: [_construct_dset_url_from_dset_version_and_lang(date_ver=_LATEST_DUMP_VERSION_DATE, lang=lang, mode="raw") for lang in lang_list]
        for country, lang_list in _COUNTRY_TO_LANG_MAPPER.items()}
    _newest_data_dedup_with_countries_all_langs = {
        country: [_construct_dset_url_from_dset_version_and_lang(date_ver=_LATEST_DUMP_VERSION_DATE, lang=lang, mode="dedup") for lang in lang_list]
        for country, lang_list in _COUNTRY_TO_LANG_MAPPER.items()}

    BUILDER_CONFIGS = [
        SEAWikiConfig(
            name="seawiki_all",
            description=_SEA_WIKI_RAW_DESCRIPTION,
            data_url=_newest_data_raw_all_langs
        ),
        SEAWikiConfig(
            name="seawiki_dedup_all",
            description=_SEA_WIKI_DEDUP_DESCRIPTION,
            data_url=_newest_data_dedup_all_langs
        ),
        SEAWikiConfig(
            name="seawiki_with_countries_all",
            description=_SEA_WIKI_RAW_DESCRIPTION,
            data_url=_newest_data_raw_with_countries_all_langs
        ),
        SEAWikiConfig(
            name="seawiki_with_countries_dedup_all",
            description=_SEA_WIKI_DEDUP_DESCRIPTION,
            data_url=_newest_data_dedup_with_countries_all_langs
        ),
    ]


    def _info(self):
        features = {feature: datasets.Value("string") for feature in self.config.features}

        return datasets.DatasetInfo(
            description = self.config.description,
            features = datasets.Features(features),
            homepage = self.config.url,
            citation = self.config.citation,
            license=_LICENSE)


    @staticmethod
    def _get_lang_name_from_data_url(data_url: str):
        # lang code occurred after "wiki_" and before date versioning (using 8len date)
        _list_folder_sep = data_url.split("/")[-1].split("_")
        _min_pos = min([pos for pos, data in enumerate(_list_folder_sep) if bool(re.search("\d{8}", data))])
        return re.sub("[^\w\.]", "_", "_".join(_list_folder_sep[1:_min_pos]))


    def _split_generators(self, dl_manager):

        # handle cases of config "seawiki_all", "seawiki_dedup_all", and custom config where only country is provided (take all langs in a country)
        if self.config.name in ("seawiki_all", "seawiki_dedup_all") or (self.config.country is not None and self.config.lang is None):
            file_dict = {self._get_lang_name_from_data_url(file): file for file in self.config.data_url}
            dl_dir = dl_manager.download_and_extract(file_dict)

            return [
                datasets.SplitGenerator(
                    name=datasets.Split(split_name),
                    gen_kwargs={
                        "data_file": file_name
                    }
                )
            for split_name, file_name in dl_dir.items()]

        # handle cases of config "seawiki_with_countries_all", "seawiki_with_countries_dedup_all"
        elif self.config.name in ("seawiki_with_countries_all", "seawiki_with_countries_dedup_all"):
            file_dict = {}

            for country, file_list in self.config.data_url.items():
                for file in file_list:
                    file_dict[country + "_" + self._get_lang_name_from_data_url(file)] = file

            dl_dir = dl_manager.download_and_extract(file_dict)

            return [
                datasets.SplitGenerator(
                    name=datasets.Split(split_name),
                    gen_kwargs={
                        "data_file": file_name
                    }
                )
            for split_name, file_name in dl_dir.items()]

        # handle custom config where only country is provided
        elif self.config.lang is not None:
            dl_dir = dl_manager.download_and_extract(self.config.data_url)
            return [
                datasets.SplitGenerator(
                    name=datasets.Split.TRAIN,
                    gen_kwargs={
                        "data_file": dl_dir
                    },
                )
            ]
        

    def _generate_examples(self, data_file):
        pd_df = pd.read_csv(data_file)
        for _, row in pd_df.iterrows():
            example = {feature: row[feature] for feature in self.config.features}
            idx = row["id"]
            yield idx, example
