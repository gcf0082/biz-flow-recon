<!--
本目录是 biz-flow-recon 的项目级先验知识库——所有子代理执行前都会**强制读取本
目录全量 .md** 作为先验上下文。把这份示例文件复制改名为对应职责的文件即可：

  briefing.md       项目高层说明（技术栈、模块布局、外部接口风格、共用机制等）
  glossary.md       项目特有术语
  conventions.md    团队约定 + 配置开关
  modules/*.md      每个子模块一份说明
  auto-*.md         由 knowledge-extractor 自动写入（不要手写）

下面这份是 briefing.md 的样例——直接改内容，别保留示例的占位文字。
-->

# {项目名} 项目说明

## 技术栈
- 后端：{Spring Boot 3.x / FastAPI 0.110 / ...}
- 数据库：{PostgreSQL 15 / MySQL 8 / ...}
- 消息：{Kafka / RabbitMQ / ...}
- 鉴权：{Spring Security + JWT / DRF SimpleJWT / ...}

## 模块布局
- `<root>/api/` —— 对外 REST 接口层
- `<root>/services/` —— 业务逻辑
- `<root>/integrations/` —— 第三方对接（每个外部系统一个目录）
- `<root>/scripts/` —— 运维脚本与定时任务
- `<root>/internal-rpc/` —— 内部 gRPC 服务

## 对外接口风格约定
- 路径：`/api/v{N}/<resource>/<action>`
- 鉴权：所有 `/api/*` 由 `JwtFilter` 统一拦截；`/api/public/*` 放行
- 响应：统一包装 `{code, msg, data}`；错误码见 `<root>/common/ErrorCode.java`
- 内容协商：`application/json; charset=utf-8`

## 跨模块共用机制
- 统一 trace：`X-Trace-Id` header（`TraceFilter.java:18` 注入）
- 加密：`AcmeCrypto` SDK 封装 AES-GCM；密钥从 KMS 拉取
- HMAC 签名：所有 outbound 第三方调用都用 `HmacSigner`（密钥取自 `${X_HMAC_SECRET}`）
- 日志：Logback；业务日志 `/var/log/{module}/biz.log`

## 内部服务定位
- charge-svc → 代码在 `../services/charge-svc/`
- idp-svc    → 代码在 `../services/idp-svc/`
- billing    → 黑盒（外部团队维护，不予追溯）

## 特殊查找线索
- 所有 `*Mapper.xml` 在 `src/main/resources/mapper/` 而非紧邻 Java 类
- 配置统一 `src/main/resources/application-{env}.yml`
- 启动参数解析在 `<root>/boot/StartupRunner.java`

## 配置开关（控制 skill 行为）

```markdown
## 递归追溯深度
3

## 执行模式
并行

## 知识库自我演化
关闭
```
