from prometheus_client import Counter, Gauge, Histogram

# Existing metrics
auth_events_total = Counter(
    'auth_events_total',
    'Total authentication events',
    ['result']
)

entitlement_enabled_total = Gauge(
    'entitlement_enabled_total',
    'Total enabled entitlements'
)

# New: Request latency histogram (in seconds)
# Buckets: default + finer-grained for sub-second latencies common in mocks
request_latency_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0, float('inf'))
)