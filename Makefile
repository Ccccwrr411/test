.PHONY: up down logs test lint clean

# Start all services
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Run all tests
test:
	cd services/member && npm test
	cd services/reservation && python -m pytest tests/ -v

# Run linters
lint:
	cd services/member && npm run lint
	cd services/reservation && ruff check src/ tests/

# Clean up
clean:
	docker compose down -v
	docker system prune -f
