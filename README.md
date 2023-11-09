# **SEA Wikipedia Code**
---
Welcome to SEA Wikipedia Code Repository. This repo containing script used for generating data in [SEA Wikipedia HF](https://huggingface.co/datasets/sabilmakbar/sea_wiki). The data are extracted from [Wikipedia HF](https://huggingface.co/datasets/wikipedia) and processed using the scripts available in this repository for reproducibility purpose. For licensing purpose, this codebase adopts license ```cc-by-sa 4.0```, following Wikipedia data license [cc-by-sa 4.0](https://en.wikipedia.org/wiki/Wikipedia:Copyrights), and Wikipedia HF Repo that has [cc-by-sa 3.0](https://huggingface.co/datasets/wikipedia).

# Getting Started #
### To read the datasets directly ###
Plase refer to the HF Repo on [SEA Wiki HF](https://huggingface.co/datasets/sabilmakbar/sea_wiki) to see ```load_datasets``` implementation of ready-to-use data

### To replicate the whole dataset generation process ###
1. Set-up a new Python/Conda Environment (recommended Python version: 3.9.6 to 3.9.18 or 3.10.0 to 3.10.13) and install the requirements on ```requirements.txt``` use this codebase via ```pip install -r requirements.txt```.

2. Activate the chosen Python/Conda environment which the requirements are being installed.

3. Force install ```multiprocess==0.70.15``` by using ```pip install multiprocess==0.70.15``` to avoid [this issue](https://github.com/huggingface/datasets/issues/5613#issuecomment-1703169594) (there's no other workaround for now)

4. Run this ```sh``` script for extractions from Wikiedia HF using ```sh extract_raw_wiki_data_sea.sh```<br>
This script will run [_```extract_raw_wiki_data.py```_](https://github.com/sabilmakbar/sea_wiki/blob/main/extract_raw_wiki_data.py) to construct the Wiki Dataset.

5.  Run this ```sh``` script for deduplications from extracted data in Step 4 using ```sh dedup_raw_wiki_data_sea.sh```<br>
This script will run [_```dedup_raw_wiki_data.py```_](https://github.com/sabilmakbar/sea_wiki/blob/main/dedup_raw_wiki_data.py) to do Wiki Dataset Clenasing. Please note that the cleansing process can be language/dialect specific.


# **FAQS**

### How does the data being preprocessed? What makes it different from loading it directly from Wikipedia HF?
The data available in here are processed with following flows:
1. Raw data is being deduplicated on ```title``` and ```text``` (text-content from a given article), to remove articles containing boilerplate text (template text that are used usually for unavailable informations or asking for contributions of content in that article), which usually deemed noisy for NLP data.
2. Furthermore, the ```title``` and ```text``` data are being checked for string-matching duplication (duplication of text that are being pre-processed, i.e symbols removed, HTML tags striped, or ASCII-chars/UTF-8 chars validated). You may check this [ ```dedup_raw_wiki_data.py```](https://github.com/sabilmakbar/sea_wiki/blob/main/dedup_raw_wiki_data.py) script to understand its implementation.

### How do I extract new Wikipedia Dataset of SEA languages?
You may check to the script [_```extract_raw_wiki_data.py```_](https://github.com/sabilmakbar/sea_wiki/blob/main/extract_raw_wiki_data.py) to understand its implementations, or you can adjust the bash provided in [_```extract_raw_wiki_data_sea.sh```_](https://github.com/sabilmakbar/sea_wiki/blob/main/extract_raw_wiki_data_sea.sh) to extract it on your own. 

### How do I extract new Wikipedia Dataset of SEA languages?
You may visit this [Wikipedia Dump Index](https://dumps.wikimedia.org/backup-index.html) to check any latest available data and this link [Wikipedia Language Coverage](https://meta.wikimedia.org/wiki/List_of_Wikipedias_by_country) to map into any languages that you're wanting to extract. Please note that this dataset is extensible to any languages of your choice.

## Citation Info:
```
@ONLINE{wikidump,
    author = "Wikimedia Foundation",
    title  = "Wikimedia Downloads",
    url    = "https://dumps.wikimedia.org"}
@ONLINE{wikipedia-hf,
    title  = "Huggingface Wikipedia Dataset",
    url    = "https://huggingface.co/datasets/wikipedia"}
```
