#!/bin/bash

#this is an example on how to execute extract_raw_wiki_data_batched.py from CLI (alternatively, you can use this bash script directly)

#params of executions
date_ver=20231101
folder_dir_to_save_batch_files=./example_result_extract_raw_wiki_data_batched
file_dir_to_save_concatted_batch_files=./example_concatted_data_batched/example_concatted_data_batched
lang_list=(id)
concat_batched_data=true

check_or_create_dir () {
  dir_to_check=$1
  if [ ! -d $dir_to_check ]; then
    echo "Dir $dir_to_check not exists! Creating the dir..."
    mkdir $dir_to_check
    fi
}

#main executions
check_or_create_dir $folder_dir_to_save_batch_files

for val in ${!lang_list[@]}; do
    lang=${lang_list[$val]}

    lang_folder_dir="$folder_dir_to_save_batch_files"_"$lang"
    check_or_create_dir $lang_folder_dir

    echo "Executing Extractor on iteration no $((val+1)) of total ${#lang_list[@]} for language $lang and date version of $date_ver"
    python extract_raw_wiki_data_batched.py \
        --lang-id $lang \
        --date-ver $date_ver \
        --save-dir-path $lang_folder_dir
    echo "Done Execution"

    if [ "$$concat_batched_data" = true ]; then
        echo "Concatting the data from $lang_folder_dir to $file_dir_to_save_concatted_batch_files"
        python concat_batched_data.py \
            --load-dir-path $folder_dir_to_save_batch_files \
            --save-dir-path "$file_dir_to_save_concatted_batch_files"_"$lang"
        fi

done
echo "Done Extraction Process"
