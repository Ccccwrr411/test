# Runbook — NekoCafé 故障处置手册

## 服务异常告警时

### 1. 快速定位
1. 在 Grafana 查看 P99 延迟 / 错误率面板
2. 在 Loki 检索最近 5min 的 ERROR 日志：
   ```
   {service="reservation"} |= "ERROR"
   ```
3. 在 Jaeger 找出涉事 traceId：
   - 筛选 `http.status_code >= 500`
   - 查看慢请求（duration > 2s）

### 2. 常见问题处置

#### 数据库连接超时
- 症状：`connection refused` / `too many clients`
- 检查：`kubectl -n prod exec deploy/postgres -- pg_isready`
- 处置：`kubectl -n prod rollout restart deploy/postgres`

#### Redis 内存耗尽
- 症状：`OOM command not allowed`
- 检查：`redis-cli INFO memory`
- 处置：扩容 Redis 内存限制 / 清理过期 key

#### Kafka 消息积压
- 症状：consumer lag 持续增长
- 检查：`kafka-consumer-groups --describe --group nekocafe`
- 处置：增加消费者实例数

#### 镜像拉取失败
- 症状：`ImagePullBackOff`
- 检查：`kubectl describe pod -l app=reservation | grep -A5 Events`
- 处置：确认 GHCR 权限 / 镜像 tag 正确

### 3. 升级流程
1. 通知运维群
2. 创建 incident channel
3. 按 runbook 排查
4. 30 分钟未解决 → 升级至值班经理
5. 1 小时未解决 → 升级至 CTO

### 4. 事后复盘
- 填写 Postmortem 文档
- 补充 runbook 条目
- 添加对应的监控告警
