<!--
默认输出模板。可被项目里同名文件覆盖。
- 粒度 B：用整份骨架（顶层叙述 + 子功能分组 + 接口块）。
- 粒度 C：只取一个接口块，把 `#### POST /api/...` 提到顶层 `# POST /api/... — 一句话功能`。
-->

# {范围名} 业务流讲解

## 整体在做什么

80-200 字成段叙述：这个范围的代码做什么、谁触发、关键流程怎么串。

## 业务流

### 子功能 1：文件管理

#### GET /api/files/{name}

已登录用户下载导出文件（com.acme.file.FileController#download，FileController.java:29）。入参直接拼到后台路径，简单流程：

```mermaid
sequenceDiagram
    autonumber
    participant U as 用户
    participant C as FileController
    participant FS as 本地磁盘

    U->>C: GET /api/files/{name}
    C->>FS: Paths.get("/data/exports/" + name)
    FS-->>C: InputStream
    C-->>U: Files.copy(in, response)
```

- **请求**：path `name` (string)
- **输入流向**：`path.name` → `Paths.get("/data/exports/" + name)` → `Files.copy(path, OutputStream)`（FileController.java:34）—— 拼路径
- **文件**：读 `/data/exports/{path.name}`（按用户传入文件名读取并写到响应流）

#### POST /api/jobs/run-report

管理员触发离线对账（com.acme.ops.JobController#runReport，JobController.java:73）。顺序流程：

1. `ProcessBuilder` 执行 `scripts/run-report.sh`
2. 脚本 `spark-submit jobs/report.jar`（数据源 PostgreSQL `bills.txn_*`）
3. 作业把 CSV 写到 `/data/reports/{date}/`，再 `awscli sync` 到 `s3://acme-reports/`
4. 脚本退出码作为接口返回；不记业务日志

#### GET /api/users/me

已登录用户读取自己的资料（com.acme.user.UserController#me，UserController.java:18）。

### 子功能 2：订单管理

#### POST /api/orders

已登录用户提交订单（com.acme.order.OrderController#create，OrderController.java:36）。Body 嵌套：

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
- **第三方**：调内部库存服务 `POST http://stock-svc/v1/reserve`（Feign，com.acme.order.StockClient，StockClient.java:12，body 是 `[{sku, qty}]` 列表）

## 未跟到的引用

仅在存在未找到的下钻目标时写这一节，按 `<引用> — 调用点 (文件:行号)` 一条一行；没有就**整节略掉**。

- `http://internal-billing/charge` — com.acme.pay.PayClient#charge（PayClient.java:31）
