from flask import Flask, render_template
from dotenv import load_dotenv
from utils import fetch_sms

load_dotenv()
app = Flask(__name__)

@app.route("/")
def index():
    sms = fetch_sms()
    return render_template("index.html", sms=sms)