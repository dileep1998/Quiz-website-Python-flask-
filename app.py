from flask import Flask,flash,redirect,url_for,session,logging,request
from flask import render_template
import psycopg2
from wtforms import Form,StringField , TextAreaField,PasswordField,validators,SubmitField
from passlib.hash import sha256_crypt
from functools import wraps
import random 


x='QUIZ1'
y='QUIZ2'

app = Flask(__name__)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def index():
	return render_template('home.html')

@app.route('/onlinequiz')
@is_logged_in
def onlinequiz():
	return render_template('onlinequiz.html')


@app.route('/about')
@is_logged_in
def about():
	return render_template('about.html')	

@app.route('/contact')
@is_logged_in
def contact():
	return render_template('contact.html')


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=6,max=30)])
    email  = StringField('Email', [validators.Length(min=6,max=30)])
    password= PasswordField('Password', [
    	validators.DataRequired(),
    	validators.EqualTo('confirmpassword',message='Do not match passwords')
    	])
    confirmpassword= PasswordField('Confirm password')


@app.route('/register',methods=['GET','POST'])
def register():
	form = RegisterForm(request.form)
	if request.method=='POST' and form.validate():
		name=form.name.data
		email=form.email.data
		password=sha256_crypt.encrypt(str(form.password.data))
		conn = psycopg2.connect(database = "exam", user = "postgres", password = "1234", host = "localhost", port = "5432")
		cur=conn.cursor()
		print(name,email,password)
		cur.execute('INSERT INTO USERS(name,email,password) VALUES(%s,%s,%s)',(name,email,password))
		cur.execute("COMMIT")
		cur.close()
		flash("you are registered",'success')
		
	return render_template('register.html' , form=form)


@app.route('/quiz',methods=['GET','POST'])
@is_logged_in
def quiz():
        conn = psycopg2.connect(database = "exam", user = "postgres", password = "1234", host = "localhost", port = "5432")
        cur=conn.cursor()
        
        cur.execute("SELECT questions,options FROM " + x + "")
        record=cur.fetchall()
        d={}
       
        for row in record:
            q=row[0]
            o=row[1]
            d[row[0]]=row[1]
     
        return render_template('quiz1.html', o=d)

@app.route('/quiz1',methods=['GET','POST'])
@is_logged_in
def quiz1():
        conn = psycopg2.connect(database = "exam", user = "postgres", password = "1234", host = "localhost", port = "5432")
        cur=conn.cursor()
        cur.execute("SELECT questions,options FROM " + y + "")
        record=cur.fetchall()
        e={}

        for row in record:
            q=row[0]
            o=row[1]
            e[row[0]]=row[1]
        
        return render_template('quiz2.html', o=e)          


@app.route('/quiz_answers', methods=['POST'])
@is_logged_in
def quiz_answers():
    if request.method == 'POST':
        conn = psycopg2.connect(database = "exam", user = "postgres", password = "1234", host = "localhost", port = "5432")
        cur=conn.cursor()
        cur.execute("SELECT questions,options,answer FROM " + x + "")
        
        record=cur.fetchall()
        d={}
        l=[]
        correct=0
        j=0
        for row in record:
            q=row[0]
            o=row[1]
            l.append(row[2])
            d[row[0]]=row[1]
            
        for i in d.keys():
            a=request.form[i]
            if l[j]==a:
            	correct+=1
            j=j+1  	
        correct=str(correct)   
        speech="You have answered "+ correct +" questions correctly"
        flash(speech)
    return render_template('onlinequiz.html')

@app.route('/quiz_answers1', methods=['POST'])
@is_logged_in
def quiz_answers1():
    if request.method == 'POST':
        conn = psycopg2.connect(database = "exam", user = "postgres", password = "1234", host = "localhost", port = "5432")
        cur=conn.cursor()
        
        cur.execute("SELECT questions,options,answer FROM " + y + "")
        
        record=cur.fetchall()
        e={}
        l=[]
        correct=0
        j=0
        for row in record:
            q=row[0]
            o=row[1]
            e[row[0]]=row[1]
            l.append(row[2])

            
        for i in e.keys():
            b=request.form[i]
            if l[j]==b:
            	correct+=1
            j=j+1 
        correct=str(correct)     
        speech="You have answered "+ correct +" questions correctly"
        flash(speech)
    return render_template('onlinequiz.html')    
    	
	
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']
        conn = psycopg2.connect(database = "exam", user = "postgres", password = "1234", host = "localhost", port = "5432")

        # Create cursor
        cur = conn.cursor()

        # Get user by username
        cur.execute("SELECT * FROM users WHERE email = '%s'"%email)
        record=cur.fetchone()
        result=record[1]
        
        if result is not None:     
            password = record[2]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                
                session['logged_in'] = True
                session['email'] = email

                flash('You are now logged in', 'success')
                return render_template('home.html')
                
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            
            cur.close()         	   	
            

        else:

            error = 'email not found'
            return render_template('home.html', error=error)             	

    return render_template('login.html')


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)
    
