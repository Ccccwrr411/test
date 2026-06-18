# NekoCafé — DevOps Pipeline & Containerized Deployment

猫咪主题餐饮预约平台 · 实验三源代码与配置仓库、、

## 项目概述

本仓库实现 NekoCafé 平台的端到端 DevOps 流水线，包含两个核心微服务：

| 服务 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| reservation | Python 3.12 + FastAPI | 8080 | 预约服务：创建/查询/取消预约 |
| member | Node.js 22 + Express | 8081 | 会员服务：注册/登录/积分/等级 |

## 快速启动（30 分钟内）

### 前置条件

- Docker Desktop 24+
- Node.js 22+（本地开发需要）
- Python 3.12+（本地开发需要）
- Git

### 一键启动

```bash
git clone <repo-url>
cd nekocafe
docker compose up -d
```

### 验证

```bash
# 预约服务健康检查
curl http://localhost:8080/healthz
# 预期: {"status":"ok","service":"reservation","timestamp":"..."}

# 会员服务健康检查
curl http://localhost:8081/healthz
# 预期: {"status":"ok","service":"member","timestamp":"..."}

# 创建预约
curl -X POST http://localhost:8080/api/reservations \
  -H "Content-Type: application/json" \
  -d '{"store_id":"store_001","customer_id":"cust_001","date":"2026-06-20","time_slot":"12:00-13:00","guest_count":4}'

# 会员注册
curl -X POST http://localhost:8081/api/members/register \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000001","nickname":"CatLover","password":"test123"}'
```

### 停止与清理

```bash
# 停止服务
docker compose down

# 停止并清理数据卷
docker compose down -v

# 清理未使用的镜像
docker image prune -f
```

## 项目结构

```
nekocafe/
├── README.md                     # 本文档
├── docker-compose.yml            # 本地一键起栈
├── Makefile                      # 常用命令快捷入口
├── .editorconfig                 # 编辑器统一配置
├── .pre-commit-config.yaml       # Git pre-commit 钩子
├── services/
│   ├── reservation/              # 预约服务（Python/FastAPI）
│   │   ├── src/main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── member/                   # 会员服务（Node.js/Express）
│       ├── src/index.js
│       ├── tests/
│       ├── Dockerfile
│       └── package.json
├── infra/
│   ├── helm/                     # Helm Chart（dev/staging/prod）
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-dev.yaml
│   │   ├── values-staging.yaml
│   │   ├── values-prod.yaml
│   │   └── templates/
│   ├── k8s-manifests/            # 原生 K8s YAML（备用）
│   └── observability/            # 可观测性配置
│       ├── dashboards/
│       ├── rules/
│       └── prometheus.yml
├── .github/workflows/
│   ├── ci.yml                    # CI 流水线
│   └── cd.yml                    # CD 流水线（蓝绿部署）
└── docs/
    ├── runbook.md                # 运维手册
    └── rollback.md               # 回滚脚本
```

## Monorepo 选型说明

选择 Monorepo 结构的原因：
- 两个服务属于同一业务域（NekoCafé），共享基础设施配置
- 便于统一 CI/CD 流水线管理
- 原子化跨服务变更
- 减少仓库管理开销

## 流水线概览

```
PR → Lint → Unit Test → SAST → Build → Container Scan → Integration Test → Push Image
                                                                                  ↓
                                                                     CD: Blue-Green Deploy
```

## 技术栈

- **CI/CD**: GitHub Actions
- **容器编排**: Docker Compose (本地) / Kubernetes (生产)
- **配置管理**: Helm 3
- **安全扫描**: Trivy, CodeQL
- **可观测性**: OpenTelemetry + Prometheus + Grafana + Jaeger
