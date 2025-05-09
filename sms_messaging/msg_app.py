from flask import Flask, request, render_template, url_for, redirect
from dotenv import load_dotenv
import json
import os
from collections import Counter
from pathlib import Path
from twilio.rest import Client
from google.cloud import firestore
from google.oauth2 import service_account

load_dotenv()

app = Flask(__name__)

# Twilio client creation encapsulated
def get_twilio_client():
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH")
    if not account_sid or not auth_token:
        raise RuntimeError("Twilio credentials not set.")
    return Client(account_sid, auth_token)

# Firestore client creation encapsulated
def get_firestore_client():
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    key_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if key_file:
        key_path = Path(__file__).resolve().parent / key_file
        credentials = service_account.Credentials.from_service_account_file(str(key_path))
        return firestore.Client(project=project_id, credentials=credentials, database="shrewcrew-database")
    else:
        return firestore.Client(project=project_id, database="shrewcrew-database")

# Hardcoded login database
database = {
    'ShrewCrew': '123Password',
    'admin': 'adminpass'
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username not in database:
            return render_template("login.html", info="Invalid Username")
        elif database[username] != password:
            return render_template("login.html", info="Invalid Password")
        else:
            return redirect(url_for('welcome'))
    else:
        return render_template("login.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/sms")
def sms():
    sms_list = fetch_sms_from_twilio()
    return render_template("sms.html", sms=sms_list)

@app.route("/tickets")
def tickets():
    ticket_list = fetch_tickets_from_firestore()

    issue_counts = Counter(ticket.get('issue_type', 'Unknown') for ticket in ticket_list)
    issue_labels = list(issue_counts.keys())
    issue_values = list(issue_counts.values())

    # Manually format into JavaScript-friendly JSON strings
    js_labels = json.dumps(issue_labels)
    js_values = json.dumps(issue_values)

    return render_template(
        "tickets.html",
        tickets=ticket_list,
        js_labels=js_labels,
        js_values=js_values
    )

# --- Helper functions ---

def fetch_sms_from_twilio():
    messages = []
    try:
        twilio_client = get_twilio_client()
        sms_messages = twilio_client.messages.list(limit=50)
        for msg in sms_messages:
            messages.append({
                'direction': msg.direction,
                'date_created': msg.date_created,
                'date_sent': msg.date_sent,
                'from_': msg.from_,
                'to': msg.to,
                'status': msg.status,
                'body': msg.body,
                'price': msg.price,
                'price_unit': msg.price_unit
            })
    except Exception as e:
        print("Error fetching Twilio SMS:", e)
    return messages

def fetch_tickets_from_firestore():
    tickets = []
    try:
        db = get_firestore_client()
        docs = db.collection('tickets').stream()
        docs = list(docs)
        print(f"Fetched {len(docs)} documents from Firestore.")

        for doc in docs:
            data = doc.to_dict()
            print(f"Raw document data: {data}")

            ticket = {
                'case_id': data.get('case_id', 'Missing case_id'),
                'issue_type': data.get('issue_type', 'Missing issue_type'),
                'status': data.get('status', 'Missing status'),
                'phone': data.get('phone', 'Missing phone'),
                'created_at': data.get('created_at', 'Missing created_at')
            }
            print(f"Processed ticket data: {ticket}")
            tickets.append(ticket)

    except Exception as e:
        print("Error fetching Tickets:", e)

    print(f"Total tickets prepared for template: {len(tickets)}")
    return tickets

if __name__ == "__main__":
    app.run(debug=True)