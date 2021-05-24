import pandas as pd
from phonetic import *

data = pd.read_csv("./외래어 모음.txt")

word_list = []
for index, row in data.iterrows():
	word_list.append((row['한국어'],row['영어']))

kor_words = [tup[0] for tup in word_list]
eng_words = [tup[1] for tup in word_list]

count = 0
for index, tup in enumerate(word_list):
    arranged_list = arrange(tup[0], eng_words)
    try:
        rank = arranged_list.index(tup[1])
    except ValueError:
        count += 1
        print(f'{tup[0]} ranked at : UnKnown')
        
    if rank >= 4:
        print(f'{tup[0]} ranked at : {rank + 1}')
        count += 1

print(f'\ntotal non_first rank : {count}')
