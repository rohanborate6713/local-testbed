from prometheus_client import Counter, Gauge

auth_events_total = Counter('auth_events_total', 'Total authentication events', ['result'])
entitlement_enabled_total = Gauge('entitlement_enabled_total', 'Total enabled entitlements')