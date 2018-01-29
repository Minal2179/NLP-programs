import re
import sys
import fileinput
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from collections import defaultdict

grammar = defaultdict(list)
part_of_speech = set()

def find_type_of_word(input_token): #get the type of word after input is being processed by tokenizer
    if re.match('^[-+]?[0-9]+$', input_token):
        return "INT"
    elif re.match('[+-]?([0-9]*[.])?[0-9]+', input_token):
        return "DOUBLE"
    elif re.match('\W', input_token):
        return "OP"
    elif type('\w') is str:
        return "STRING"


def get_rhs(string): #get the rhs of the rule
    right = re.search(r'\^\s*(.*)\b', string)
    if right:
        return right.group(1).split()[0]
    else:
        return 0


def get_lhs(string): #get lhs of the rule
    left = re.findall(r'(?:^|(?:[->?!]\s))([a-zA-Z]+)', string)
    if left:
        final_lhs = left[0].strip()
        return final_lhs
    else:
        print(string[0])


def predictor(row_input): # finds the possible expansions of the grammar
    rhs = get_rhs(row_input[0])
    lhs = get_lhs(row_input[0])
    if lhs not in part_of_speech:
        for each in grammar[rhs]:
            to_append = [rhs + " -> " + " ^ " + each, row_input[2], row_input[2], "Predictor"]
            if to_append not in s[row_input[2]]:
                enqueue(row_input[2], to_append)


def scanner(row_input, i): # scans the input word so as to get a match with the parts of speech
    fetched = get_rhs(row_input[0])
    if i < len(grammar["W"]) and grammar["W"][i] in grammar[fetched]:
        to_append = [fetched + " -> " + grammar["W"][i] + " ^ ", row_input[2], row_input[2] + 1, "Scanner"]
        enqueue(row_input[2] + 1, to_append)


def completer(row_input): # increments one step when a match is found by the scanner
    lhs = get_lhs(row_input[0])
    for each in s[row_input[1]]:
        if ("^" + " " + lhs) in each[0] and lhs != "S":
            left = each[0].split('^')[0]
            right = each[0].split('^')[1]
            mid = right.split(" ")[1]
            to_append = [left + mid + " ^ " + " ".join(right.split()[1:]), each[1], row_input[2], "Completer"]
            enqueue(row_input[2], to_append)


def earley_parser(words): #Initialize a dummy state and calls predictor, scanner and completer to give the final result
    enqueue(0, ["Z -> ^ S", 0, 0,"Dummy Start State"])
    for i in range(len(words) + 1):
        for row_input in s[i]:
            rhs = get_rhs(row_input[0])
            if rhs != 0 and rhs not in part_of_speech:
                predictor(row_input)
            elif rhs != 0 and rhs in part_of_speech:
                scanner(row_input, i)
            else:
                completer(row_input)


def enqueue(state, chart_entry): # adds the passed rules onto a chart
    i = 0
    for item in s[state]:
        if item[0] == chart_entry[0]:
            i = 1
    if i == 0:
        s[state].append(chart_entry)


