from flask import Flask, request, render_template
from dotenv import load_dotenv
from utils import fetch_sms

load_dotenv()
app = Flask(__name__)

@app.route("/")
def index():
    ##sms = fetch_sms()
    ##return render_template("index.html", sms=sms)
    return render_template("login.html")
database={'ShrewCrew':'123Password'} ## Username:Password

@app.route("/form_login", methods=['POST', 'GET'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username not in database:
        return render_template("login.html", info="Invalid Username")
    else:
        if database[username]!=password:
            return render_template('login.html', info="Invalid Password")
        else:
            sms = fetch_sms()
            return render_template("index.html", sms=sms)
        
@app.route("/form_stats")
def stats():
    return render_template("overview.html")

    