
from flask import jsonify, request
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token
import requests
import os

def forward_to_cloud_run(original_request):
    cloud_run_url = os.getenv('CLOUD_RUN_URL')
    audience = cloud_run_url

    try:
        token = id_token.fetch_id_token(GoogleAuthRequest(), audience)
    except Exception as e:
        return jsonify({'error': 'Failed to obtain identity token', 'details': str(e)}), 500

    headers = dict(original_request.headers)
    headers['Authorization'] = f'Bearer {token}'

    try:
        response = requests.post(
            cloud_run_url,
            headers=headers,
            data=original_request.form
        )
        return (response.content, response.status_code, response.headers.items())
    except Exception as e:
        return jsonify({'error': 'Error forwarding request', 'details': str(e)}), 500
