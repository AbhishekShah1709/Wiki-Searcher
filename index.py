import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time
import json 
import pickle 
import re 
import sys 
import os 
import Stemmer

start_time = time.time()

dump_path = sys.argv[1]
index_path = sys.argv[2]
stats_path = sys.argv[3]


if os.path.isdir('./index_files')==False:
    os.mkdir('./index_files')

if os.path.isdir('./index_files/titles')==False:
    os.mkdir('./index_files/titles')

if os.path.isdir('./index_files/helper_files')==False:
    os.mkdir('./index_files/helper_files')

f = open(index_path+"/index.txt", "w")
f.close()

content = iter(ET.iterparse(dump_path, events=("start", "end")))

with open('./stopwords.pkl', 'rb') as f:
    stop_words = pickle.load(f)

ss = Stemmer.Stemmer('english')

page_id = 0
tok_reg = re.compile(r'[A-Za-z0-9]+')
str_reg = re.compile(r'(\{\{cite web\|.*\|.*)(title=[^|]*)(\|.*\}\})')
garbage_reg = re.compile(r'{\|(.*?)\|}',re.DOTALL)
numal_reg = re.compile(r"[0-9]+[a-z]+[0-9a-z]*")

cnt=0
title_cnt=0
title_done=0

page_title = ''
title_of_page = {}

all_files_dct = {}

def make_index(ss, filtered_sentence, all_files_dct, subst, page_id):

    freq = {}
    
    for i in range(len(filtered_sentence)):
        if len(filtered_sentence[i])>13:
            continue

        filtered_sentence[i] = ss.stemWord(filtered_sentence[i])
        word = filtered_sentence[i]
    
        if freq.get(word):
            val = freq[word]
            freq[word] = val+1
        else:
            freq[word] = 1

    for word in freq:
        if len(word)>=3:
            filename_key = word[0]+word[1]+word[2]
        elif len(word)>=2:
            filename_key = word[0]+word[1]
        else:
            filename_key = word[0]

        if all_files_dct.get(filename_key):
            filename_val = all_files_dct[filename_key]

            if filename_val.get(word):
                corr_dct = filename_val[word]
                if corr_dct.get(subst):
                    internal_lst = corr_dct[subst]
                    if freq[word]==1:
                        internal_lst.append(str(page_id))
                    else:
                        internal_lst.append(str(page_id)+"-"+str(freq[word]))
                
                else:
                    tmp_lst = []
                    if freq[word]==1:
                        tmp_lst = [str(page_id)]
                    else:
                        tmp_lst = [str(page_id)+"-"+str(freq[word])]
        
                    corr_dct.update({subst:tmp_lst})
        
            else:
                tmp_lst = []
                if freq[word]==1:
                    tmp_lst = [str(page_id)]
                else:
                    tmp_lst = [str(page_id)+"-"+str(freq[word])]
        
                the_dct = {subst: tmp_lst}
                filename_val.update({word: the_dct})
        
        else:
            tmp_lst = []
            if freq[word]==1:
                tmp_lst = [str(page_id)]
            else:
                tmp_lst = [str(page_id)+"-"+str(freq[word])]
        
            the_dct = {subst: tmp_lst}
            final_dct = {word: the_dct}

            all_files_dct.update({filename_key: final_dct})

    return all_files_dct

