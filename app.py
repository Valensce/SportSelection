from flask import Flask, request, session, redirect, url_for, render_template, flash
import sqlite3 as db
import re 
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.secret_key = 'This_Should_Be_Random_And_Impossible_To_Crack'

@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
    
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    conn = db.connect("user_data.db")
    conn.row_factory = db.Row 
    cursor = conn.cursor()
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using SQLite
        cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['user_id'] = account['user_id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username and/or password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username and/or password')
 
    return render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = db.connect("user_data.db")
    conn.row_factory = db.Row
    cursor = conn.cursor()
 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Check if account exists using SQLite
        cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO Users (fullname, username, password, email) VALUES (?, ?, ?, ?)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')
   
   
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('user_id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
  
@app.route('/profile')
def profile():
    conn = db.connect("user_data.db")
    conn.row_factory = db.Row
    cursor = conn.cursor()
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM Users WHERE user_id = ?', [session['user_id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
 
@app.route('/students')
def students():
    conn = db.connect("user_data.db")
    cursor = conn.cursor() #A cursor is just like a file handler that we can use to perform operations on the database.
    conn.row_factory = db.Row
    s = "SELECT * FROM Users" #Save the SQL query as a variable
    cursor.execute(s) # Execute the SQL
    list_users = cursor.fetchall()#fetches all the rows of a query result
    return render_template('students.html', list_users = list_users)#Makes the list_users variable available in index.html

@app.route('/edit_user/<user_id>', methods = ['POST', 'GET'])
def get_student(user_id):
    conn = db.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id)) #Selects all fields for the current id
    data = cursor.fetchall() #stores the data in a variable
    cursor.close()
    return render_template('edit_user.html', Users = data[0]) #Makes data available in the edit_student.html template for the current student
 
@app.route('/update_user/<user_id>', methods=['POST']) #Data from the form from edit_student.html is posted to this route
def update_student(user_id):
    if request.method == 'POST': #Data from the form from edit_student.html is requested
        fullname = request.form['fullname'] 
        username = request.form['username']
        email = request.form['email']
        
        conn = db.connect("user_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students
            SET fname = ?,
                lname = ?,
                email = ?
            WHERE user_id = ?
        """, (fullname, username, email, user_id)) #Details are updated on execution of the cursor
        flash('Student Updated Successfully') #Message is flashed to the user
        conn.commit() #Changes are committed (saved) to the database
        return redirect(url_for('Students')) #User is redirected to the "Students" function (this is in the root route).

@app.route('/delete_user/<string:user_id>', methods = ['POST','GET'])
def delete_user(user_id):

    conn = db.connect("user_data.db")
    conn.row_factory = db.Row #Maybe don't need this
    cursor = conn.cursor()

    cursor.execute('DELETE FROM Users WHERE user_id = {0}'.format(user_id))
    conn.commit()
    flash('Student Removed Successfully')
    return redirect(url_for('students'))


@app.route('/sports')
def sports():
    conn = db.connect("user_data.db")
    cursor = conn.cursor() #A cursor is just like a file handler that we can use to perform operations on the database.
    conn.row_factory = db.Row
    s = "SELECT * FROM sports" #Save the SQL query as a variable
    cursor.execute(s) # Execute the SQL
    list_sports = cursor.fetchall()#fetches all the rows of a query result
    return render_template('sports.html', list_sports = list_sports)#Makes the list_sports variable available in index.html

@app.route('/selection/<sport_id>', methods = ['POST','GET'])
def selection(sport_id):
    conn = db.connect("user_data.db")
    cursor = conn.cursor() #A cursor is just like a file handler that we can use to perform operations on the database.
    conn.row_factory = db.Row
    user_id = session['user_id']

    cursor.execute('''
        INSERT INTO student_sports (user_id, sport_id)
        SELECT Users.user_id, sports.sport_id
        FROM Users
        CROSS JOIN sports
        WHERE Users.user_id = ?
        AND sports.sport_id= ?;
    ''',(user_id, sport_id))
    
    cursor.execute("SELECT * FROM sports WHERE sport_id = ?", (sport_id))
    list_sports = cursor.fetchall()#fetches all the rows of a query result
    return render_template('selection.html', list_sports = list_sports)#Makes the list_sports variable available in index.html

@app.route('/add_student', methods=['POST'])
def add_student():
    conn = db.connect("user_data.db")
    cursor = conn.cursor()
    if request.method == 'POST':
        username = request.form['username'] #Gets data from the form with a name of fname (this is in the index.html view)
        fullname = request.form['fullname'] #Gets data from the form with a name of lname (this is in the index.html view)
        email = request.form['email'] #Gets data from the form with a name of email (this is in the index.html view)
        cursor.execute("INSERT INTO Users (username, fullname, email) VALUES (?,?,?)", (username, fullname, email))
        conn.commit()
        flash('Student added successfully')
        return redirect(url_for('students'))

@app.route('/add_sport', methods=['POST'])
def add_sport():
    conn = db.connect("user_data.db")
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name'] #Gets data from the form with a name of fname (this is in the index.html view)
        teacher = request.form['teacher'] #Gets data from the form with a name of lname (this is in the index.html view)
        location = request.form['location'] #Gets data from the form with a name of email (this is in the index.html view)
        cursor.execute("INSERT INTO sports (name, teacher, location) VALUES (?,?,?)", (name, teacher, location))
        conn.commit()
        flash('Sport added successfully')
        return redirect(url_for('sports'))

@app.route('/update_sport/<sport_id>', methods=['POST']) #Data from the form from edit_student.html is posted to this route
def update_sport(sport_id):
    if request.method == 'POST': #Data from the form from edit_student.html is requested
        name = request.form['name'] 
        location = request.form['location']
        teacher = request.form['teacher']
        
        conn = db.connect("user_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sports
            SET name = ?,
                location = ?,
                teacher = ?
            WHERE sport_id = ?
        """, (name, location, teacher, sport_id)) #Details are updated on execution of the cursor
        flash('Student updated successfully') #Message is flashed to the user
        conn.commit() #Changes are committed (saved) to the database
        return redirect(url_for('sports')) #User is redirected to the "Students" function (this is in the root route).

@app.route('/edit_sport/<sport_id>', methods = ['POST', 'GET'])
def get_sport(sport_id):
    conn = db.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sports WHERE sport_id = ?', (sport_id)) #Selects all fields for the current id
    data = cursor.fetchall() #stores the data in a variable
    cursor.close()
    return render_template('edit_sport.html', sports = data[0]) #Makes data available in the edit.html template for the current student

@app.route('/delete_sport/<string:sport_id>', methods = ['POST','GET'])
def delete_sport(sport_id):

    conn = db.connect("user_data.db")
    conn.row_factory = db.Row #Maybe don't need this
    cursor = conn.cursor()

    cursor.execute('DELETE FROM sports WHERE sport_id = {0}'.format(sport_id))
    conn.commit()
    flash('Sport removed successfully')
    return redirect(url_for('sports'))

if __name__ == "__main__":
    app.run(debug=True)