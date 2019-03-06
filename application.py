import os
import sqlalchemy

from cs50 import SQL # from library50 import cs50
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import urllib.parse
from urllib.parse import urlparse

from helpers import apology, login_required, lookup

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///recipes.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show assessment results"""
    if request.method == "POST":
        # get the #
        y = request.form.get("delete")
        n = int(list(filter(str.isdigit, y))[0])  # https://stackoverflow.com/questions/26825729/extract-number-from-string-in-python/26825781
        print(n)
        n = n-1
        print(n)

        # select the title in the nth row in SQLlite
        titleN = db.execute("SELECT title FROM saved WHERE id = :user LIMIT 1 OFFSET :variable ", user=userId, variable=n)  # https://stackoverflow.com/questions/3419626/sqlite3-or-general-sql-retrieve-nth-row-of-a-query-result
        titleN = titleN[0]["title"]
        print(titleN)

        # delete the row
        db.execute("DELETE FROM saved WHERE title = :title", title=titleN)  # http://www.sqlitetutorial.net/sqlite-delete/

        return redirect("/")
    else:
        # display users username
        result = db.execute("SELECT username FROM users WHERE id = :username", username=userId)

        # display users saved recipes
        rows = db.execute("SELECT * FROM saved WHERE id = :username", username=userId)

        # calculate number of saved recipes
        length = len(rows)

        if length == 0:
            return render_template("index.html", username=result[0]["username"])
        else:
            return render_template("indexResults.html", username=result[0]["username"], rows=rows, length=length)



@app.route("/searchResults", methods=["GET", "POST"])
@login_required
def searchResults():
    """Save recipes."""

    # User reached route via POST (they submit a form on the page?)
    if request.method == "POST":

        # METHOD 1
        # do something if button is clicked
        # https://stackoverflow.com/questions/19794695/flask-python-button

        # get the number of the button that was clicked
        y = request.form.get("save")
        x = int(list(filter(str.isdigit, y))[0])  # https://stackoverflow.com/questions/26825729/extract-number-from-string-in-python/26825781
        if request.form['save']:  # when button clicked
            # Retrieve recipe title, link, and image in database
            title = recipe['hits'][x-1]['recipe']['label']
            link = recipe['hits'][x-1]['recipe']['url']
            image = recipe['hits'][x-1]['recipe']['image']

            # Store recipe title, link, and image in database
            store = db.execute("INSERT INTO saved (id, title, link, image) VALUES (:userid, :title, :link, :image)",
                               userid=userId, title=title, link=link, image=image)

        # return render_template("searchResults.html", recipe=recipe, maximum=maximum, time=cookTime)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("searchResults.html", recipe=recipe, maximum=maximum, time=cookTime)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search recipes."""

    # User reached route via POST (they submit a form on the page?)
    if request.method == "POST":

        # Ensure query was submitted
        if not request.form.get("query"):
            return apology("must provide a search term for recipes")

        # Ensure time was submitted
        if not request.form.get("time"):
            return apology("must provide a cook time")

        # save symbol
        global recipe
        recipe = lookup(request.form.get("query"),request.form.get("time"))
        count = recipe["count"]
        global cookTime
        cookTime = request.form.get("time")
        global maximum
        maximum = int(min(10, int(count)))

        # Redirect user to error if stock doesn't exist. Else reutnr quote confirmation page
        if recipe is None:
            return apology("No recipes exist for that query", 400)
        else:  # else if quote is a real ticker symbol, return the quoteConfirmation page/route
            # return render_template("searchResults.html", title=recipe["recipeTitle"], url=recipe["url"], image=recipe["image"])
            # return render_template("searchResults.html", recipe=recipe, maximum=maximum)
            return redirect("/searchResults")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",  # returns an array
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        global userId
        userId = rows[0]["id"]
        session["user_id"] = userId

        # need to access the first row of the array rows, row[0] and then go to the index cash, ["cash"]

        # Redirect user to home page
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

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure passwordConfirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation")

        # check passwords equals password confirmation
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match")

        # reject duplicate username
        result = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if result:
            return apology("Not a unique username")
            # return apology("username taken", 200)

        # Hash password
        # https://www.programcreek.com/python/example/82817/werkzeug.security.generate_password_hash
        hashed_password = generate_password_hash(request.form.get("password"))

        # Store user + pass in database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                   username=request.form.get("username"), hash=hashed_password)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
 app.debug = True
 port = int(os.environ.get('PORT', 5000))
 app.run(host='0.0.0.0', port=port)
