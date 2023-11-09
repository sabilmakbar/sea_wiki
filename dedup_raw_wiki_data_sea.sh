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
folder_dir_to_save=./sea_wiki_dedup_data
input_folder_to_be_dedup=./sea_wiki_raw_data

drop_hard_dupl=True
drop_soft_dupl=True


# main executions

# src: https://stackoverflow.com/a/18887210 (to list all files under a dir)
shopt -s nullglob
file_name_array=($input_folder_to_be_dedup/*)
shopt -u nullglob # Turn off nullglob to make sure it doesn't interfere with anything later
file_name_array="${file_name_array}"

if [ ${#file_name_array[@]} == 0 ]; then
    echo "No files found under directory $input_folder_to_be_dedup" >&2
fi

if [ ! -d $folder_dir_to_save ];
then
    echo "Dir $folder_dir_to_save not exists! Creating the dir..."
    mkdir $folder_dir_to_save
fi

echo "The params hard-dedup drop is set as $drop_hard_dupl"
echo "The params soft-dedup drop is set as $drop_soft_dupl"

for val in ${!file_name_array[@]}; do
    csv_path=${file_name_array[$val]}

    if [[ ${csv_path} != *".csv" ]]; then
        echo "The extracted file name isn't a CSV! Skipping! Received $csv_path"
        continue
    fi

    echo "Executing Dedup on iteration no "$((val+1))" of total ${#file_name_array[@]} for input data $csv_path"
    #see the script bcs there are more args than this command is using
    python dedup_raw_wiki_data.py \
        --raw-csv-path $csv_path \
        --drop-hard-dupl $drop_hard_dupl \
        --drop-soft-dupl $drop_soft_dupl \
        --save-dir-path $folder_dir_to_save
    echo "Done Execution"
done
echo "Done Dedup Process"
