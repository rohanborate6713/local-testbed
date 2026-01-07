#!/usr/bin/env python3

import sys
import time
import json
import subprocess
import requests

ADAPTER_URL = "http://localhost:8081"
ENTITLEMENT_URL = "http://localhost:8080"
IMSI = "001010000000001"

def run_cmd(cmd):
    """Run a shell command and return stdout"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout

def wait_for_healthy():
    print("Waiting for entitlement-server to be healthy...")
    for _ in range(30):
        try:
            resp = requests.get(f"{ENTITLEMENT_URL}/healthz", timeout=5)
            if resp.text.strip() == "OK":
                print("entitlement-server is healthy.")
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    print("FAIL: entitlement-server did not become healthy in time")
    sys.exit(1)

def trigger_event(endpoint):
    url = f"{ADAPTER_URL}/simulate/{endpoint}"
    print(f"Triggering {endpoint}...")
    resp = requests.post(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    corr_id = data.get("correlation_id")
    if not corr_id:
        print(f"FAIL: No correlation_id in response from {endpoint}")
        sys.exit(1)
    print(f"{endpoint.replace('auth-', '').capitalize()} correlation_id: {corr_id}")
    return corr_id

def check_entitlement(expected_state):
    resp = requests.get(f"{ENTITLEMENT_URL}/v1/entitlement/{IMSI}", timeout=10)
    resp.raise_for_status()
    state = resp.json().get("entitlement")
    if state != expected_state:
        print(f"FAIL: Entitlement is '{state}', expected '{expected_state}'")
        sys.exit(1)

def get_container_logs(container_name):
    cmd = f"docker logs $(docker ps -q -f name={container_name}) 2>&1"
    return run_cmd(cmd)

def verify_correlation_in_logs(corr_id, logs, service_name):
    if corr_id not in logs:
        print(f"FAIL: correlation_id {corr_id} not found in {service_name} logs")
        sys.exit(1)

def main():
    wait_for_healthy()

    success_corr_id = trigger_event("auth-success")
    check_entitlement("ENABLED")

    fail_corr_id = trigger_event("auth-fail")
    check_entitlement("DISABLED")

    print("Verifying correlation_ids in logs...")
    adapter_logs = get_container_logs("operator-adapter")
    entitlement_logs = get_container_logs("entitlement-server")

    for corr_id, name in [(success_corr_id, "Success"), (fail_corr_id, "Fail")]:
        verify_correlation_in_logs(corr_id, adapter_logs, "operator-adapter")
        verify_correlation_in_logs(corr_id, entitlement_logs, "entitlement-server")

    print("All smoke tests passed!")

if __name__ == "__main__":
    main()