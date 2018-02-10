import re
import utils
from collections import Counter
from string import punctuation
from math import sqrt

weight = 0
ACCURACY_THRESHOLD = 0.03
NO_DATA = "Sorry I don't know what to say"

def get_id(entityName, text, cursor):
    """Retrieve an entity's unique ID from the database, given its associated text.
    If the row is not already present, it is inserted.
    The entity can either be a sentence or a word."""
    tableName = entityName + 's'
    columnName = entityName
    cursor.execute('SELECT rowid FROM ' + tableName + ' WHERE ' + columnName + ' = ?', (text,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute('INSERT INTO ' + tableName + ' (' + columnName + ') VALUES (?)', (text,))
        return cursor.lastrowid
 
def get_words(text):
    """Retrieve the words present in a given string of text.
    The return value is a list of tuples where the first member is a lowercase word,
    and the second member the number of time it is present in the text."""
    wordsRegexpString = '(?:\w+|[' + re.escape(punctuation) + ']+)'
    wordsRegexp = re.compile(wordsRegexpString)
    wordsList = wordsRegexp.findall(text.lower())
    return Counter(wordsList).items()


def set_association(words, sentence_id, cursor):
    """ Pass in "words" which is a list of tuples - each tuple is word,count
    ("a_word" and count of occurences - i.e. ("the", 3) means the occurred 3 times in sentence)
    Nothing is returned by this function - it just updates the associations table in the database
    
    If current association for a word_id is 0, a new word-sentence association is added
    
    If current association for a word_id is > 0, the word-sentence association is updated with a new weight
    which is just the existing association weight (passed back by get_association) and the new weight
    """

    words_length = sum([n * len(word) for word, n in words]) # int giving number of chars in words
    
    # Looping through Bot-Words, associating them with Human Sentence
    for word, n in words:                 
    
        word_id = get_id('word', word, cursor) # if the ID doesn't exist, a new word + hash ID is inserted
        weight = sqrt(n / float(words_length))  # repeated words get higher weight.  Longer sentences reduces their weight
                
        #Association shows that a Bot-Word is associated with a Human-Sentence
        # Bot learns by associating our responses with its words
        association = get_association(word_id,sentence_id, cursor)
        if association > 0:                                            
            cursor.execute('UPDATE associations SET weight = ? WHERE word_id = ? AND sentence_id = ?',(association+weight,word_id,sentence_id))
            cursor.execute('INSERT INTO associations VALUES (?, ?, ?)', (word_id, sentence_id, weight))
    connection.commit()

 

def get_association(word_id,sentence_id, cursor):
    """Get the weighting associating a Word with a Sentence-Response
    If no association found, return 0
    This is called in the set_association routine to check if there is already an association
    
    associations are referred to in the get_matches() fn, to match input sentences to response sentences
    """
    cursor.execute('SELECT weight FROM associations WHERE word_id AND sentence_id')
    row = cursor.fetchone()
    print(row)
    
    if row:
        weight = row[0]
    else:
        weight = 0
    return weight

def get_matches(words, cursor):
    """ Retrieve the most likely sentence-answer from the database
    pass in humanWords, calculate a weighting factor for different sentences based on data in associations table  
    """
    results = []
    listSize = 10
    
    # Removed temp tables due to  GTID configuration issue in mySQL
    cursor.execute('CREATE TEMPORARY TABLE results(sentence_id TEXT, sentence TEXT, weight REAL)')

    
    # calc "words_length" for weighting calc
    words_length = sum([n * len(word) for word, n in words])  
    
    for word, n in words:
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO results SELECT associations.sentence_id, sentences.sentence, ?*associations.weight/(4+sentences.used) FROM words INNER JOIN associations ON associations.word_id=words.rowid INNER JOIN sentences ON sentences.rowid=associations.sentence_id WHERE words.word=?', (weight, word,))
   

    cursor.execute('SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
    # Fetch an ordered "listSize" number of results
    for i in range(0,listSize):
        row = cursor.fetchone()
        print(row)
        if row:
            results.append([row[0], row[1], row[2]])
        else:
            break
    #cursor.execute('DROP TEMPORARY TABLE results')
    cursor.execute('DROP TABLE results')
    return results

def feedback_stats(sentence_id, cursor, previous_sentence_id = None, sentiment = True):
    """
    Feedback usage of sentence stats, tune model based on user response.
    Simple BOT Version 1 just updates the sentence used counter
    """
    cursor.execute('UPDATE sentences SET used=used+1 WHERE rowid=?', (sentence_id,))
    
def train_me(inputSentence, responseSentence, cursor):
    inputWords = get_words(inputSentence) #list of tuples of words + occurrence count
    responseSentenceID = get_id('sentence', responseSentence, cursor) 
    set_association(inputWords, responseSentenceID, cursor)
    
def chat_flow(cursor, humanSentence, weight):
   
    # Take the human-words and try to find a matching response based on a weighting-factor
    humanWords = get_words(humanSentence)        
    matches = get_matches(humanWords, cursor)    #get_matches returns ordered list of matches for words:
                                                 #                         sentence_id, sentence, weight 
    trainMe = False # if true, the bot requests some help
    
    if len(matches) == 0:
        botSentence = NO_DATA
        trainMe = True
    else:
        sentence_id, botSentence, weight = matches[0]
        if weight > ACCURACY_THRESHOLD:
            # tell the database the sentence has been used and feedback other stats / weighting updates
            feedback_stats(sentence_id, cursor)
            train_me(botSentence, humanSentence, cursor)
        else:
            botSentence = NO_DATA
            trainMe = True
                        
    return botSentence, weight, trainMe

    
if __name__ == "__main__":    
    
    print("Starting Bot...") 
    # initialize the connection to the database
    print("Connecting to database...")
    connection = utils.db_connection() 
    cursor = connection.cursor() 
    print("...connected")
    
    trainMe = False
    botSentence = 'Hello!'
    while True:
        # Output bot's message
        print('Bot> ' + botSentence)
        if trainMe:
            print('Bot> Please can you train me - enter a response for me to learn (Enter to Skip)' )
            previousSentence = humanSentence
            humanSentence = raw_input('>>> ').strip()
            
            if len(humanSentence) > 0:
                train_me(previousSentence, humanSentence, cursor)
                print("Bot> Thanks I've noted that" )
            else:
                print("Bot> OK, moving on..." )
                trainMe = False
         
        # Ask for user input; if blank line, exit the loop
        humanSentence = raw_input('>>> ').strip()
        print(humanSentence)
        if humanSentence == '' or humanSentence.strip(punctuation).lower() == 'quit' or humanSentence.strip(punctuation).lower() == 'exit':
            break
    
        botSentence, weight, trainMe = chat_flow(cursor, humanSentence, weight)
    
        connection.commit()






''' 
B = 'Hello!'
while True:
    # output bot's message
    print('B: ' + B)
    # ask for user input; if blank line, exit the loop
    H = raw_input('H: ').strip()
    if H == '':
        break
    # store the association between the bot's message words and the user's response
    words = get_words(B)
    words_length = sum([n * len(word) for word, n in words])
    sentence_id = get_id('sentence', H)
    for word, n in words:
        word_id = get_id('word', word)
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO associations VALUES (?, ?, ?)', (word_id, sentence_id, weight))
    connection.commit()
    # retrieve the most likely answer from the database
    cursor.execute('CREATE TEMPORARY TABLE results(sentence_id INT, sentence TEXT, weight REAL)')
    words = get_words(H)
    words_length = sum([n * len(word) for word, n in words])
    for word, n in words:
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO results SELECT associations.sentence_id, sentences.sentence, ?*associations.weight/(4+sentences.used) FROM words INNER JOIN associations ON associations.word_id=words.rowid INNER JOIN sentences ON sentences.rowid=associations.sentence_id WHERE words.word=?', (weight, word,))
    # if matches were found, give the best one
    cursor.execute('SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
    row = cursor.fetchone()
    cursor.execute('DROP TABLE results')
    # otherwise, just randomly pick one of the least used sentences
    if row is None:
        cursor.execute('SELECT rowid, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()
    # tell the database the sentence has been used once more, and prepare the sentence
    B = row[1]
    cursor.execute('UPDATE sentences SET used=used+1 WHERE rowid=?', (row[0],))
'''