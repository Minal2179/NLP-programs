import sqlite3

# initialize the connection to the database
def db_connection():
	connection = sqlite3.connect('chatdata.sqlite')
	cursor = connection.cursor()
	 
	# create the tables needed by the program
	create_table_request_list = [
	    'CREATE TABLE words(word TEXT UNIQUE)',
	    'CREATE TABLE sentences(sentence TEXT UNIQUE, used INT NOT NULL DEFAULT 0)',
	    'CREATE TABLE associations (word_id INT NOT NULL, sentence_id INT NOT NULL, weight REAL NOT NULL)',
	]
	for create_table_request in create_table_request_list:
	    try:
	        cursor.execute(create_table_request)
	    except:
	        pass
	return connection

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    The "answer" return value is True for "yes" or False for "no".
    - a Cut-and-Paste piece of code from Stack Overflow
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")