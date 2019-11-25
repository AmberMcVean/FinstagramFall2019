#Import Flask Library
from flask import  Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib

SALT = 'cs3083'

#Initialize the app from Flask
app = Flask(__name__)

#Step 1 make all the connections to mySQL
conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       password='',
                       db='finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function-this is the first page the user/client sees
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password'] + SALT
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT username, password FROM person WHERE username = %s and password = %s'
    cursor.execute(query, (username, hashed_password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid username or password.'
        return render_template('login.html', error=error)

    # Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password'] + SALT
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    bio = request.form['bio']


    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists."
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashed_password, firstname, lastname, bio))
        conn.commit()
        cursor.close()
        return render_template('index.html')\


@app.route('/home')
def home():
    user = session['username']
    cursor = conn.cursor();
    isFollowing = 'SELECT username_followed FROM follow WHERE username_follower = %s AND followstatus = TRUE'
    isShared= 'SELECT photoID FROM sharedWith WHERE (%s, groupOwner, groupName) IN (SELECT * FROM belongTo)'
    query = 'SELECT photoID, photoPoster FROM Photo WHERE (' + isFollowing + ') AND (allFollowers = TRUE OR (' + isShared + ')) ORDER BY postingdate DESC'
    cursor.execute(query, (user, user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data)

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)