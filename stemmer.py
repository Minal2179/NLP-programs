import re
import atexit
import fileinput
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

ps = PorterStemmer()

@atexit.register
def quit_gracefully():
    print("ENDFILE")

def findType(inputToken):
    if(re.match('^[-+]?[0-9]+$', inputToken)):
        return "INT"
    elif(re.match('[+-]?([0-9]*[.])?[0-9]+',inputToken)):
        return "DOUBLE"
    elif(re.match('\W',inputToken)):
        return "OP"
    elif (type(inputToken) is str):
        return "STRING"


# stdin input 
for line in fileinput.input():
    print(line);
    for w in word_tokenize(line):
        type_of_word = findType(w)
        if line.find('=') == -1:
            print(w, ' ', type_of_word, ' ', fileinput.lineno())
        else:
            print(w,' ',type_of_word,' ',fileinput.lineno(),' ',ps.stem(w))
