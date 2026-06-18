# NekoCafe Runbook — 运维手册

## 服务列表

| 服务 | 端口 | 技术栈 | 健康检查 |
|------|------|--------|----------|
| reservation | 8080 | Python 3.12 / FastAPI | GET /healthz |
| member | 8081 | Node.js 20 / Express | GET /healthz |

## 日常运维

### 查看服务状态

```bash
docker compose ps
kubectl get pods -n prod
```

### 查看日志

```bash
# 本地
docker compose logs -f

# K8s
kubectl logs -f -l service=reservation -n prod
kubectl logs -f -l service=member -n prod
```

### 查看监控

1. Grafana: http://localhost:3000
2. Prometheus: http://localhost:9090
3. Jaeger: http://localhost:16686

## 故障处理

### 服务无响应

1. 检查 Pod 状态: `kubectl get pods -n <namespace>`
2. 查看日志: `kubectl logs -l service=<service> -n <namespace> --tail=100`
3. 检查资源: `kubectl top pods -n <namespace>`

### 数据库连接失败

```bash
kubectl port-forward svc/postgres 5432:5432 -n prod
psql -h localhost -U nekocafe -d nekocafe -c "SELECT 1"
```

### 自动回滚触发条件

- 错误率 > 1%（持续 2 分钟）
- P95 延迟 > 1s（持续 2 分钟）
- 健康检查连续失败 3 次

## 环境信息

| 环境 | Namespace | 副本数 | 说明 |
|------|-----------|--------|------|
| dev | dev | 1 | 开发测试 |
| staging | staging | 2 | 预发布 + 金丝雀 |
| prod | prod | 3 | 生产 + 蓝绿部署 |
