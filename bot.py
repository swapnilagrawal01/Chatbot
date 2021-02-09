from flask import Flask, render_template, request, session
import aiml
from req_libraries import similarity as s
import random
import re
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def index():
	session['sid'] = random.randint(1,10000) #uuid.uuid4()
	k.learn("std-startup.xml")
	k.respond("load aiml b", session.get('sid'))
	return render_template("index.html")

@app.route("/<query>")
def api(query):
	return res(query)


sent_check = s.Sent_Similarity() #Check what it is doing

k = aiml.Kernel()

DEFAULT_RESPONSES = ["I did not get you! Pardon please!","I couldn't understand what you just said! Kindly rephrase"
					 " what you said :-)", "What you are saying is out of my understanding! You can ask me" ]

EMPTY_RESPONSES = ["Say something! I would love to help you!","Don't hesitate. I'll answer your queries to the best"
				   " of my knowledge!","Say my friend!"]

ONE_WORD_RESPONSES = ["Please elaborate your query for me to understand!", "I could not understand your context, please say more!",
					  "Sorry, I could not get you! Please say something more for me to understand!"]
	

def matchingSentence(inp):
	f = open('database/questions.txt')
	match = "";
	max_score=0;
	for line in f.readlines():
		score = sent_check.symmetric_sentence_similarity(inp, line)
		if score > max_score:
			max_score = score
			match = line
	f.close()
	return match, max_score

def preprocess(inp):
	if(inp!=""):
		if inp[-1]=='.':
			inp = inp[:-1]
	# to remove . symbol between alphabets. Eg. E.G.C becomes EGC
	inp = re.sub('(?<=\\W)(?<=\\w)\\.(?=\\w)(?=\\W)','',inp) 
	# to remove - symbol between alphabet. Eg. E-G-C becomes EGC
	inp = re.sub('(?<=\\w)-(?=\\w)',' ',inp) 
	# to remove . symbol at word boundaries. Eg. .E.G.C. becomes E.G.C
	inp = re.sub('((?<=\\w)\\.(?=\\B))|((?<=\\B)\\.(?=\\w))','',inp)
	# to remove ' ' symbol in acronyms. Eg. E B C becomes EBC
	inp = re.sub('(?<=\\b\\w) (?=\\w\\b)','',inp)
	inp = inp.upper()
	return inp

def isKeyword(word):
	f = open('database/questions.txt','r')
	keywords = f.read().split()
#    print(keywords)
	if(word in keywords):
		return True
	else:
		return False

def res(inp):
	p_inp = preprocess(inp)
	inp = p_inp
	response = k.respond(inp, session.get('sid'))
	if(response=='No match'):
		# to invalidate wrong one-word input
		if(len(inp.split(" "))==1):
			if(isKeyword(inp)==False): 
				return(random.choice(ONE_WORD_RESPONSES))
				
		inp = matchingSentence(inp)
#        print(inp)

		#Checking for confidence
		response = k.respond(inp[0], session.get('sid'))
		confidence = inp[1]

		#Creating a Log File
		if(confidence < 0.5):
			log = open('database/invalidated_log.txt','a')
			log.write(p_inp+"\n")
			log.close()
			return(random.choice(DEFAULT_RESPONSES))
		else:
			response = re.sub(r'( )?(http:[%\-_/a-zA-z0-9\\.]*)','<a href="\\2">\\2</a>',response)       
			return(response)

	elif(response==""):
		return(random.choice(EMPTY_RESPONSES))
	else: 
		response = re.sub(r'( )?(http:[%\-_/a-zA-z0-9\\.]*)','<a href="\\2">\\2</a>',response)
		return (response)


if __name__ == "__main__":
	app.run()
	