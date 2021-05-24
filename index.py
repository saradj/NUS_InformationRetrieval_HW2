#!/usr/bin/python3
import nltk
import sys
import getopt
import math
import pickle
import string
from os import listdir
from os.path import isfile, join
from nltk.stem.porter import PorterStemmer


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    index = {}
    posting = {}
    punctuationList = list(string.punctuation)
    stemmer = PorterStemmer()
    all_files = [file for file in listdir(in_dir)
             if isfile(join(in_dir, file))]

    for file in all_files:

        tokens = []
        fp = open(join(input_directory, file), "r")
        for line in fp:
            for sentence_tokens in nltk.sent_tokenize(line):
                for word in nltk.word_tokenize(sentence_tokens):
                    stemm = stemmer.stem(word).lower()
                    if stemm not in punctuationList: #if the word is not a punctuation
                        tokens.append(stemm)
        for token in tokens:
                    if token in index:
                        if int(file) not in posting[token]:
                            prev_freq = index[token][1]
                            index[token] = (0, prev_freq + 1, 0)
                        posting[token].add(int(file))
                    else:
                        index[token] = (0, 1, 0)
                        posting[token] = set([int(file)])

    all_ids = sorted([int(file) for file in all_files])
    file_acc = 0
    fp = open(out_postings, "w")
    for postng in posting:
        postings_string = postings_list_to_string(sorted(list(posting[postng])))
        fp.write(postings_string)
        index[postng] = (file_acc, index[postng][1], len(postings_string))
        file_acc += len(postings_string)
    post_string_allids = postings_list_to_string(all_ids)
    fp.write(post_string_allids)
    fp.close()
    pickle.dump([index,(file_acc, len(all_ids), len(post_string_allids))], open(out_dict,"wb")) #using pickle for saving on disc



def postings_list_to_string(sorted_posting_list):
    """
     this function adds skip pointers to the sorted postings list, taking a list of postiongs as an input,
     creates a string with the skip pointers marked by "_" underscore and followed by the number of bytes to skip and returns it!
     sorted input list: [1,2,3,4,5]
     output string : " 1 _3 2 3 _3 4 5"
     meaning there is a skip pointer at 1 to skip 3 bytes and at 3 for 3 bytes
     """
    length = len(sorted_posting_list)
    interval_to_skip = int(math.sqrt(length))
    ctr = 0
    resulting_string = ""
    while(ctr < length):
        resulting_string += " "
        resulting_string += str(sorted_posting_list[ctr])
        if interval_to_skip > 1 and ctr % interval_to_skip == 0 :
            skip_until = ctr + interval_to_skip
            if skip_until >= length:
                ctr = ctr + 1
            else:
                skiped_part = sorted_posting_list[ctr + 1:skip_until]
                skipping_string = " ".join(str(doc) for doc in skiped_part)
                # Calculating the bytes that need to be skipped
                resulting_string += " " + "_" + str(len(skipping_string) + 2)
                #using _ underscore to define the skip pointer
                resulting_string += " " + skipping_string
                ctr = ctr + len(skiped_part) + 1
        else:
            ctr = ctr + 1
    return resulting_string

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
