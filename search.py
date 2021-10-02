from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time
import json 
import pickle 
import sys
import Stemmer
import os
import math

TOTAL_DOCS=30000000
ss = Stemmer.Stemmer('english')

weights = {'t': 30, 'b': 25, 'r': 5, 'e': 5, 'c': 10, 'i': 20}

file_exists = open('./index_files/helper_files/file_exists.txt', 'r')
file_exists_content = file_exists.read()
file_exists_content = json.loads(file_exists_content)
file_exists.close()

first_word = open('./index_files/helper_files/first_word.txt', 'r')
first_word_content = first_word.read()
first_word_content = json.loads(first_word_content)
first_word.close()

def get_final_answer(merged_lst, num_of_items, merged_dct_with_scores):
    ans_lst = []
    tmp_lst = []
    return_lst = []

    tmp_lst.append(merged_lst[0][0])
    prev = merged_lst[0][1]

    for num in range(1,num_of_items):
        if merged_lst[num][1]==prev:
            tmp_lst.append(merged_lst[num][0])
        else:
            ans_lst.append(tmp_lst)
            tmp_lst = []
            tmp_lst.append(merged_lst[num][0])
        
        prev = merged_lst[num][1]

    ans_lst.append(tmp_lst)

    for this_lst in ans_lst:
        score_lst = []
        for this_item in this_lst:
            score_lst.append([merged_dct_with_scores[this_item], this_item])
        score_lst.sort(reverse=True)
        return_lst.extend(score_lst)

    return return_lst
    

def make_ranking_dct(res, subst, l, ranking_dct):
    idf = math.log(TOTAL_DOCS/l)
    
    for val in res[subst]:
        split_lst = val.split("-")
        doc_id = split_lst[0]
    
        if len(split_lst)>1:
            tf = math.log(1+int(split_lst[1]))*weights[subst]
        else:
            tf = math.log(1+1)*weights[subst]
            
        if merged_dct.get(doc_id):
            curr_value = merged_dct[doc_id]
            merged_dct[doc_id] = curr_value+1
        else:
            merged_dct[doc_id] = 1

        if merged_dct_with_scores.get(doc_id):
            curr_value = merged_dct_with_scores[doc_id]
            merged_dct_with_scores[doc_id] = curr_value+tf*idf
        else:
            merged_dct_with_scores[doc_id] = tf*idf

    return ranking_dct

query_file = sys.argv[1]
f = open(query_file, "r")
lines = f.read()
f.close()

queries = lines.split("\n")

