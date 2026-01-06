from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)

ENTITLEMENT_URL = os.environ.get('ENTITLEMENT_URL', 'http://localhost:8080/v1/auth/event')

@app.route('/simulate/auth-success', methods=['POST'])
def simulate_auth_success():
    correlation_id = str(uuid.uuid4())
    event = {
        "msisdn": "9999999999",
        "imsi": "001010000000001",
        "event": "AUTH_SUCCESS",
        "operator": "demo-op",
        "correlation_id": correlation_id
    }
    response = requests.post(ENTITLEMENT_URL, json=event)
    app.logger.info(f"Sent AUTH_SUCCESS event with correlation_id: {correlation_id}")
    return jsonify({"status": "success", "correlation_id": correlation_id}), response.status_code

@app.route('/simulate/auth-fail', methods=['POST'])
def simulate_auth_fail():
    correlation_id = str(uuid.uuid4())
    event = {
        "msisdn": "9999999999",
        "imsi": "001010000000001",
        "event": "AUTH_FAIL",
        "operator": "demo-op",
        "correlation_id": correlation_id
    }
    response = requests.post(ENTITLEMENT_URL, json=event)
    app.logger.info(f"Sent AUTH_FAIL event with correlation_id: {correlation_id}")
    return jsonify({"status": "fail", "correlation_id": correlation_id}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)