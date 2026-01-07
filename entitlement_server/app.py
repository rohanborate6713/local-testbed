from flask import Flask, jsonify, request
import redis
import logging
import os
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge

app = Flask(__name__)

# Redis connection
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port, db=0)

# logging
logging.basicConfig(level=logging.INFO)

# === Initialize PrometheusMetrics ONCE with custom latency histogram buckets ===
metrics = PrometheusMetrics(
    app,
    group_by='endpoint',  # Adds useful 'endpoint' label to latency metrics
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0, float("inf"))
)

# === Define your custom metrics using the exporter ===
auth_events_total = Counter(
    'auth_events_total',
    'Total authentication events processed',
    ['result']
)

entitlement_enabled_total = Gauge(
    'entitlement_enabled_total',
    'Current number of enabled entitlements (across all IMSIs)'
)

@app.route('/v1/auth/event', methods=['POST'])
def auth_event():
    data = request.json
    imsi = data.get('imsi')
    event = data.get('event')
    correlation_id = data.get('correlation_id')

    if not imsi or not event or not correlation_id:
        return jsonify({"error": "Missing fields"}), 400

    if event == 'AUTH_SUCCESS':
        r.set(f"entitlement:{imsi}", "ENABLED")
        auth_events_total.labels(result='success').inc()
        entitlement_enabled_total.inc()
    elif event == 'AUTH_FAIL':
        r.set(f"entitlement:{imsi}", "DISABLED")
        auth_events_total.labels(result='fail').inc()
        entitlement_enabled_total.dec()
    else:
        return jsonify({"error": "Invalid event"}), 400

    # Store last 20 events per IMSI
    event_key = f"events:{imsi}"
    r.lpush(event_key, str(data))
    r.ltrim(event_key, 0, 19)

    app.logger.info(f"Processed event {event} for IMSI {imsi} with correlation_id: {correlation_id}")

    return jsonify({"status": "processed"}), 200


@app.route('/v1/entitlement/<imsi>', methods=['GET'])
def get_entitlement(imsi):
    status = r.get(f"entitlement:{imsi}")
    return jsonify({"entitlement": status.decode('utf-8') if status else "UNKNOWN"}), 200


@app.route('/healthz', methods=['GET'])
def healthz():
    try:
        r.ping()
        return "OK", 200
    except:
        return "UNHEALTHY", 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)