for event, elem in content:

    tag = elem.tag
    tag = tag.split("}")[1]
    value = elem.text

    if event=="end" and tag=="page":
        title_of_page.update({page_id: page_title})
        page_id+=1
        cnt+=1
        title_cnt+=1
        elem.clear()

    if event=="end" and tag=="title":
        if value!=None:
            page_title = value
            fin_sent = value.lower()

            fin_sent = re.sub('# 2',' ',fin_sent)
            fin_sent = re.sub(str_reg, r"\2", fin_sent)
            fin_sent = re.sub(garbage_reg, '', fin_sent)
            fin_sent = re.sub(numal_reg, '', fin_sent)
 
            fin_sent = re.sub(r"(http://|https://|ftp://|smtp://)([a-z0-9.\-]+[.][a-z]{2,4})([^ \n]*\||[^ \n]*;|[^ \n]* |[^ \n]*|)", '', fin_sent)
            
            fin_sent = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;|&cent;|&pound;|&yen;|&euro;|&copy;|&reg;', r' ', fin_sent)

            word_tokens = re.findall(tok_reg, fin_sent)
            filtered_sentence = [w for w in word_tokens if not w in stop_words]

            all_files_dct = make_index(ss, filtered_sentence, all_files_dct, 't', page_id)


    if event=="end" and tag=="text":
        if value!=None:
            fin_sent = value.lower()
 
            fin_sent = re.sub('# 2',' ',fin_sent)
            fin_sent = re.sub(str_reg, r"\2", fin_sent)
            fin_sent = re.sub(garbage_reg, '', fin_sent)
            fin_sent = re.sub(numal_reg, '', fin_sent)
            
            fin_sent = re.sub(r"(http://|https://|ftp://|smtp://)([a-z0-9.\-]+[.][a-z]{2,4})([^ \n]*\||[^ \n]*;|[^ \n]* |[^ \n]*|)", '', fin_sent)
            
            fin_sent = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;|&cent;|&pound;|&yen;|&euro;|&copy;|&reg;', r' ', fin_sent)

            links_lst = fin_sent.split("==external links==")

            if len(links_lst)>1:
                links = links_lst[1]
                actual_links = links.split("\n\n")[0]
                fin_sent = fin_sent.replace(actual_links,'')

                word_tokens = re.findall(tok_reg, actual_links)
                filtered_sentence = [w for w in word_tokens if not w in stop_words]

                all_files_dct = make_index(ss, filtered_sentence, all_files_dct, 'e', page_id)

            refs_lst = fin_sent.split("==references==")

            if len(refs_lst)>1:
                refs = refs_lst[1]
                actual_refs = refs.split("\n\n")[0]
                fin_sent = fin_sent.replace(actual_refs,'')

                word_tokens = re.findall(tok_reg, actual_refs)
                filtered_sentence = [w for w in word_tokens if not w in stop_words]

                all_files_dct = make_index(ss, filtered_sentence, all_files_dct, 'r', page_id)

            cat_lst = fin_sent.split("[[category:")

            if len(cat_lst)>1:
                filtered_sentences = []
                for i in range(1,len(cat_lst)):
                    cat = cat_lst[i]
                    actual_cat = cat.split("\n")[0]
                    fin_sent = fin_sent.replace(actual_cat,'')

                    word_tokens = re.findall(tok_reg, actual_cat)
                    filtered_sentence = [w for w in word_tokens if not w in stop_words]
                    filtered_sentences.extend(filtered_sentence)

                all_files_dct = make_index(ss, filtered_sentences, all_files_dct, 'c', page_id)

            info_lst = fin_sent.split("{{infobox")
            
            if len(info_lst)>1:
                info = info_lst[1]
                actual_info = info.split("}}")[0]
                fin_sent = fin_sent.replace(actual_info,'')

                word_tokens = re.findall(tok_reg, actual_info)
                filtered_sentence = [w for w in word_tokens if not w in stop_words]

                all_files_dct = make_index(ss, filtered_sentence, all_files_dct, 'i', page_id)

            word_tokens = re.findall(tok_reg, fin_sent)
            filtered_sentence = [w for w in word_tokens if not w in stop_words]

            all_files_dct = make_index(ss, filtered_sentence, all_files_dct, 'b', page_id)

    if title_cnt==20000:
        title_cnt=0
        title_done+=1
        f = open('./index_files/titles/titles'+"_"+str(title_done)+".txt", 'w')
        f.write(json.dumps(title_of_page, indent=0, separators=(",",":")).replace("\n", ""))
        f.close()
        title_of_page = {}
    
    if cnt==80000:
        cnt=0
    
        for alpha_key in all_files_dct.keys():
            if all_files_dct.get(alpha_key):
                alpha_val = all_files_dct[alpha_key]
                filename = alpha_key+'.txt'
                if os.path.exists("./index_files/"+filename):
                    f = open("./index_files/"+filename, 'r+')
                    content = f.read()
                    content = content.replace("\'","\"")
                    existing_dct = json.loads(content)
        
                    for key in alpha_val.keys():
                        if existing_dct.get(key):
                            layer1_dct = existing_dct[key]
                            base1_dct = alpha_val[key]
                            for headings in base1_dct.keys():
                                if layer1_dct.get(headings):
                                    layer2_lst = layer1_dct[headings]
                                    base2_lst = base1_dct[headings]
                                    layer2_lst.extend(base2_lst)
                                else:
                                    layer1_dct[headings] = base1_dct[headings]
                        else:
                            existing_dct[key] = alpha_val[key]
                    f.seek(0)
                    #f.write(json.dumps(existing_dct))
                    f.write(json.dumps(existing_dct, indent=0, separators=(",",":")).replace("\n", ""))
                    f.close()
        
                else:
                    f = open("./index_files/"+filename, 'w')
                    #f.write(json.dumps(alpha_val))
                    f.write(json.dumps(alpha_val, indent=0, separators=(",",":")).replace("\n", ""))
                    f.close()

        all_files_dct = {}

