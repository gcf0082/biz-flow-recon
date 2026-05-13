<!--
风险分析扫描计划。主 agent 在步骤 1 扫描 _results/ 后写入 _risk-results/_risk-plan.md。
可被被分析项目内的同名文件覆盖。

观测点档位（红/橙/黄）是事实分析产物中的标记，仅用于决定分析优先级，
不直接映射到风险严重等级。

slug 派生规则：路径去除前导 / 后小写连字符。
POST /api/files/upload → slug = api-files-upload

status 字段由主 agent 在派发过程中更新：pending → done / failed。
-->

# {项目名} — 风险分析扫描计划

数据来源：`_results/` 中 {N} 个 endpoint-*.md，其中 {M} 个含观测点

## 扫描队列

```yaml
scan_queue:
  - endpoint: POST /api/files/upload
    file: endpoint-POST-api-files-upload.md
    scope: com.acme.file.UploadController#upload (UploadController.java:48)
    priority: P1
    observation_points:
      - node_id: WRITE
        level: 高(红)
        summary: 落地原始文件，body.filename 拼接到路径
        category_hint: path-traversal
      - node_id: SCAN
        level: 高(红)
        summary: 触发内容扫描，body.filename 拼接到命令
        category_hint: injection
      - node_id: REPORT
        level: 中(橙)
        summary: 上报监控，TLS 校验关闭
        category_hint: config
    status: pending

  - endpoint: GET /api/users/search
    file: endpoint-GET-api-users-search.md
    scope: com.acme.user.UserController#search (UserController.java:35)
    priority: P2
    observation_points:
      - node_id: QUERY
        level: 中(橙)
        summary: 用户搜索查询拼接 SQL
        category_hint: injection
    status: pending

  - endpoint: GET /api/users/me
    file: endpoint-GET-api-users-me.md
    scope: com.acme.user.UserController#me (UserController.java:18)
    priority: P3
    observation_points:
      - node_id: AUTH
        level: 低(黄)
        summary: 会话 token 未校验加入黑名单
        category_hint: authn
    status: pending
```