import string
import re
import atexit
import fileinput
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

ps = PorterStemmer()

# example_words = ["pythoner","pythoning","pythonly","pythoned","python"]

# for w in example_words:
#     print(ps.stem(w))
def quit_gracefully():
    print("end of file")

def findType(inputToken):
    if(type(inputToken) is int):
        return "INT"
    elif(type(inputToken) is str):
        return "STRING"
    elif(type(inputToken) is float):
        return "DOUBLE"
    elif(atexit.register(quit_gracefully())):
        return "ENDFILE"
    else:
        return "OP"


line_no = 0
# words = input("Enter the input consisting of grammar and the text:")
for line in fileinput.input():
    print(line);
    line_no = line_no+1
    for w in word_tokenize(line):
        type_of_word = findType(w)
        print(w)
        print(type_of_word)
        print(line_no)
        print(ps.stem(w))
