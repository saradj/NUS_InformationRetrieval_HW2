import math
from nltk.stem.porter import PorterStemmer
import os


class Query_operand:

    def __init__(self, index, postings_file, token = "", result_list=[], all=False):

        # result variables
        self.next_idx = 0
        self.done_res = []

        # word variables
        self.holds_result = False
        self.postings_file = postings_file
        self.fp_start = 0
        self.next_fp = 0
        self.freq = 0
        self.size = 0
        self.word = ""

        if all:
            self.fp_start = index[0]
            self.freq = index[1]
            self.size = index[2]
            self.next_fp = self.fp_start
        elif token != "":
            stemmer = PorterStemmer()
            self.word = stemmer.stem(token).lower()
            if self.word not in index:
                self.holds_result = True
            else:
                self.fp_start = index[self.word][0]
                self.next_fp = self.fp_start
                self.freq = index[self.word][1]
                self.size = index[self.word][2]
        else:
            self.holds_result = True
            self.done_res = result_list


    def next_value(self):
        next_val = ""
        if self.holds_result:
            if self.next_idx < len(self.done_res):
                next_val = self.done_res[self.next_idx]
                self.next_idx += 1
        elif self.next_fp < self.fp_start + self.size:
            fp_posting = open(self.postings_file, "rb")
            fp_posting.seek(self.next_fp)
            while next_val == "":
                fp_posting.seek(1,os.SEEK_CUR) # The first one is a space
                current = fp_posting.read(1)
                current = current.decode("utf-8") #binary mode, need to decode
                if current == "": #if end of file
                    return next_val
                while current != " " and current != "":
                    if not current == "_": #if not a skip pointer
                        next_val += current
                    current = fp_posting.read(1)
                    current = current.decode("utf-8") #binary mode, need to decode
                fp_posting.seek(-1,os.SEEK_CUR)
            self.next_fp = fp_posting.tell()
            fp_posting.close()

        return next_val


    def skip_ptr(self):
        ret_result = ("",0)
        if self.holds_result:
            skipping_interval = math.sqrt(len(self.done_res))
            if self.next_idx % skipping_interval == 0 and self.next_idx + skipping_interval < len(self.done_res):
                ret_result = (self.done_res[self.next_idx + skipping_interval], skipping_interval)
        else:
            fp_postings = open(self.postings_file, "rb")
            fp_postings.seek(self.next_fp)
            # first one is a space
            fp_postings.seek(1, os.SEEK_CUR)
            curr = fp_postings.read(1)
            skipped_bytes = 0
            skipped = ""
            skipped_value = ""
            #if we encounter a skip pointer => _
            if curr == "_":
                skipped_bytes += 2
                curr = fp_postings.read(1)
                skipped_bytes += 1

                while curr != " ":
                    skipped += curr
                    skipped_bytes += 1
                    curr = fp_postings.read(1)

                fp_postings.seek(int(skipped) - 1, 1)
                skipped_bytes += int(skipped) - 1
                curr = fp_postings.read(1)
                skipped_bytes += 1

                while curr != " ":
                    skipped_value += curr
                    curr = fp_postings.read(1)
                    skipped_bytes += 1
                skipped_bytes -= 1 # We rewind one byte so that it will always start on space
            fp_postings.close()
            ret_result = (skipped_value,skipped_bytes)
        return ret_result
