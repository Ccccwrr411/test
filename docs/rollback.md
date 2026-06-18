# Rollback 回滚指南

## 一键回滚命令

### Kubernetes (Helm)

```bash
# 回滚到上一个版本
helm rollback nekocafe-reservation -n prod

# 回滚到指定版本
helm rollback nekocafe-reservation 3 -n prod

# 查看历史版本
helm history nekocafe-reservation -n prod
```

### Docker Compose (本地)

```bash
# 切换到上一个 Git 版本
git checkout HEAD~1
make up
```

## 自动回滚触发条件

| 指标 | 阈值 | 动作 |
|------|------|------|
| P95 延迟 | > 500ms | 自动回滚 |
| 错误率 | > 1% | 自动回滚 |
| 健康检查失败 | 连续 3 次 | 自动回滚 |

## 手动回滚步骤

1. 确认问题：`kubectl -n prod describe pod -l app=nekocafe`
2. 执行回滚：`helm rollback nekocafe-reservation -n prod --wait`
3. 验证恢复：`curl -f https://api.nekocafe.com/healthz`
4. 通知团队：企业微信群 / PagerDuty
