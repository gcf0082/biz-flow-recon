<!--
biz-flow-recon 默认输出模板（粒度 B：子功能 + 接口）。
本文件可被被分析项目里的 `biz-flow-recon/templates/default.md` 覆盖。
读完照样写一份给当前分析对象。

要点：
- 接口下面**不用 bullet**，写 1-2 段散文。
- 没有发生的事实就不提；下钻得到的下游事实继续织进同一段（用从句串），不要嵌套子节。
- 段落里嵌入 (类#方法，文件:行号) 作为可定位锚点。
- 不评判风险，只描述事实。
- 找不到的下钻目标必须点名 + 在末尾"未跟到的引用"列出。
-->

# {范围名} 业务流讲解

## 整体在做什么

80-200 字连贯叙述：这个范围内的代码完成什么业务、由谁触发、关键流程怎么串。成段叙述，不要 bullet。

## 业务流

### 子功能 1：用户登录与会话

#### POST /api/login

未登录用户的登录入口（com.acme.auth.AuthController#login，AuthController.java:42）。
进来先用 BCrypt.checkpw 校验密码哈希，**通过后调内部令牌服务
http://internal-idp/token 换 JWT，对端实现是 com.acme.idp.IdpController#issue
（services/idp-svc/src/main/java/com/acme/idp/IdpController.java:25），那边
从 Redis 拉用户的角色集合再用 RS256 签 Token，私钥在启动时由 KmsClient
从 KMS 拉到本地缓存（IdpKmsClient.java:18，启动后每小时刷一次）**；JWT 拿
回后，登录侧再把会话信息回写 Redis。配置 config/oauth.yaml（YAML）启动时读，
每次登录尝试往 /var/log/acme/auth.log 写一行 Logback。代码在
src/main/java/com/acme/auth/。

#### POST /api/jobs/run-report

管理员触发离线对账（com.acme.ops.JobController#runReport，JobController.java:73）。
调用 `ProcessBuilder` 执行 `scripts/run-report.sh`，**那个脚本里先
`spark-submit` 一个打包在 jobs/report.jar 的作业（数据源是 PostgreSQL `bills`
库的 `txn_*` 分区表），结束后把 CSV 写到 /data/reports/{date}/，再用 awscli
sync 到 s3://acme-reports/**。脚本退出码作为接口返回；不记业务日志。
代码在 src/main/java/com/acme/ops/、scripts/run-report.sh。

#### GET /api/users/me

已登录用户读取自己的资料（com.acme.user.UserController#me，UserController.java:18，
代码在 src/main/java/com/acme/user/）。

### 子功能 2：订单管理

#### POST /api/orders

...（同样 1-2 段散文，下钻到下游服务/脚本/SQL）

## 未跟到的引用

仅当存在未在工作区找到的下钻目标时才写这一节，按下面格式一条一行；没有就**整节略掉**。

- `scripts/legacy-import.py` — 调用点 com.acme.imp.ImportRunner#run（ImportRunner.java:54）
- `http://internal-billing/charge` — 调用点 com.acme.pay.PayClient#charge（PayClient.java:31），未在工作区找到对应服务
