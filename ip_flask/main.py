from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def get_ip():
    response = requests.get("https://api64.ipify.org?format=json")
    return response.json(), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)