title_done+=1
for alpha_key in all_files_dct.keys(): 
    f = open('./index_files/titles/titles'+"_"+str(title_done)+".txt", 'w')
    f.write(json.dumps(title_of_page, indent=0, separators=(",",":")).replace("\n", ""))
    f.close()
    title_of_page = {}

    if all_files_dct.get(alpha_key):
        alpha_val = all_files_dct[alpha_key]
        filename = alpha_key+'.txt'
        if os.path.exists("./index_files/"+filename):
            f = open("./index_files/"+filename, 'r+')
            content = f.read()
            content = content.replace("\'","\"")
            existing_dct = json.loads(content)

            for key in alpha_val.keys():
                if existing_dct.get(key):
                    layer1_dct = existing_dct[key]
                    base1_dct = alpha_val[key]
                    for headings in base1_dct.keys():
                        if layer1_dct.get(headings):
                            layer2_lst = layer1_dct[headings]
                            base2_lst = base1_dct[headings]
                            layer2_lst.extend(base2_lst)
                        else:
                            layer1_dct[headings] = base1_dct[headings]
                else:
                    existing_dct[key] = alpha_val[key]
            f.seek(0)
            f.write(json.dumps(existing_dct, indent=0, separators=(",",":")).replace("\n", ""))
            #f.write(json.dumps(existing_dct))
            f.close()

        else:
            f = open("./index_files/"+filename, 'w')
            f.write(json.dumps(alpha_val, indent=0, separators=(",",":")).replace("\n", ""))
            #f.write(json.dumps(alpha_val))
            f.close()


total_tokens = 0
directory = 'index_files/'
dir_lst = os.listdir(directory)

for filename in dir_lst:
    if os.path.isfile(directory+filename):
        f = open(directory+filename, "r")
        content = f.read()
        content = content.replace("\'","\"")
        curr_dct = json.loads(content)
    
        total_tokens += len(curr_dct.keys())
    
        f.close()


f = open('stats.txt', 'w')
f.write(str(total_tokens))
f.close()

for filename in dir_lst:
    if os.path.isfile(directory+filename):
        f = os.path.join(directory, filename)
        file_size = os.path.getsize(f)
        
        threshold = 1000000*40
