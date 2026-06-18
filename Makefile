.PHONY: up down restart logs test lint clean help

# 一键启动完整开发环境
up:
	docker compose up -d --build
	@echo ""
	@echo "=========================================="
	@echo "  NekoCafé Dev Environment Started!"
	@echo "  Reservation API : http://localhost:8081"
	@echo "  Member API      : http://localhost:8082"
	@echo "  Jaeger UI       : http://localhost:16686"
	@echo "  Prometheus      : http://localhost:9090"
	@echo "  Grafana         : http://localhost:3000 (admin/nekocafe)"
	@echo "=========================================="

# 停止并清理
down:
	docker compose down -v

# 重启所有服务
restart:
	docker compose restart

# 查看日志（跟随模式）
logs:
	docker compose logs -f --tail=100

# 运行测试
test:
	docker compose exec reservation pytest tests/ -v
	docker compose exec member npm test

# 代码检查
lint:
	cd services/member && npm run lint
	cd services/reservation && ruff check src/ tests/
	docker run --rm -i hadolint/hadolint < services/member/Dockerfile
	docker run --rm -i hadolint/hadolint < services/reservation/Dockerfile

# 清理构建缓存和未使用镜像
clean:
	docker compose down -v --rmi all
	docker system prune -f

# 健康检查
health:
	@echo "Checking Reservation Service..."
	@curl -s -o /dev/null -w "Reservation: %{http_code}\n" http://localhost:8081/healthz || echo "Reservation: DOWN"
	@echo "Checking Member Service..."
	@curl -s -o /dev/null -w "Member: %{http_code}\n" http://localhost:8082/healthz || echo "Member: DOWN"

# 帮助
help:
	@echo "NekoCafé Makefile Commands:"
	@echo "  make up       — Start all services"
	@echo "  make down     — Stop and remove all services"
	@echo "  make restart  — Restart all services"
	@echo "  make logs     — Tail all logs"
	@echo "  make test     — Run all tests"
	@echo "  make lint     — Run all linters"
	@echo "  make health   — Health check all services"
	@echo "  make clean    — Full cleanup"
