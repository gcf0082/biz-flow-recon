<!--
子任务拆分计划。planner 子代理写入 output/_plan.md。可被被分析项目内的同名文件覆盖。

按"审计优先级"（启发式分流 hint，**不是风险结论**）从高到低排序：
- high：upload/download/import/export/exec/shell/script/payment/charge/refund/transfer/admin/auth/login/password/token/redirect/proxy/webhook/callback/crypto/encrypt/decrypt/sign 等关键词；或 PUT/DELETE/PATCH 涉核心对象
- medium：search/list/query（SQL 注入面）、update/delete（数据修改）、其他用户带 body 的 POST
- low：纯只读 GET / health / metric / config 查询 / 元数据返回

子功能 priority 取其内部 endpoint 最高一档。
-->

# {项目名} — 子任务拆分

总体策略：按 {目录/包/maven 模块/业务域} 划分；按审计优先级 high → medium → low 排序。

## 子任务

```yaml
sub_features:
  - name: 文件管理
    slug: file
    priority: high
    scope:
      - src/main/java/com/acme/file/
    endpoints:
      - method: POST
        path: /api/files/upload
        class_method: com.acme.file.UploadController#upload
        file_line: UploadController.java:48
        expected_output: endpoint-POST-api-files-upload.md
        priority: high
      - method: GET
        path: /api/files/{name}
        class_method: com.acme.file.FileController#download
        file_line: FileController.java:29
        expected_output: endpoint-GET-api-files-name.md
        priority: high

  - name: 支付
    slug: pay
    priority: high
    scope:
      - src/main/java/com/acme/pay/
      - services/pay-gw/
    endpoints:
      - method: POST
        path: /api/transfer
        class_method: com.acme.pay.TransferController#transfer
        file_line: TransferController.java:58
        expected_output: endpoint-POST-api-transfer.md
        priority: high

  - name: 用户中心（只读）
    slug: user
    priority: low
    scope:
      - src/main/java/com/acme/user/
    endpoints:
      - method: GET
        path: /api/users/me
        class_method: com.acme.user.UserController#me
        file_line: UserController.java:18
        expected_output: endpoint-GET-api-users-me.md
        priority: low
```
