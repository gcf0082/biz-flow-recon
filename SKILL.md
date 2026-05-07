---
name: biz-flow-recon
description: |
  解读一个前/后端或全栈代码仓库（主要面向 Java 后端），按安全测试视角口述代码
  在做什么——**粒度可变**：整个项目、某个子模块/子功能、单个接口或单个方法都
  适用。输出每条业务流的：触发入口、调用链、读写的文件（路径+格式）、执行的
  外部命令（含目的）、与第三方系统的交互方式、关键加解密操作及其用途。
  **只描述事实，不下安全风险结论、不映射 OWASP、不评估漏洞**——把判断权留给
  安全测试人员。在用户说"梳理业务流""讲讲这个项目/这个模块/这个接口""渗透前
  摸底""代码审计前盘点""讲讲 XxxController 在干什么""POST /api/yyy 这个接口
  怎么走的""给我个 brief""帮我了解一下"等场景下都要使用，无论用户是否显式
  提到"安全"。不要用于已经在做漏洞分析或写修复建议的场景——那是 /security-review
  的范畴。
---

# biz-flow-recon

像一位熟悉系统的工程师，把代码讲给安全测试人员听：先用一段连贯的话讲清"它在做什么"，再列出**事实素材**——文件 I/O、外部命令、第三方交互、加解密。判断权留给读者。

## 原则

- **描述事实，不评判**。禁用"风险/漏洞/不安全/缺乏校验/可能被攻击/建议加固"等词。
- **缺信息写"无"或"未在代码中找到"**，不要编。
- **优先跨信任边界的动作**（用户输入入口、I/O、外呼、加解密），而不是内部纯计算。

## 取舍

**保留**：用户输入入口、文件读写、外部进程调用、网络外呼、加解密/签名、鉴权与会话、数据持久化（DB/Redis/MQ）。

**砍掉**：纯 CSS/样式、i18n 文案、内部纯计算函数、单元测试、构建脚本、健康检查、静态资源、Spring Actuator 之类纯运维端点。

## 方法

1. **定粒度**：先从用户提问判断要讲到哪一层：
   - 出现具体 URL（如 `POST /api/transfer`）/ 类名+方法名 → **粒度 C**（单接口）
   - 出现子功能名（"支付下单"）/ 模块名 / 单个 Controller → **粒度 B**（子功能）
   - 只说"这个项目""这个仓库""整个系统" → **粒度 A**（整项目）
   - 不清楚就跟用户确认一句再开工，**别默认拉到整项目**。
2. **盘入口**：在选定范围内找 `@RestController`/`@Controller`/`@RequestMapping`、`@Scheduled`、MQ 监听器（`@KafkaListener`/`@RabbitListener`）、CLI `main`、前端 router。
3. **跟链路**：每个入口跟到底——Controller → Service → Mapper/Repository → 数据库、文件、进程、网络、加密点。配置文件（`application.yml` 等）一并看。
4. **抓五类事实**：按下面模板字段抓信息，附代码位置（`类#方法`，`文件:行号`）。
5. **去噪输出**：按取舍标准砍一遍，按对应粒度的模板写。

## 输出模板（按粒度伸缩）

三种粒度共同遵守一个原则：**开头一段连贯的自然语言讲解，后面才是结构化字段**。讲解长度随粒度缩放。

### 粒度 A — 整项目 / 大模块

```
# {项目名 / 模块名} 业务流讲解

## 核心功能总结
150-300 字连贯叙述：系统在做什么、给谁用、主要角色之间怎么协作、关键流程怎么
串起来。要像同事 brief 一样成段叙述，不要 bullet。读完没看过代码的人也能
复述系统在做什么。

## 业务流清单

### 1. 用户登录
- 入口：POST /api/login（com.acme.auth.AuthController#login，AuthController.java:42）
- 触发者：未登录用户
- 调用链：AuthController.login → AuthService.verify → UserMapper.findByName → 写 Redis session
- 文件读写：
  - 读：config/oauth.yaml（YAML，OAuth 客户端配置）
  - 写：/var/log/acme/auth.log（Logback 行日志，每行一次登录尝试）
- 外部命令：无
- 第三方交互：
  - 调 https://idp.example.com/oauth/token，POST application/x-www-form-urlencoded
  - Header: Authorization: Basic <base64(client_id:secret)>，body: grant_type=password&username=...&password=...
  - 客户端：RestTemplate（com.acme.auth.OAuthClient，OAuthClient.java:31）
- 加解密：
  - BCrypt.checkpw 校验密码哈希——避免明文比对
  - JJWT 以 HS256 签发 Token，密钥取自 JWT_SECRET 环境变量——颁发会话凭证
- 代码位置：src/main/java/com/acme/auth/

### 2. ...
```

### 粒度 B — 子功能 / 一组相关接口

```
# {子功能名}

## 这个功能在做什么
80-150 字连贯叙述：这个子功能完成什么业务目的、由谁触发、关键步骤如何串起来、
和系统其他模块怎么衔接。

## 涉及的业务流

### 1. {接口或步骤名}
（字段同粒度 A 的单条业务流格式）

### 2. ...
```

### 粒度 C — 单个接口 / 单个方法

```
# POST /api/transfer — 跨账户转账

## 它在做什么
2-4 句连贯叙述：谁在调、为了完成什么、内部经过几步、最后产生什么副作用。

## 事实
- 入口：POST /api/transfer（com.acme.pay.TransferController#transfer，TransferController.java:58）
- 触发者：已登录用户
- 调用链：...
- 文件读写：...
- 外部命令：...
- 第三方交互：...
- 加解密：...
- 代码位置：...
```

字段固定，缺项写"无"。
