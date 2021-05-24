#!/usr/bin/python3

import sys
import getopt
import pickle
from Query_operand import *



openBrace = "("
closedBrace = ")"
operators = set(["AndNOT", "NOT", "AND", "OR"])
op_precedence = {"NOT":2, "AndNOT":1, "AND":1, "OR": 0} #have added AndNOT which is and not so that it is considered with precedence 1 not 2!

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')


    fp_query = open(queries_file, "r")
    output_file = open(results_file, "w")
    index = pickle.load(open(dict_file, "rb"))
    for query in fp_query:
        query = query.strip()
        final_query = shunting_yard_algo(query)
        q_stack = []
        for q_token in final_query:
            if q_token not in operators:  q_stack.append(Query_operand(index[0], postings_file, token = q_token, result_list=[], all=False))
            elif q_token == "AND": q_stack.append(query_and(q_stack.pop(), q_stack.pop(), index[0], postings_file))
            elif q_token == "NOT":
                q_stack.append(query_not(q_stack.pop(), index[0], index[1], postings_file))
            elif q_token == "AndNOT": q_stack.append(query_and_not(q_stack.pop(), q_stack.pop(), index[0], postings_file))
            elif q_token == "OR": q_stack.append(query_or(q_stack.pop(), q_stack.pop(), index[0], postings_file))
        result =  q_stack.pop();
        if not result.holds_result:
            for _ in range(result.freq):
                result.done_res.append(result.next_value())
            result.holds_result = True
        output_file.write(" ".join(result.done_res) + "\n")
    fp_query.close()
    output_file.close()

def get_top_operator(op_stack):
    return 0 if not op_stack else op_precedence[op_stack[len(op_stack) - 1]]

def shunting_yard_algo(query):
    out_queue = []
    op_stack = []
    query_words = []
    words = query.split(" ")
    for word in words:
        nb_closed_brace = 0
        curr_word = word
        while(curr_word[0] == openBrace):
            curr_word = curr_word[1:]
            query_words.append(openBrace)

        while(curr_word[-1] == closedBrace):
            curr_word = curr_word[:-1]
            nb_closed_brace += 1
        query_words.append(curr_word)

        for _ in range(nb_closed_brace):
            query_words.append(closedBrace)

    while query_words:
        curr_word = query_words.pop(0)
        # for the AND NOT case, turn it into AndNOT
        if query_words and curr_word == "AND" and query_words[0] == "NOT":
            curr_word = "AndNOT"
            query_words.pop(0)
        # shunting yard algorithm applied
        if curr_word not in operators and not (curr_word == closedBrace or curr_word == openBrace):
            out_queue.append(curr_word)
        if curr_word in operators:
            while op_stack and op_stack[len(op_stack) - 1] != openBrace and ((get_top_operator(op_stack) > op_precedence[curr_word]) or (curr_word != "NOT" and get_top_operator(op_stack) == op_precedence[curr_word])) :
                out_queue.append(op_stack.pop())
            op_stack.append(curr_word)
        if curr_word == openBrace:
            op_stack.append(curr_word)
        if curr_word == closedBrace:
            while op_stack[len(op_stack) - 1] != openBrace:
                out_queue.append(op_stack.pop())
            op_stack.pop()
    while op_stack:
        out_queue.append(op_stack.pop())
    return out_queue


"""
functions implementing the query search for different operators, given the operand(s)
"""
def query_and(first_op, second_op, index, postings_file):

    first_op_freq = len(first_op.done_res) if first_op.holds_result else first_op.freq
    second_op_freq = len(second_op.done_res) if second_op.holds_result else second_op.freq
    if first_op_freq > second_op_freq:
        return query_and(second_op, first_op, index, postings_file) #optimization such that we have the smallest frequency operator first
    else:
        result = []
        first = first_op.next_value()
        second = second_op.next_value()
        while first != "" and second != "":
            if int(first) == int(second): #we found a match containing both operands add it to the result
                result.append(first)
                first = first_op.next_value()
                second = second_op.next_value()
            elif int(first) < int(second):
                (first_skip, first_skip_interval) = first_op.skip_ptr()
                if first_skip != "" and int(first_skip) <= int(second): #if we should take the skip pointer
                    if not first_op.holds_result: first_op.next_fp += first_skip_interval
                    else: first_op.next_idx += first_skip_interval
                    first = first_skip
                else:
                    first = first_op.next_value() #we dont take the skip pointer
            else:
                (sec_skip, sec_skip_interval) = second_op.skip_ptr()
                if sec_skip != "" and int(sec_skip) <= int(first):#if we should take the skip pointer
                    if not second_op.holds_result: second_op.next_fp += sec_skip_interval
                    else: second_op.next_idx += sec_skip_interval
                    second = sec_skip
                else:
                    second = second_op.next_value()#we dont take the skip pointer
        return Query_operand(index, postings_file, result_list = result)


def query_or(first, second, index, postings_file):
    result = []
    if first.holds_result and not first.done_res :
        if not second.holds_result:
            for _ in range(second.freq):
                second.done_res.append(second.next_value())
            second.holds_result = True
        result = second.done_res

    elif second.holds_result and len(second.done_res) == 0:
        if not first.holds_result:
            for _ in range(first.freq):
                first.done_res.append(first.next_value())
            first.holds_result = True

        result = first.done_res

    else:
        n_first = first.next_value()
        n_second = second.next_value()
        while not (n_first == "" or n_second == ""):
            if int(n_first) == int(n_second): #found a match in both == and
                result.append(n_first)
                n_first = first.next_value()
                n_second = second.next_value()
            elif int(n_first) < int(n_second):
                result.append(n_first)
                n_first = first.next_value()
            else:
                result.append(n_second)
                n_second = second.next_value()
        while not n_first == "":
            result.append(n_first)
            n_first = first.next_value()

        while not n_second == "":
            result.append(n_second)
            n_second = second.next_value()

    return Query_operand(index, postings_file, result_list = result)

def query_and_not(first_op, second_op, index, postings_file):
    first = second_op.next_value()
    negated = first_op.next_value()
    result = []
    while not (first == "" or negated == ""):
        if int(first) == int(negated):
            first = second_op.next_value()
            negated = first_op.next_value()

        elif int(first) < int(negated):
            result.append(first)
            first = second_op.next_value()
        else:
            negated = first_op.next_value()
    while not first == "":
        result.append(first)
        first = second_op.next_value()
    return Query_operand(index, postings_file, result_list = result)

def query_not(operand, index, all_ids, postings_file):
    everything = Query_operand(all_ids, postings_file, all = True)
    op_next = operand.next_value()
    e_next = everything.next_value()
    result = []
    while op_next != "" and e_next != "":
        if int(op_next) == int(e_next):
            op_next = operand.next_value()
            e_next = everything.next_value()
        elif int(op_next) < int(e_next):
            result.append(op_next)
            op_next = operand.next_value()
        else:
            result.append(e_next)
            e_next = everything.next_value()
    while e_next != "":
        result.append(e_next)
        e_next = everything.next_value()
    return Query_operand(index, postings_file, result_list = result)


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)



run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
