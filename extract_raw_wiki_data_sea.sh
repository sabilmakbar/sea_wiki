#!/bin/bash

# all available lang codes in SEA local-languages or linguistically-related to following countries in SEA:
# Indonesia: "ace" (Acehnese), "ban" (Balinese), "bjn" (Banjarese), "bug" (Buginese), "gor" (Gorontalo), "id" (Indonesian), "jv" (Javanese), "mad" (Madurese), "map-bms" (Banyumasan, Dialect of Javanese), "min" (Minangkabau), "ms" (Malay), "nia" (Nias), "su" (Sundanese), "tet" (Tetum)
# Singapore: "ms" (Malay), "ta" (Tamil)
# Malaysia: "ms" (Malay), "ta" (Tamil)
# Brunei: "ms" (Malay)
# Thailand: "mnw" (Mon), "shn" (Shan), "th" (Thai)
# Myanmar: "my" (Burmese), "mnw" (Mon), "shn" (Shan)
# Laos: "lo" (Lao)
# Vietnam: "vi" (Vietnamese)
# Cambodia: "km" (Khmer)
# East Timor: "tet" (Tetum)
# Philippines: "bcl" (Central Bicolano), "cbk-zam" (Chavacano), "ceb" (Cebuano), "ilo" (Ilokano), "pag" (Pangasinan), "pam" (Kapampangan), "tl" (Tagalog), "war" (Waray)

#params of executions
date_ver=20231101
folder_dir_to_save=./sea_wiki_raw_data
# example:
lang_list=(ace id map-bms mnw pag pam shn war)
# full list:
# lang_list=(ace ban bcl bjn bug cbk-zam ceb gor id ilo jv km lo mad map-bms min mnw ms my nia pag pam shn su tet ta th tl vi war)


#main executions

if [ ! -d $folder_dir_to_save ]; then
    echo "Dir $folder_dir_to_save not exists! Creating the dir..."
    mkdir $folder_dir_to_save
fi

for val in ${!lang_list[@]}; do
    lang=${lang_list[$val]}
    echo "Executing Extractor on iteration no $((val+1)) of total ${#lang_list[@]} for language $lang and date version of $date_ver"
    python extract_raw_wiki_data.py \
        --lang-id $lang \
        --date-ver $date_ver \
        --save-dir-path $folder_dir_to_save
    echo "Done Execution"
done
echo "Done Extraction Process"
