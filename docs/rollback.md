# NekoCafe Rollback — 一键回滚脚本

## 场景 1: Helm 回滚到上一个版本

```bash
#!/bin/bash
# rollback.sh — 一键回滚到上一个 Release

NAMESPACE=${1:-prod}
RELEASE=${2:-nekocafe}

echo "Rolling back $RELEASE in namespace $NAMESPACE..."

# 查看历史
helm history $RELEASE -n $NAMESPACE

# 回滚到上一个版本
helm rollback $RELEASE -n $NAMESPACE

# 等待就绪
kubectl rollout status deployment -n $NAMESPACE -l app=nekocafe --timeout=5m

echo "Rollback complete. Checking health..."
kubectl get pods -n $NAMESPACE -l app=nekocafe
```

## 场景 2: 蓝绿部署回滚（切回旧颜色）

```bash
#!/bin/bash
# blue-green-rollback.sh

CURRENT=$(kubectl get svc nekocafe-prod -n prod -o jsonpath='{.spec.selector.color}')
if [ "$CURRENT" = "blue" ]; then
  PREVIOUS="green"
else
  PREVIOUS="blue"
fi

echo "Current: $CURRENT, Rolling back to: $PREVIOUS"
kubectl patch svc nekocafe-prod -n prod -p "{\"spec\":{\"selector\":{\"color\":\"$PREVIOUS\"}}}"
echo "Traffic switched to $PREVIOUS"
```

## 场景 3: Docker Compose 回滚

```bash
# 切换到上一个镜像 tag
export TAG=previous-tag
docker compose up -d
```

## 自动回滚触发条件

| 指标 | 阈值 | 持续 |
|------|------|------|
| 错误率 | > 1% | 2 分钟 |
| P95 延迟 | > 1s | 2 分钟 |
| 健康检查 | 连续失败 3 次 | - |
