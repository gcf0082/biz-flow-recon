<!-- 默认输出模板（粒度 B：子功能 + 接口）。可被项目里同名文件覆盖。 -->

# {范围名} 业务流讲解

## 整体在做什么

80-200 字成段叙述：这个范围的代码做什么、谁触发、关键流程怎么串。

## 业务流

### 子功能 1：用户登录与会话

#### POST /api/login

未登录用户的登录入口（com.acme.auth.AuthController#login，AuthController.java:42）。涉及多服务跨调用，画图最清楚：

```mermaid
sequenceDiagram
    autonumber
    participant U as 用户
    participant A as AuthController
    participant DB as 用户库
    participant IDP as IdpController (idp-svc)
    participant R as Redis
    participant K as KMS

    U->>A: POST /api/login (username, password)
    A->>DB: 查密码哈希
    A->>A: BCrypt.checkpw
    A->>IDP: POST /token (subject)
    IDP->>R: 拉用户角色集
    IDP->>K: 取 RS256 私钥(本地缓存命中,每小时刷)
    IDP-->>A: JWT
    A->>R: 写会话
    A-->>U: 200 {token}
```

- **请求**：body JSON `{username: string!, password: string!}`（DTO: com.acme.auth.LoginRequest，LoginRequest.java:11，字段都 @NotBlank）
- **加解密**：`BCrypt.checkpw` 校验密码哈希——避免明文比对；`IdpController#issue`（services/idp-svc/.../IdpController.java:25）用 RS256 签 JWT，私钥由 `IdpKmsClient`（IdpKmsClient.java:18）启动时从 KMS 拉到本地缓存
- **配置**：启动读 `config/oauth.yaml`（YAML，OAuth 客户端配置）
- **日志**：每次登录尝试写一行 Logback 到 `/var/log/acme/auth.log`

#### POST /api/jobs/run-report

管理员触发离线对账（com.acme.ops.JobController#runReport，JobController.java:73）。流程顺序，列编号步骤：

1. `ProcessBuilder` 执行 `scripts/run-report.sh`
2. 脚本里 `spark-submit` 一个打包在 `jobs/report.jar` 的作业，数据源是 PostgreSQL `bills` 库的 `txn_*` 分区表
3. 作业把 CSV 写到 `/data/reports/{date}/`
4. `awscli sync` 同步到 `s3://acme-reports/`
5. 脚本退出码作为接口返回；不记业务日志

#### GET /api/users/me

已登录用户读取自己的资料（com.acme.user.UserController#me，UserController.java:18）。

### 子功能 2：订单管理

#### POST /api/orders

已登录用户提交订单（com.acme.order.OrderController#create，OrderController.java:36）。请求体嵌套，用字段树最清楚：

```json5
{
  "orderId":   "string!",                 // @NotBlank @Size(<=32)
  "items": [
    {"sku": "string!", "qty": "int! >0", "price": "decimal!"}
  ],
  "address": {
    "country": "string!",                 // ISO-3166-1 alpha-2
    "city":    "string!",
    "zip":     "string"
  },
  "couponCode": "string?"                 // 可选
}
```

DTO: com.acme.order.OrderRequest（OrderRequest.java:18）；Header `Content-Type: application/json`，鉴权走 `Authorization: Bearer <jwt>`。

- **数据库**：MyBatis `mapper/OrderMapper.xml` 在 `orders`、`order_items` 表 INSERT
- **第三方**：调内部库存服务 `http://stock-svc/reserve`（POST，`{sku, qty}` 列表）锁库存

#### GET /api/orders/{id}

已登录用户查订单详情（com.acme.order.OrderController#get，OrderController.java:74）。`**请求**: path `id` (Long)`。从 `orders`/`order_items` 表读后返回。

#### GET /api/files/{name}

已登录用户下载导出文件（com.acme.file.FileController#download，FileController.java:29）。`**请求**: path `name` (string)`。

- **输入流向**：`path.name` → `Paths.get("/data/exports/" + name)`，再 `Files.copy(...)` 到响应流（FileController.java:34）—— 拼路径

## 未跟到的引用

仅在存在未找到的下钻目标时写这一节，按 `<引用> — 调用点 (文件:行号)` 一条一行；没有就**整节略掉**。

- `http://internal-billing/charge` — 调用点 com.acme.pay.PayClient#charge（PayClient.java:31），未在工作区找到对应服务
