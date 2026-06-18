# NekoCafé 智慧餐饮预约平台 — 实验三 PoC 仓库

> 基于实验二架构方案，使用 DevOps 流水线实现 CI/CD + 容器化部署

## 项目结构

```
nekocafe/
├── README.md                    一键启动 30 分钟内可成功
├── .editorconfig                统一编辑器规范
├── .pre-commit-config.yaml      Git pre-commit 钩子
├── .yamllint                    YAML linter 配置
├── docker-compose.yml           本地一键启动完整栈（7 容器）
├── prometheus.yml               Prometheus 采集配置
├── init-db.sql                  数据库初始化 DDL + 种子数据
├── Makefile                     常用命令快捷方式
├── services/                    微服务源码
│   ├── reservation/             预约服务（Python 3.12 + FastAPI）
│   │   ├── Dockerfile           三阶段构建，非 root 用户
│   │   ├── requirements.txt     依赖锁定
│   │   ├── src/main.py          8 个 API + OTel 集成
│   │   └── tests/               单元测试 + conftest
│   └── member/                  会员服务（Node.js 20 + Express）
│       ├── Dockerfile           三阶段构建，dumb-init
│       ├── package.json         依赖锁定
│       └── src/
│           ├── index.js         5 个 API + 结构化 JSON 日志
│           └── telemetry.js     OTel SDK 初始化
├── infra/                       基础设施即代码
│   ├── helm/                    Helm Chart（dev/staging/prod）
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-dev.yaml
│   │   ├── values-staging.yaml
│   │   ├── values-prod.yaml
│   │   └── templates/           10 个 K8s 模板
│   ├── observability/           可观测性配置
│   │   ├── prometheus-rules.yml 4 条告警规则
│   │   └── loki-config.yml      日志聚合配置
│   └── k8s-manifests/           K8s 原生清单（备用）
├── .github/workflows/           CI/CD 流水线
│   ├── ci.yml                   5 阶段持续集成
│   └── cd.yml                   4 环境渐进式部署
├── grafana-dashboards/          Grafana Dashboard JSON
│   ├── dashboards.yaml          Provisioning 配置
│   └── nekocafe-service-overview.json  12 面板服务总览
├── grafana-datasources/         Grafana 数据源
│   └── datasources.yaml         Prometheus + Jaeger + Loki
└── docs/                        运维文档
    ├── runbook.md               故障处置手册（4 大场景）
    └── rollback.md              回滚操作指南
```

## 架构取舍说明

- **Monorepo**：两个微服务共享同一仓库，便于统一 CI/CD 流水线、共享可观测性配置和 PR 审核上下文
- **Helm Chart 存放位置**：`infra/helm/` 与 D3-5 交付物保持一致，完整版本详见 D3-5 文件夹
- **本地可观测性**：Prometheus + Grafana + Jaeger 通过 docker-compose 一键启动，生产环境通过 Helm 部署

## 前置依赖

| 工具 | 最低版本 | 用途 |
|------|---------|------|
| Docker | 24.0+ | 容器运行时 |
| Docker Compose | 2.20+ | 本地编排 |
| Make | 4.0+ | 快捷命令（可选） |

## 一键启动

```bash
# 方式一：使用 Make（推荐）
make up

# 方式二：直接使用 docker compose
docker compose up -d --build
```

## 验证

```bash
# 健康检查
make health

# 或手动检查
curl http://localhost:8081/healthz        # Reservation Service
curl http://localhost:8082/healthz        # Member Service
curl http://localhost:3000                # Grafana (admin/nekocafe)
curl http://localhost:16686               # Jaeger UI
curl http://localhost:9090                # Prometheus
```

## 测试

```bash
# 运行所有测试
make test

# 单独测试预约服务
docker compose exec reservation pytest tests/ -v

# 单独测试会员服务
docker compose exec member npm test
```

## 代码检查

```bash
make lint
```

## 停止与清理

```bash
# 停止并删除容器和卷
make down

# 完全清理（含镜像）
make clean
```

## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| Reservation API | 8081 | 预约服务 REST API |
| Member API | 8082 | 会员服务 REST API |
| PostgreSQL | 5432 | 关系数据库 |
| Redis | 6379 | 缓存 |
| Jaeger UI | 16686 | 链路追踪查询 |
| Prometheus | 9090 | 指标采集与查询 |
| Grafana | 3000 | 可视化监控面板 |

## CI/CD 流水线

- **CI**：PR 触发 → Lint → SAST → Build → Trivy 扫描 → 集成测试 → PR 评论
- **CD**：main 推送 → 构建镜像 → Dev 部署 → Staging 金丝雀(5%→100%) → Prod 蓝绿部署
- **回滚**：`helm rollback nekocafe-{color} -n prod`

## 安全说明

- 所有 Secret 通过 GitHub Secrets 注入，禁止硬编码
- 镜像通过 Trivy 扫描，HIGH/CRITICAL 漏洞阻断流水线
- 生产环境数据库密码通过 Kubernetes Secret 管理
- 日志自动脱敏手机号等 PII 数据
- pre-commit 钩子集成 gitleaks 密钥检测
