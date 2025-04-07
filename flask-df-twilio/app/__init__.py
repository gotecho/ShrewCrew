from flask import Flask
from config import Config
import logging, os

log_file_path = os.path.join(os.path.dirname(__file__), '../app.log')
logging.basicConfig( 
    filename = log_file_path, level = logging.INFO, 
    format = '%(asctime)s [%(levelname)s] %(message)s', datefmt = '%Y-%m-%d %H:%M:%S' 
    )

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes import main
    app.register_blueprint(main)

    return app
