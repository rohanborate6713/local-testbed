# local test bed 

## Prerequisites
- Docker and Docker Compose
- Make
- bash, curl, jq (for smoke tests)
- zip (for debug bundle)

## Make Commands
- `make up`: Starts the stack (builds and runs containers)
- `make smoke`: Runs smoke tests to validate the stack
- `make down`: Stops the stack
- `make logs`: Tails logs for entitlement-server and operator-adapter
- `make debug-bundle`: Generates debug-bundle.zip with docker-compose.yml, README.md, last 200 log lines, docker ps output, timestamp, and note on correlation IDs

## How to Run Smoke Tests
Run `make smoke`. It will:
1. Wait for /healthz to return OK
2. Trigger /simulate/auth-success and check entitlement becomes ENABLED
3. Trigger /simulate/auth-fail and check entitlement becomes DISABLED
4. Verify correlation_ids appear in both services' logs

## How to Generate Debug Bundle
Run `make debug-bundle`. It creates debug-bundle.zip with the required files.

## To see Prometheus metrics like auth_events_total and entitlement_enabled_total.
curl http://localhost:8080/metrics 
