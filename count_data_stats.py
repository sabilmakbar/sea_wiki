import multiprocessing as mp

import numpy as np
from datasets import load_dataset

import tiktoken

def num_tokens_from_string(string: str):
    """Returns the number of tokens in a text string."""    
    num_tokens = len(encoding.encode(string))
    return num_tokens

def cnt_token_in_hf_wiki_dset(data):
    data["token_cnt"] = num_tokens_from_string(data["text"])
    return data

if __name__ == "__main__":

    #this will refer to its local version of dataset loader script, not the HF repo ones
    dataset = load_dataset("sea_wiki.py")

    encoding = tiktoken.encoding_for_model('gpt-4')

    stat_dict = {}
    for split, dset in dataset.items():
        dset_text = dset.select_columns(['text'])
        print(f"Counting total token in split lang: {split}")
        dset_text = dset_text.map(cnt_token_in_hf_wiki_dset, num_proc=max(mp.cpu_count()-2,1))
        token_data = list(dset_text["token_cnt"])
        total_token = sum(token_data)
        avg_token = sum(token_data)/len(token_data)
        min_token = min(token_data)
        max_token = max(token_data)
        deciles = np.percentile(token_data, np.arange(10, 100, 10)).tolist()
        stat_dict[split] = {"total": total_token, "avg": avg_token, "min": min_token, "max": max_token, "deciles": deciles}

    # for markdown table format
    print("| Lang Code | Total Token | Avg Token per Article | Min Token | Max Token | Token Deciles List |")
    print("| :---: | ---: | ---: | ---: | ---: | :--- |")
    for key, data in stat_dict.items():
        print(f"| {key} | {data['total']:,} | {data['avg']:,} | {data['min']:,} | {data['max']:,} | {[round(num,2) for num in data['deciles']]} |")
