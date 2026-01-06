#!/bin/bash

set -e

ADAPTER_URL="http://localhost:8081"
ENTITLEMENT_URL="http://localhost:8080"
IMSI="001010000000001"

# Wait for stack to be healthy
echo "Waiting for entitlement-server to be healthy..."
for i in {1..30}; do
  if curl -s "$ENTITLEMENT_URL/healthz" | grep -q "OK"; then
    echo "Stack is healthy."
    break
  fi
  sleep 2
done

# Trigger auth-success
echo "Triggering auth-success..."
SUCCESS_RESP=$(curl -s -X POST "$ADAPTER_URL/simulate/auth-success")
SUCCESS_CORR_ID=$(echo "$SUCCESS_RESP" | jq -r '.correlation_id')
echo "Success correlation_id: $SUCCESS_CORR_ID"

# Check entitlement ENABLED
ENTITLEMENT=$(curl -s "$ENTITLEMENT_URL/v1/entitlement/$IMSI" | jq -r '.entitlement')
if [ "$ENTITLEMENT" != "ENABLED" ]; then
  echo "FAIL: Entitlement not ENABLED"
  exit 1
fi

# Trigger auth-fail
echo "Triggering auth-fail..."
FAIL_RESP=$(curl -s -X POST "$ADAPTER_URL/simulate/auth-fail")
FAIL_CORR_ID=$(echo "$FAIL_RESP" | jq -r '.correlation_id')
echo "Fail correlation_id: $FAIL_CORR_ID"

# Check entitlement DISABLED
ENTITLEMENT=$(curl -s "$ENTITLEMENT_URL/v1/entitlement/$IMSI" | jq -r '.entitlement')
if [ "$ENTITLEMENT" != "DISABLED" ]; then
  echo "FAIL: Entitlement not DISABLED"
  exit 1
fi

# Verify correlation_ids in logs (grep from docker logs)
echo "Verifying correlation_ids in logs..."
ADAPTER_LOGS=$(docker logs $(docker ps -q -f name=operator-adapter) 2>&1)
ENTITLEMENT_LOGS=$(docker logs $(docker ps -q -f name=entitlement-server) 2>&1)

if ! echo "$ADAPTER_LOGS" | grep -q "$SUCCESS_CORR_ID" || ! echo "$ENTITLEMENT_LOGS" | grep -q "$SUCCESS_CORR_ID"; then
  echo "FAIL: Success correlation_id not in both logs"
  exit 1
fi

if ! echo "$ADAPTER_LOGS" | grep -q "$FAIL_CORR_ID" || ! echo "$ENTITLEMENT_LOGS" | grep -q "$FAIL_CORR_ID"; then
  echo "FAIL: Fail correlation_id not in both logs"
  exit 1
fi

echo "All smoke tests passed!"