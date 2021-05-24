This is the README file for A0207386Y's submission

== Python Version ==

I'm (We're) using Python Version <3.7.6> for
this assignment.

== General Notes about this assignment ==

INDEXING:
For this part I just iterated through the files in the training set and used the suggested nltk functions to parse the words from the text.
I created the entries in the dictionary as follows=> 
({'word1': (starting position, frequency of word, size of posting), 'word2':...}, //this is the first element of the dictionary obtained as index[0] in the code
(starting position for all document ids, frequency for all doc ids, size of all doc ids) //second element - index[1]
) //end of dictionary

The starting position where all document ids are stored (the second element in the dictionary) is usefull for NOT queries, we compare the doc ids containing of the operand with all doc ids and obtain the difference!

I stored the dictionary using pickle.

The posting list is saved as string, where I use the notation underscore for skip pointers => ex for list [1, 2, 3, 4, 5], the stored string would be 1 _3 2 3 _3 4 5, where the number after the underscore specifies the number of bytes to skip, in this case 3 bytes at 1 and 3 bytes at 3.

Searching:

Given the query, I first apply the shunting-yard algorithm to obtain the Reverse Polish notation of the query. Then this query is processed, the AND NOT is turned into an ANOT, a new operator that has the same precedence as AND:1. I used a Query_operand class to encapsulate the operands making it easier to work with them, and then called the appropriate functions(query_and, query_or, query_and_not or query_not) to get the result given the different operators used for the operands.  

== Files included with this submission ==

index.py: code for iterating through all documents and indexing them

dictionary.txt: Resulting file from index.py, stored form of dictionary

postings.txt: Resulting file from index.py, stored form of postings strings

Query_operand.py: code for Query_operand class, encapsulates query operands for easier manipulation

search.py: code for searching given queries using the dictionary and postings files


== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[X] I/We, A0000000X, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

https://en.wikipedia.org/wiki/Shunting-yard_algorithm