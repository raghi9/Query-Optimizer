from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import urllib2
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/def_repository'
db = SQLAlchemy(app)

class Example(db.Model):
	__tablename__ = 'def'		
	name = db.Column('name' , db.String)
	des = db.Column('des', db.String)
	keyword = db.Column('keyword', db.String , primary_key = True)

	def __init__(self , name , des , keyword):
		self.name = name
		self.des = des
		self.keyword = keyword

an = []
keys = []

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
    	keys[:]=[]
        an.append(request.form['search'])
        #print(an);
        words=an[0].split(',')
        search(words)
        an[:] = [] 
        return render_template("1.html",key=keys,an=words,len_an=len(words),len_key=len(keys))
    
    return render_template('1.html')

def search(words):
	print(words)
	if len(words)==1:
		row = Example.query.filter_by(name=words).first()
		if row == None:
			scraping_for_db(words[0])
		row = Example.query.filter_by(name=words).all()
		for i in row:
			keys.append(i.des)
		

	elif len(words)==2:
		for word in words:
			row = Example.query.filter_by(name=word).first()
			if row == None:
				scraping_for_db(word)
		scraping_for_result(words[0],words[1])	


	# elif len(words)>2:
	# 	for word in words:
	# 		row = Example.query.filter_by(name=word).first()
	# 		if row == None:
	# 			scraping_for_db(word)
	# 	#similarity in a diff. way
				
def scraping_for_db(word):
	count = 0
	search = "http://wordnetweb.princeton.edu/perl/webwn?s="+word+"&sub=Search+WordNet&o2=&o0=1&o8=1&o1=1&o7=&o5=&o9=&o6=&o3=&o4=&h=000"
	page = urllib2.urlopen(search)
	soup = BeautifulSoup(page, "html.parser")
	flag = False
	for i in soup.find_all("li"):
		pos=i.a.next_sibling.next_element
		pos = pos[2:len(pos)-2]
		if flag == True:
			if pos!=pos1:
				pos1=pos
				count=0
		else:
			pos1=pos
			flag=True
		gloss=i.i.previous_element
		gloss = gloss[2:len(gloss)-2]
		count = count + 1
		s=""
		s= s+word+"#"+pos+"#"+str(count)
		new_row= Example(word, gloss , s)
		db.session.add(new_row)
		db.session.commit()


def scraping_for_result(a,b):
	search='http://maraca.d.umn.edu/cgi-bin/similarity/similarity.cgi?word1=' + a + '&senses1=all&word2=' + b + '&senses2=all&measure=path&rootnode=yes&sense=yes&showform=no'
	page = urllib2.urlopen(search)
	soup = BeautifulSoup(page, "html.parser")
	all_tr=soup.find_all('tr')
	if len(all_tr)==1:
		return

	else:
		count = 0
		for i in all_tr:
			if count == 0:
				count = count+1
				continue
			elif count>3:
				break					
			else:
				w1=i.td.next_sibling.a.next_element
				w2=i.td.next_sibling.next_sibling.a.next_element
				row1=Example.query.filter_by(keyword=w1).first()
				row2=Example.query.filter_by(keyword=w2).first()
				keys.append(row1.des)
				keys.append(row2.des)
				count=count+1


if __name__ == '__main__':
	app.run(debug=True)
