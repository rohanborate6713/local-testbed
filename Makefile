up:
	docker compose up -d --build

down:
	docker compose down

smoke:
	python3 smoke_tests/smoke.py

logs:
	docker compose logs -f entitlement-server operator-adapter

debug-bundle:
	mkdir -p debug-bundle
	cp docker-compose.yml debug-bundle/
	cp README.md debug-bundle/
	docker compose logs --tail=200 entitlement-server > debug-bundle/entitlement_logs.txt
	docker compose logs --tail=200 operator-adapter > debug-bundle/adapter_logs.txt
	docker ps > debug-bundle/docker_ps.txt
	echo "Timestamp: $$(date)" > debug-bundle/info.txt
	echo "Smoke correlation IDs: (run make smoke to generate)" >> debug-bundle/info.txt
	zip -r debug-bundle.zip debug-bundle/
	rm -rf debug-bundle