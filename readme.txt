The code contains index.sh, index.py and search.py. 

index.sh calls index.py and needs arguments as path_to_dump, path_to_index, stats.txt 
index.py is used for making the inverted_index and search.py is used for searching the queries.

The index_files have been created on the basis of the first 3 alphabets of the word if the length of the word is greater than 3, otherwise it will be on the basis of the length of the word.

Further, if the size of the file becomes greater than 50 MB, that file is divided into multiple files in an alphabetical order.

Other than the index_files, I have created 3 more helper files.
1) One helps in storing the titles corresponding to the document ids. 
2) Second one helps me detect if this file was split into multiple files or not.
3) Third file helps me with the first word (in the alphabetical order) of the files which were splitted.

All these files are created by index.py and will aid in searching.

To make index, type the following command:
./index.sh './enwiki-latest-pages-articles17.xml-p23570393p23716197' '.' 'stats.txt'

To search queries, type the following command:
python3 search.py queries.txt

## NOTE

The numbers in the stats.txt have been extrapolated since the code could not run on the entire dataset within the time limit.