for query in queries:
    merged_dct = {}
    merged_dct_with_scores = {}

    start_time = time.time()    
    write_file = open('2018101052_queries_op.txt', 'a')
    
    find_lst = []
    if query=='':
        continue
    
    query_lst = query.split(":")
    if len(query_lst)>1:
        for i in range(len(query_lst)):
            element = query_lst[i]
            element = element.strip()
            tmp = element.split(" ")
            if len(tmp)>1:
                for j in range(len(tmp)-1):
                    find_lst.append([prev, tmp[j]])
                prev = tmp[-1]
            else:
                if i!=0:
                    find_lst.append([prev, tmp[0]])
                prev = tmp[-1]
    else:
        elements = query_lst[0].split(" ")
        for element in elements:
            find_lst.append(element)

    all_ranked_lst = []

    for the_word in find_lst:
        ranking_dct = {}
        flag=0
    
        if isinstance(the_word, list):
            subst = the_word[0]
            word = the_word[1].lower()
            word = ss.stemWord(word)
            flag=1
        else:
            word = the_word.lower()
            word = ss.stemWord(word)
   
        if len(word)>=3:
            filename = word[0]+word[1]+word[2]
        elif len(word)>=2:
            filename = word[0]+word[1]
        else:
            filename = word[0]

        file_path = filename  + ".txt"
        
        if file_exists_content.get(file_path):
            file_num_value=file_exists_content[file_path]

            if file_num_value!=-1:
                for file_counter in range(file_num_value,0,-1):
                    
                    this_file_path = "index_files/" + filename  + "_" + str(file_counter)
                    this_first_word = first_word_content[this_file_path]
                    if this_first_word<word:
                        get_cnt_value = file_counter
                        break
    
                final_file_path = "index_files/" + filename  + "_" + str(get_cnt_value) + ".txt"
            else:
                final_file_path = "index_files/" + filename  + ".txt"

            if os.path.exists(final_file_path):
                f = open(final_file_path, 'r')
                text = f.read()
                #text = text[1:-1]
                #text = text.replace("\'", "\"")
                content = json.loads(text)
                f.close()
        else:
            content = {}
    
        if content.get(word):
            res = content[word]
            tmp = {}

            if flag==1:
                subst_ids = []
                if res.get(subst):
                    subst_ids_len = len(res[subst])
                    ranking_dct = make_ranking_dct(res, subst, subst_ids_len, ranking_dct)

            else:
                title_ids = []
                text_ids = []
                ref_ids = []
                links_ids = []
                cat_ids = []
                infobox_ids = []
    
                if res.get('t'):
                    title_ids_len = len(res['t'])
                    ranking_dct = make_ranking_dct(res, 't', title_ids_len, ranking_dct)
    
                if res.get('b'):
                    text_ids_len = len(res['b'])
                    ranking_dct = make_ranking_dct(res, 'b', text_ids_len, ranking_dct)
    
                if res.get('r'):
                    ref_ids_len = len(res['r'])
                    ranking_dct = make_ranking_dct(res, 'r', ref_ids_len, ranking_dct)
    
                if res.get('e'):
                    links_ids_len = len(res['e'])
                    ranking_dct = make_ranking_dct(res, 'e', links_ids_len, ranking_dct)
    
                if res.get('c'):
                    cat_ids_len = len(res['c'])
                    ranking_dct = make_ranking_dct(res, 'c', cat_ids_len, ranking_dct)
    
                if res.get('i'):
                    infobox_ids_len = len(res['i'])
                    ranking_dct = make_ranking_dct(res, 'i', infobox_ids_len, ranking_dct)

        all_ranked_lst.append(ranking_dct)

    result_flag=0

    merged_lst = sorted(merged_dct.items(), key=lambda x: x[1], reverse=True)
    
    if len(merged_lst)==0:
        write_file.write("No Relevant Docs Found!"+"\n")
        result_flag=1

    elif len(merged_lst)<=10:
        result_lst = get_final_answer(merged_lst, len(merged_lst), merged_dct_with_scores)

    elif len(merged_lst)>10:

        cutoff_val1 = merged_lst[9][1]
        cutoff_val2 = merged_lst[10][1]

        if cutoff_val1!=cutoff_val2:
            result_lst = get_final_answer(merged_lst, 10, merged_dct_with_scores)

        else:
            idx = -1
            for num in range(9,-1,-1):
                tmp_value = merged_lst[num][1]
                if tmp_value!=cutoff_val1:
                    idx=num
                    break

            idx_result_lst = []
            if idx!=-1:
                idx_result_lst = get_final_answer(merged_lst, idx+1, merged_dct_with_scores)

            result_lst = []
            result_lst.extend(idx_result_lst)

            docs = []

            for num in range(idx+1, len(merged_lst)):
                if merged_lst[num][1]==cutoff_val1:
                    docs.append([merged_dct_with_scores[merged_lst[num][0]], merged_lst[num][0]])
                else:
                    break

            docs.sort(reverse=True)
            docs = docs[0:10-idx-1]
            result_lst.extend(docs)

    if result_flag==0:

        for num in range(len(result_lst)):
            
            title_idx = int(int(result_lst[num][1])/20000)
            
            f = open('./index_files/titles/titles'+"_"+str(title_idx+1)+'.txt', 'r')
            title_content = f.read()
            page_titles = json.loads(title_content)
            f.close()    
            
            write_file.write(result_lst[num][1]+", "+page_titles[result_lst[num][1]]+"\n")
        
    write_file.write(str(time.time()-start_time)+"\n")
    write_file.write("\n")
    
    write_file.close()
