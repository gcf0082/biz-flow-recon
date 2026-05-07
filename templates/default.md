<!--
biz-flow-recon 默认输出模板（粒度 B：子功能 + 接口）。
本文件可被被分析项目里的 `biz-flow-recon/templates/default.md` 覆盖。
模板就是一份示例骨架——读完照样写一份给当前分析对象。
-->

# {范围名} 业务流讲解

## 整体在做什么

80-200 字连贯叙述：这个范围内的代码完成什么业务、由谁触发、关键流程怎么串。成段叙述，不要 bullet。

## 业务流

### 子功能 1：用户登录与会话

#### POST /api/login

未登录用户的登录入口（com.acme.auth.AuthController#login，AuthController.java:42）。
进来先用 BCrypt.checkpw 校验密码哈希，避免明文比对；通过后向外部身份提供方
https://idp.example.com/oauth/token 发一次 POST application/x-www-form-urlencoded，
Header 带 Authorization: Basic <base64(client_id:secret)>，body 是
grant_type=password&username=...&password=...，使用 RestTemplate
（OAuthClient.java:31）。换回的身份信息再由 JJWT 以 HS256 签发会话 Token，
密钥取自 JWT_SECRET 环境变量，颁给前端保会话。配置 config/oauth.yaml（YAML）
在启动时读，每次登录尝试会往 /var/log/acme/auth.log 写一行 Logback 日志。
代码在 src/main/java/com/acme/auth/。

#### GET /api/users/me

已登录用户读取自己的资料（com.acme.user.UserController#me，UserController.java:18，
代码在 src/main/java/com/acme/user/）。

### 子功能 2：订单管理

#### POST /api/orders

...（同样 1-2 段散文）

<!--
注意：
- 接口下面**不用 bullet**，写 1-2 段散文。
- 没有发生的事实就不提（如 /api/users/me 没有 I/O / 命令 / 第三方 / 加解密，就一句话讲完）。
- 段落里嵌入 (类#方法，文件:行号) 作为可定位锚点。
- 不评判风险，只描述事实。
-->
