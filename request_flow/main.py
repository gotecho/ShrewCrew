from flask import Flask
from request_flow.routes import routes_bp
from request_flow.routes.overview import overview_bp

app = Flask(__name__)

app.register_blueprint(routes_bp)
app.register_blueprint(overview_bp)

if __name__ == "__main__":
    app.run(debug=True)