# -*- coding: utf-8 -*-

import requests
import re
CODE = re.compile(r"Code[^s /][^(Switch)(switch)]|[-2]Code|Code [A-Z]|code corpus|corpus of code|trained.{1,20}on.{1,20} code|code understanding|code generation|code.writing|code summarization|code translation|code completion|code synthesize|understand.{1,5} code|generat.{1,5} code|writ.{1,5} code|summariz.{1,5} code|translat.{1,5} code|complet.{1,5} code|synthesiz.{1,5} code|from code|to code", re.S)
LLM = re.compile(r"[Ll]arge [Ll]anguage [Mm]odel|[Ff]oundation [Mm]odel", re.S)
IA = re.compile(r"([Ii]ntelligent|[Aa]utonomous|[Ee]mbodied|LLM|[Cc]omputer|[Mm]ulti.|[Ll]anguage|[Rr]easoning|(Ss)ituated) [Aa]gent|robot(ic)? task|robot(ic)? polic")
TO_PATTERN_MAPPING = {
    "code": CODE,
    "llm": LLM,
    "ia": IA,
}
import time
import pandas as pd
from bs4 import BeautifulSoup
import csv
import os
import random

def get_one_page(url):
    send_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8"
    }
    response = requests.get(url, headers=send_headers)
    while response.status_code == 403:
        time.sleep(500 + random.uniform(0, 500))
        response = requests.get(url,headers=send_headers)
    if response.status_code == 200:
        return response.text

    return None

def get_papers(date):
    url = f'https://arxiv.org/list/cs/{date}?skip=0&show=10000'
    try:
        list_ids = []
        list_title = []
        list_authors = []
        list_subjects = []
        html = get_one_page(url)
        soup = BeautifulSoup(html, features='html.parser')
        content = soup.dl
        # print(date)
        list_ids.extend(content.find_all('a', title = 'Abstract'))
        list_title.extend(content.find_all('div', class_ = 'list-title mathjax'))
        list_authors.extend(content.find_all('div', class_ = 'list-authors'))
        list_subjects.extend(content.find_all('div', class_ = 'list-subjects'))
        
        list_subject_split = []
        for subjects in list_subjects:
            subjects = subjects.text.split(': ', maxsplit=1)[1]
            subjects = subjects.replace('\n\n', '')
            subjects = subjects.replace('\n', '')
            subject_split = subjects.split('; ')
            list_subject_split.append(subject_split)
        
        items = {k: [] for k in TO_PATTERN_MAPPING.keys()}
        for i, paper in enumerate(zip(list_ids, list_title, list_authors, list_subjects, list_subject_split)):
            time.sleep(1)
            # arXiv:2201.00001
            _id = paper[0].text.replace("\n", " ").replace("  ", " ").strip()
            _id = _id.split(":")[1].strip()
            # Title: Modeling Advection on Directed Graphs using Matérn Gaussian Processes for Traffic Flow
            _title = paper[1].text.replace("\n", " ").replace("  ", " ").strip()
            _title = _title.split(":")[1].strip()
            # Authors: Danielle C Maddix, Nadim Saad, Yuyang Wang
            _authors = paper[2].text.replace("\n", " ").replace("  ", " ").strip()
            _authors = _authors.split(":")[1].strip().split(", ")
            # Subjects: Numerical Analysis (math.NA); Machine Learning (stat.ML)
            _subjects = paper[3].text.replace("\n", " ").replace("  ", " ").strip()
            _subjects = _subjects.split(":")[1].strip().split(", ")
            # ['Numerical Analysis (math.NA)', 'Machine Learning (stat.ML)']
            _subject_split = paper[4]
            _abstract = BeautifulSoup(get_one_page("https://arxiv.org/abs/"+_id), features='html.parser').find_all('blockquote', class_="abstract mathjax")[0].text.split("Abstract:")[1].strip().replace("\n", " ").replace("  ", " ").strip()
            for k in items.keys():
                if TO_PATTERN_MAPPING[k].search(_abstract):
                    items[k].append([_id, _title, _abstract])
        name = ['id', 'title', 'abstract']
        count = {}  
        for k, v in items.items():
            count[k] = len(v)    
            paper = pd.DataFrame(columns=name,data=v)
            paper = paper.drop_duplicates(subset='id',keep='first')
            paper.to_csv(os.path.join('/home/key4/Wizard', f'{date}_{k}.csv'))
        return count
    except:
        print("Invalid date:", date)
    

def main():
    os.makedirs('/home/key4/Wizard', exist_ok=True)
    with open('/home/key4/Wizard/output.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["Date"]+[k.upper() for k in TO_PATTERN_MAPPING.keys()])
        for y in [str(i) for i in range(17, 24)]:
            for m in ["{:02d}".format(i) for i in range(1, 13)]:
                _c = get_papers(y+m)
                if _c:
                    writer.writerow([y+m]+[_c[k] for k in TO_PATTERN_MAPPING.keys()])


if __name__ == '__main__':
    main()
    
    
