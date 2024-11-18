import json, os, traceback
from flask import g
from dotenv import load_dotenv

class GlobalCheckException(Exception):
    """Failed to verify globals before creating gcloud log entry"""

class Custom_Logger:
    def __init__(self, request):
        try:
            self.ENV = os.getenv("ENVIRONMENT")
            self.PROJECT_ID = os.getenv("PROJECT_ID")
            self.trace_header = request.headers.get("X-Cloud-Trace-Context")
            self.full_trace = self.trace_header if self.ENV == 'REMOTE' and self.trace_header else 'localenvironment/dummytrace'
            self.request = request
            
            # Setting flask global app context  https://flask.palletsprojects.com/en/2.3.x/appcontext/
            g.trace = self.full_trace.split("/")[0]
            g.request_id = request.headers.get("Dialogflow-Request-Id")
            g.session_id = request.headers.get("Dialogflow-Session-Id")

        except Exception as error:
            raise GlobalCheckException("Could not verify globals while initializing logger \nSelf: \n" + str(self), error)


    def debug(self, message:str, optional_params:dict={}):
        entry = {
            "message": message,
            "severity": 'DEBUG',
            "logging.googleapis.com/trace": f"projects/{self.PROJECT_ID}/traces/{g.trace}",
            "request_id": g.request_id,
            "session_id": g.session_id,
            "original_request": {
                "url": self.request.base_url,
                "data": self.request.get_json() if self.request.content_type == 'application/json' else None
            },
            **optional_params
        }
        print(json.dumps(entry))

    def info(self, message:str, optional_params:dict={}):
        entry = {
            "message": message,
            "severity": 'INFO',
            "logging.googleapis.com/trace": f"projects/{self.PROJECT_ID}/traces/{g.trace}",
            "request_id": g.request_id,
            "session_id": g.session_id,
            "original_request": {
                "url": self.request.base_url,
                "data": self.request.get_json() if self.request.content_type == 'application/json' else None
            },
            **optional_params
        }
        print(json.dumps(entry))

    def warn(self, message:str,optional_params:dict={}):
        entry = {
            "message": message,
            "severity": 'WARN',
            "logging.googleapis.com/trace": f"projects/{self.PROJECT_ID}/traces/{g.trace}",
            "request_id": g.request_id,
            "session_id": g.session_id,
            "original_request": {
                "url": self.request.base_url,
                "data": self.request.get_json() if self.request.content_type == 'application/json' else None
            },
            **optional_params
        }
        print(json.dumps(entry))

    def error(self, message:str, error:Exception=Exception('default error'), optional_params:dict={}):
        
        if error.args[0]:
            message = f"{message} - {error.args[0]}\n"

        tb_obj = error.__traceback__
        
        if tb_obj:
            tb_list = traceback.format_list(traceback.extract_tb(tb_obj))
            acc = ''
            for line in tb_list:
                acc += line
            message += 'Traceback: \n' + acc

        entry = {
            "message": message,
            "severity": 'ERROR',
            "logging.googleapis.com/trace": f"projects/{self.PROJECT_ID}/traces/{g.trace}",
            "request_id": g.request_id,
            "session_id": g.session_id,
            "original_request": {
                "url": self.request.base_url,
                "data": self.request.get_json() if self.request.content_type == 'application/json' else None
            },
            **optional_params
        }
        print(json.dumps(entry))