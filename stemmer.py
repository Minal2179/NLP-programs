import string
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

ps = PorterStemmer()

# example_words = ["pythoner","pythoning","pythonly","pythoned","python"]

# for w in example_words:
#     print(ps.stem(w))
def findType(inputToken):
    if(type(inputToken) is int):
        type_of_word = "INT"
    elif(type(inputToken) is str):
        type_of_word = "STRING"
    elif(type(inputToken) is float):
        type_of_word = "DOUBLE"
    elif(re.match(r'',inputToken)):
        type_of_word = "OP"
    elif():
        type_of_word = "ENDFILE"

words = input("Enter the input consisting of grammar and the text:")

for w in word_tokenize(words):
    findType(w)

    if(w == "="):
    stemmed_word = ps.stem(w)


    print(ps.stem(w))