#        threshold = 1000*200
        denominator = threshold/2
        if file_size>threshold:
            tmp = int(file_size/denominator)

            if denominator*tmp==file_size:
                num_files = int(file_size/denominator)
            else:
                num_files = int(file_size/denominator)+1

            if os.path.exists('./index_files/helper_files/file_exists.txt'): 
                file_exists_f = open('./index_files/helper_files/file_exists.txt', 'r+')
                file_exists_content = file_exists_f.read()
                file_exists_content = json.loads(file_exists_content)
                file_exists_content.update({filename: num_files})
                file_exists_f.seek(0)
                file_exists_f.write(json.dumps(file_exists_content, indent=0, separators=(",",":")).replace("\n", ""))
                file_exists_f.close()
            else:
                file_exists_f = open('./index_files/helper_files/file_exists.txt', 'a')
                file_exists_content = {filename: num_files}
                file_exists_f.write(json.dumps(file_exists_content, indent=0, separators=(",",":")).replace("\n", ""))
                file_exists_f.close()

            fl = open(f,'r')
            content = fl.read()
            content = content.replace("\'","\"")
            curr_dct = json.loads(content)
        
            keys_lst = curr_dct.keys()
            keys_lst = list(keys_lst)
            keys_lst.sort()
            l = len(keys_lst)
        
            file_counter=1
            dct_counter=0
            dct_threshold=int(l/num_files)+1

            ini_f = f.split(".")[0]
            new_f = open(ini_f+"_"+str(file_counter)+".txt", 'w')
            new_lst = []
            new_dct = {}

            if os.path.exists('./index_files/helper_files/first_word.txt'): 
                first_f = open('./index_files/helper_files/first_word.txt', 'r+')
                first_content = first_f.read()
                first_content = json.loads(first_content)
                first_content.update({ini_f+"_"+str(file_counter): keys_lst[0]})
                first_f.seek(0)
                first_f.write(json.dumps(first_content, indent=0, separators=(",",":")).replace("\n", ""))
                first_f.close()
            else:
                first_f = open('./index_files/helper_files/first_word.txt', 'a')
                first_content = {ini_f+"_"+str(file_counter): keys_lst[0]}
                first_f.write(json.dumps(first_content, indent=0, separators=(",",":")).replace("\n", ""))
                first_f.close()

            for key in keys_lst:
        
                if dct_counter==dct_threshold:
                    new_f.write(json.dumps(new_dct, indent=0, separators=(",",":")).replace("\n", ""))
                    new_f.close()
            
                    file_counter+=1
                    new_f = open(ini_f+"_"+str(file_counter)+".txt", 'w')
                    
                    first_f = open('./index_files/helper_files/first_word.txt', 'r+')
                    first_content = first_f.read()
                    first_content = json.loads(first_content)
                    first_content.update({ini_f+"_"+str(file_counter): key}) 
                    first_f.seek(0)
                    first_f.write(json.dumps(first_content, indent=0, separators=(",",":")).replace("\n", ""))
                    first_f.close()
                    
                    new_dct = {}
                    new_dct.update({key: curr_dct[key]})
                    dct_counter=1
                else:
                    new_dct.update({key: curr_dct[key]})
                    dct_counter+=1
        
            new_f.write(json.dumps(new_dct, indent=0, separators=(",",":")).replace("\n", ""))
            new_f.close()
            os.remove(f)
        else:
            if os.path.exists('./index_files/helper_files/file_exists.txt'): 
                file_exists_f = open('./index_files/helper_files/file_exists.txt', 'r+')
                file_exists_content = file_exists_f.read()
                file_exists_content = json.loads(file_exists_content)
                file_exists_content.update({filename: -1})
                file_exists_f.seek(0)
                file_exists_f.write(json.dumps(file_exists_content, indent=0, separators=(",",":")).replace("\n", ""))
                file_exists_f.close()
            else:
                file_exists_f = open('./index_files/helper_files/file_exists.txt', 'a')
                file_exists_content = {filename: -1}
                file_exists_f.write(json.dumps(file_exists_content, indent=0, separators=(",",":")).replace("\n", ""))
                file_exists_f.close()