def main(): # Stemmer code followed by the grammar and parts of speech generation
    ps = PorterStemmer()
    pattern_line = ""
    array = []
    count = tempc = temps = colon = semi = 0
    for input_line in fileinput.input():
        for w in word_tokenize(input_line): ## Stem code begins here - word by
            if count == 0:
                print("Stemmer: ")
                count += 1
            type_of_word = find_type_of_word(w)
            if input_line.find('=') == -1:
                if re.search('\|*\s*([a-zA-Z\-\s]+)', w) is not None:
                    stem_parts = re.split('\|', w)
                    for i in range(len(stem_parts)):
                        if len(stem_parts) > 1 and i == 1 and stem_parts[i] is not '':
                            print('|', ' ', 'OP', ' ', fileinput.lineno())
                        if stem_parts[i] is '':
                            print('|', ' ', 'OP', ' ', fileinput.lineno())
                        else:
                            type_of_word = find_type_of_word(stem_parts[i])
                            print(stem_parts[i], ' ', type_of_word, ' ', fileinput.lineno())
                else:
                    print(w, ' ', type_of_word, ' ', fileinput.lineno())
            else:
                if re.search('[A-Za-z]', w) is not None and w != "W":
                    print(w, ' ', type_of_word, ' ', fileinput.lineno(), ' ', ps.stem(w).lower(), ' ')
                else:
                    print(w, ' ', type_of_word, ' ', fileinput.lineno()) ## Stem code ends here
        input_line.strip()
        if "#" in input_line:
            continue
        if pattern_line and pattern_line[-1] == ";":
            array.append(pattern_line)
            pattern_line = ""
        if input_line and input_line[-1] == ";":
            pattern_line = pattern_line + input_line
            array.append(pattern_line)
            pattern_line = ""
        elif ":" in input_line:
            if pattern_line:
                array.append(pattern_line)
            pattern_line = input_line
        else:
            pattern_line += input_line
    if pattern_line:
        array.append(pattern_line)
    for line in array:
        sent = re.search('[^(a-zA-Z|\*|\s|\:|\=|\;|\-|\||\#|\.|\?|\!|\,|\'|\")]', line)
        if sent is not None and sent.group(0) is not None:
            print("Input is invalid : Illegal!!!")
            exit("Input is invalid : Illegal!!!")
        elif line.isspace():
            continue

        semi = temps + line.count(';')
        colon = tempc + line.count(':')
        if semi == colon:
            semi = colon = temps = tempc = 0
        elif semi > colon:
            print("Input is erroneous: Illegal!!!!")
            sys.exit("Input is erroneous: Illegal!!!!")
        else:
            tempc = colon
            temps = semi

        for each in line.split(';'):
            each = each.lstrip()
            if re.search('^([a-zA-Z\-]+)\s*[\:|\=]+\s*([a-zA-Z\-\|\*\s*\'\"\,\.\?\!]*)', each) is not None:
                parts = re.search('([a-zA-Z\-]+)\s*[\:|\=]+\s*([a-zA-Z\-\|\*\s*\'\"\,\.\?\!]*)', each)
                lhs = parts.group(1)
                if parts.group(2).find('|') == -1 and lhs == 'W':
                    subpart = re.split('\s+', parts.group(2))
                else:
                    subpart = re.split('\s*\|\s*', parts.group(2))
            elif re.findall('\s*\|\s*[a-zA-Z\-\s]+', each) is not None:
                childpart = re.findall('\s*\|\s*([a-zA-Z\-\s]+)', each)
                for x in childpart:
                    childsubpart = x
                    childsubpart = re.sub('[\n\t\r]+', ' ', childsubpart)
                    grammar[lhs].append(childsubpart.rstrip())
            elif re.search('\#\s*[a-zA-Z]+', each) is not None:
                continue

            for i in range(len(subpart)):
                if subpart[i].islower():
                    if lhs != 'W':
                        part_of_speech.add(lhs)
                if lhs == 'W':
                    a = re.search('[a-zA-Z\-]+', subpart[i])
                    if subpart[i] == '' or a is None:
                        continue
                    b = a.group(0)
                    rhs = ps.stem(b).lower()
                else:
                    rhs = subpart[i]
                    rhs = re.sub('[\n\t\r]+', ' ', rhs)
                grammar[lhs].append(rhs.rstrip())


    if semi < colon:
        print("Input is erroneous: Semicolon missing!!!")
        sys.exit("Input is erroneous: Semicolon missing!!!")
    print("ENDFILE")
    if not grammar or 'W' not in grammar:
        print("No Input: Illegal!!!")
        sys.exit("No Input: Illegal!!!")


def initialize(words): #grammar is fed to the earley parser after initial checks
    global s
    s = [[] for i in range(len(words) + 1)]
    for word in grammar["W"]:
        found = 0
        for x in grammar:
            if x != "W":
                for j in grammar[x]:
                    if j == word:
                        found += 1

        if found == 0:
            print("Grammar is incorrect: Illegal!!!!")
            exit("Grammar is incorrect: Illegal!!!!")
    earley_parser(grammar["W"])


def create_parse_chart(): # creates a chart out of the given parsing logic
    print("\nParsed Chart: ")
    chart_number = 0
    check_chart = 0
    for each in s:
        for elem in each:
            if check_chart == elem[2]:
                print("\nChart [",elem[2],"]\n")
                check_chart += 1
            print("S",chart_number," ",elem[0],"\t\t\t","[",elem[1],",",elem[2],"]","\t\t",elem[3])
            chart_number += 1


main()
initialize(grammar["W"])
create_parse_chart()

