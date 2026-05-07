---
name: biz-flow-recon
description: |
  解读一个前/后端或全栈代码仓库（主要面向 Java 后端），按安全测试视角口述代码
  在做什么——**默认按子功能 + 接口的粒度讲解**，必要时收敛到单接口或扩展到
  整项目。每条业务流用一两段自然语言讲清楚：在哪、谁触发、读写哪些文件、跑哪些
  外部命令、和哪些第三方系统怎么交互、有哪些加解密以及为什么。**只列实际存在的
  事实，没发生的不写**。
  **只描述事实，不下安全风险结论、不映射 OWASP、不评估漏洞**——把判断权留给
  安全测试人员。在用户说"梳理业务流""讲讲这个项目/这个模块/这个接口""渗透前
  摸底""代码审计前盘点""讲讲 XxxController 在干什么""POST /api/yyy 这个接口
  怎么走的""给我个 brief""帮我了解一下"等场景下都要使用，无论用户是否显式
  提到"安全"。不要用于已经在做漏洞分析或写修复建议的场景——那是 /security-review
  的范畴。
---

# biz-flow-recon

像一位熟悉系统的工程师，把代码讲给安全测试人员听：先一段连贯的话讲清"它在做什么"，再按子功能分组，每个接口下用**自然的段落**讲它怎么跑——把文件 I/O、外部命令、第三方交互、加解密自然地织进句子里。判断权留给读者。

## 原则

- **描述事实，不评判**。禁用"风险/漏洞/不安全/缺乏校验/可能被攻击/建议加固"等词。
- **每条业务流用 1-2 段自然语言讲，不用 bullet**。事实嵌在句子里，简单接口可以一句话讲完。
- **不存在的事实不提**，让产物像讲解、不像填表。
- **优先跨信任边界的动作**（用户输入入口、I/O、外呼、加解密），而不是内部纯计算。

## 取舍

**保留**：用户输入入口、文件读写、外部进程调用、网络外呼、加解密/签名、鉴权与会话、数据持久化。

**砍掉**：纯 CSS/样式、i18n 文案、内部纯计算函数、单元测试、构建脚本、健康检查、静态资源、Spring Actuator 之类纯运维端点。

## 方法

1. **定粒度**（默认 B）：
   - **默认走粒度 B**：按子功能分组（登录、下单、文件上传……），每组下列出相关接口。
   - **粒度 A（整项目）**：仅当用户明确说"整个项目""全量梳理""系统全貌"等总览意图时使用。
   - **粒度 C（单接口）**：仅当用户给了具体 URL 或类#方法名时使用。
2. **盘入口**：在选定范围内找 `@RestController`/`@Controller`/`@RequestMapping`、`@Scheduled`、MQ 监听器、CLI `main`、前端 router。
3. **跟链路**：每个入口跟到底——Service、Mapper/Repository、配置文件（`application.yml`）、文件 I/O、外部进程、网络调用、加密点。
4. **写段落**：把上一步抓到的事实**编织成一两段话**讲清楚，自然提到 `(类#方法，文件:行号)` 作为可定位锚点。

## 段落要包含什么

每条接口的描述段必须自然地交代清楚：

- 是哪段代码的哪个入口（含 `文件:行号`）
- 谁在触发
- 当**实际发生**时把以下信息织进描述：读写了哪些文件（路径+格式）、跑了哪些命令（含目的）、调了哪些第三方（协议、字段、鉴权）、做了哪些加解密（算法+对象+为什么）

不存在的就不写。读者读完一段，应能跳到代码并知道这段流程在做什么。

## 输出模板

三种粒度共同遵守一个原则：**先一段总体讲解，再按子功能分组讲接口**。接口描述全部用段落，不用 bullet。

### 粒度 B — 默认（子功能 + 接口）

```
# {范围名} 业务流讲解

## 整体在做什么
80-200 字连贯叙述：这个范围内的代码完成什么业务、由谁触发、关键流程怎么串。

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
```

注意 `/api/users/me` 那条**只有一句话**——它就是个简单读接口，没文件 I/O / 命令 / 第三方 / 加解密。**就让它简短**，不要硬凑。

### 粒度 A — 整项目

```
# {项目名} 业务流讲解

## 核心功能总结
150-300 字连贯叙述：系统在做什么、给谁用、主要角色协作、关键流程怎么串起来。

## 业务流

### 子功能 1：...
（往下结构同粒度 B：子功能分组 + 接口段落）
```

### 粒度 C — 单接口

```
# POST /api/transfer — 跨账户转账

已登录用户发起跨账户转账（com.acme.pay.TransferController#transfer，
TransferController.java:58）。请求落库前先用 HMAC-SHA256 签外呼报文——
避免支付通道篡改；随后调用支付网关 https://pay.example.com/v2/transfer
（POST application/json，Header X-Sign: <hex>，body 含金额、账户、订单号），
客户端是 OkHttp（PayClient.java:71）。回执写库后异步往 /var/log/acme/pay.log
追加一行交易记录。代码在 src/main/java/com/acme/pay/。
```
