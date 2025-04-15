
from flask import Flask, request, jsonify
from twilio_verify import verify_twilio_request
from ip_blocklist import is_blocked, block_ip
from cloud_run_proxy import forward_to_cloud_run
import os

app = Flask(__name__)

@app.route('/proxy', methods=['POST'])
def proxy():
    client_ip = request.remote_addr

    if is_blocked(client_ip):
        return jsonify({'error': 'Forbidden'}), 403

    if not verify_twilio_request(request):
        block_ip(client_ip)
        return jsonify({'error': 'Invalid Twilio request'}), 403

    return forward_to_cloud_run(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
