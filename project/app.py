import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

import requests
import urllib.parse
from functools import wraps


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cs50bank.db")

ACTIONS = [
    "Change username",
    "Change password",
    "Delete account"
]


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show transactions"""
    user_id = session['user_id']
    account_number = db.execute('SELECT account_number FROM users WHERE id = ?', user_id)[0]['account_number']
    username = db.execute('SELECT username FROM users WHERE id = ?', user_id)[0]['username']

    current_balance = db.execute('SELECT initial_deposit FROM users WHERE id = ?', user_id)[0]['initial_deposit']

    views =  db.execute('SELECT description, method, withdrawal, deposit, accountNumber, balance, time FROM transactions WHERE user_id = ? ORDER BY time DESC', user_id)

    return render_template('index.html', views=views, balance=current_balance, username=username, account_number=account_number)


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    """Make deposits"""
    if (request.method =='POST'):
        description = request.form.get('description')
        method = request.form.get('method')

        if not description:
            flash('Enter a description please!', 'danger')
            return redirect('/deposit')

        elif not method:
            flash('Choose a method please!', 'danger')
            return redirect('/deposit')
        try:
            deposit = int(request.form.get('deposit'))
        except:
            flash('Amount must be a number.', 'danger')
            return redirect('/deposit')

        user_id = session['user_id']

        if deposit <= 0:
            flash('amount must be a positive number', 'danger')
            return redirect('/deposit')

        db.execute('INSERT INTO transactions(user_id, description, method, deposit) VALUES(?, ?, ?, ?)',
                    user_id, description, method, deposit)

        # Update balance after each deposit
        initial_deposit = db.execute('SELECT initial_deposit FROM users WHERE id = ?', user_id)[0]['initial_deposit']

        amount = initial_deposit + deposit

        db.execute('UPDATE users SET initial_deposit = ? WHERE id = ?', amount, user_id)
        db.execute('UPDATE transactions SET balance = ? WHERE user_id = ? AND time = CURRENT_TIMESTAMP', amount, user_id)

        flash('Operation successfully completed!', 'success')
        return redirect('/')

    else:
        return render_template('deposits.html')


@app.route("/withdrawal", methods=["GET", "POST"])
@login_required
def withdrawal():
    """ Make withdrawals """
    if request.method == 'POST':
        description = request.form.get('description')
        method = request.form.get('method')
        account_numberR = request.form.get('account_number')

        if not description:
                flash('Describe this expenditure please!', 'danger')
                return redirect('/withdrawal')

        elif not method:
                flash('Choose a method please!','danger')
                return redirect('/withdrawal')

        try:
                withdrawal = int(request.form.get('amount'))

        except:
                flash('amount must be a number','danger')
                return redirect('/withdrawal')

        if withdrawal <= 0:
                flash('amount must be a positive number')
                return redirect('/withdrawal')

        user_id = session['user_id']

        initial_deposit = db.execute('SELECT initial_deposit FROM users WHERE id = ?', user_id)[0]['initial_deposit']

        #find sender account number
        account_numberS = db.execute('SELECT account_number FROM users WHERE id = ?', user_id)[0]['account_number']

        if initial_deposit < withdrawal:
            flash('Not enough cash', 'danger')
            return redirect('/withdrawal')

        if (method == 'Payment'):
            # Insert transaction into table transactions
            db.execute('INSERT INTO transactions(user_id, description, method, withdrawal) VALUES(?, ?, ?, ?)',
                        user_id, description, method, withdrawal)

            # Update balance after each withdraw
            balance = initial_deposit - withdrawal

            db.execute('UPDATE users SET initial_deposit = ? WHERE id = ?', balance, user_id)
            db.execute('UPDATE transactions SET balance = ? WHERE user_id = ? AND time = CURRENT_TIMESTAMP', balance, user_id)

            flash('Operation successfully completed', 'success')
            return redirect('/')

        else:
            if not account_numberR:
                flash('You must provide the account number you want to transfer money to', 'danger')
                return redirect('/withdrawal')

            elif account_numberR == account_numberS:
                flash('You must provide an account number that differs than yours ', 'danger')
                return redirect('/withdrawal')

            # Update transactions for sender
            else:
                db.execute('INSERT INTO transactions(user_id, description, method, withdrawal, accountNumber) VALUES(?, ?, ?, ?, ?)',
                            user_id, description, method, withdrawal, account_numberR)

                # Update balance after each withdraw (for sender account)
                balanceS = initial_deposit - withdrawal

                db.execute('UPDATE users SET initial_deposit = ? WHERE id = ?', balanceS, user_id)
                db.execute('UPDATE transactions SET balance = ? WHERE user_id = ? AND time = CURRENT_TIMESTAMP', balanceS, user_id)

                # Update after each withdraw (for receiver account)
                initial_depositR = db.execute('SELECT initial_deposit FROM users WHERE account_number = ?', account_numberR)[0]['initial_deposit']
                print(f'\n\n{initial_depositR}\n\n')

                balanceR = initial_depositR + withdrawal
                print(f'\n\n{balanceR}\n\n')

                # Update balance receiver
                db.execute('UPDATE users SET initial_deposit = ? WHERE account_number = ?', balanceR, account_numberR)
                print(f'\n\n{balanceR}\n\n')

                #find receiver id
                id_R = db.execute('SELECT id FROM users WHERE account_number = ?', account_numberR )[0]['id']

                #find receiver user_id
                user_idR = db.execute('SELECT transactions.user_id FROM transactions JOIN users ON users.id = transactions.user_id WHERE users.account_number = ?', account_numberR)[0]['user_id']

                # Update transactions for receiver
                db.execute('INSERT INTO transactions(user_id, description, method, deposit, accountNumber) VALUES(?, ?, ?, ?, ?)',
                            user_idR, description, method, withdrawal, account_numberS)

                #update balance reciever
                db.execute('UPDATE transactions SET balance = ? WHERE user_id = ? AND time = CURRENT_TIMESTAMP', balanceR, user_idR)

                flash('Operation successfully completed', 'success')
                return redirect('/')

    else:
        return render_template('withdrawal.html')


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """change username, password and delete account"""

    # Actions: Change username, Change password, Delete account
    if (request.method =='POST'):
        # Action
        action = request.form.get('action')

        # New username
        new_username = request.form.get('new_username')
        user_confirmation = request.form.get('user_confirmation')
        # New password
        current_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        pswd_confirmation = request.form.get('confirmation')
        # Delete account
        password = request.form.get('password')
        username = request.form.get('username')
        user_id = session['user_id']

        if not action:
            flash('Define an action please!', 'danger')
            return redirect('/settings')

        # Change username
        if action == "Change username":

            if not new_username:
                flash('Enter a new username please!', 'danger')
                return redirect('/settings')

            elif not user_confirmation:
                flash('Confirm username please!', 'danger')
                return redirect('/settings')

            elif new_username != user_confirmation:
                flash('Username does not match, try again', 'danger')
                return redirect('/settings')

            try:
                db.execute('UPDATE users SET username = ? WHERE id = ?', new_username, user_id)
                flash('Username has been successfully changed', 'success')
                return redirect("/")

            except:
                flash('Username alredy exists', 'danger')
                return redirect('/settings')

        # Change password
        elif action == "Change password":

            if not current_password:
                flash('Enter current password please!','danger')
                return redirect('/settings')

            elif not new_password:
                flash('Enter new password please!', 'danger')
                return redirect('/settings')

            elif not pswd_confirmation:
                flash('Confirm password please!', 'danger')
                return redirect('/settings')

            elif new_password != pswd_confirmation:
                flash('Passwords do not match, try again', 'danger')
                return redirect('/settings')

            # Query database for current password
            rows1 = db.execute("SELECT * FROM users WHERE id = ?", user_id)

            # Ensure current password is correct
            if len(rows1) != check_password_hash(rows1[0]['hash'], current_password):
                flash("current password invalid", "danger")
                return redirect('/settings')

            new_hash = generate_password_hash(new_password)

            try:
                db.execute('UPDATE users SET hash = ? WHERE id = ?', new_hash, user_id)
                flash('Password has been successfully changed', 'success')
                return redirect("/")

            except:
                flash('Action failed: password not changed', 'danger')
                return redirect("/")

        # Delete account
        elif action == "Delete account":

            if not username:
                flash('Enter username please!', 'danger')
                return redirect('/settings')

            if not password:
                flash('Enter password please!', 'danger')
                return redirect('/settings')

            #Ensure the username is the one logged in
            if username == db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]['username']:
                # Query database for username
                rows2 = db.execute("SELECT * FROM users WHERE id = ?", db.execute("SELECT id FROM users WHERE username = ?", username)[0]['id'])

            else:
                flash('Username incorrect.', 'danger')
                return redirect('/settings')

            # Ensure username exists and password is correct
            if len(rows2) != 1 or not check_password_hash(rows2[0]["hash"], password):
                flash("invalid password", "danger")
                return redirect('/settings')

            try:
                db.execute('DELETE FROM transactions WHERE user_id = ?', user_id)
                db.execute('DELETE FROM users WHERE id = ?', user_id)
                flash('Operation completed. Account has been deleted', 'success')
                return redirect('/login')

            except:
                flash('Ation failed: account not deleted')
                return redirect('/')

    else:
        return render_template('settings.html', actions=ACTIONS)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        # Ensure username was submitted
        if not username:
            flash("You must provide username", "danger")
            return redirect('/login')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("You must provide password", "danger")
            return redirect('/login')

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password", "danger")
            return redirect('/login')

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash('Hello ' + username + ', welcome to your bank account online interface!', 'primary')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if (request.method =='POST'):
        username = request.form.get('username')
        account_number = request.form.get('accountNumber')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            flash('You must provide a user name', 'danger')
            return redirect('/register')

        if not account_number.isnumeric():
            flash('Invalid account number, try again!', 'danger')
            return redirect('/register')

        elif len(account_number) < 10:
            flash('Account number must be equal or greater then 10 digits.')
            return redirect('/register')

        elif not password:
            flask('You must provide a password', 'danger')
            return redirect('/register')

        elif not confirmation:
            flash('You must confirm your password', 'danger')
            return redirect('/register')

        elif password != confirmation:
            flash('Passwords do not match', 'danger')
            return redirect('/register')

        hash = generate_password_hash(password)

        try:
            db.execute('INSERT INTO users (username, account_number, hash) VALUES (?, ?, ?)', username, account_number, hash)
            flash('You are successfully registered, Please click on login to log into your account!', 'success')
            return redirect('/register')

        except:
            flash('Username and/or account number alredy exist', 'danger')
            return redirect('/register')

    else:
        return render_template('register.html')
