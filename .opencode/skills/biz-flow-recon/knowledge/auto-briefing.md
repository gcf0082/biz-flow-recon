# Device Management System 项目说明（auto 提取）

> 自动提取自代码与产物——供用户 review 后转写为正式 `briefing.md`。
> 项目描述：`SpringBoot demo for security static call chain analysis`

## 技术栈

- **后端框架**：Spring Boot 2.7.14
- **Java 版本**：11
- **构建工具**：Maven（JAR 打包）
- **鉴权**：Spring Security HTTP Basic（.anyRequest().authenticated()），CSRF 禁用
- **参数校验**：spring-boot-starter-validation + `@Valid` / `@NotBlank` / `@Pattern`
- **API 文档**：Swagger / Springfox（`springfox-swagger-annotations 1.6.12`，路径 `/api-docs`）
- **序列化**：Jackson（jackson-databind）
- **工具库**：Lombok、Apache Commons Lang3
- **日志**：SLF4J（Spring Boot 默认 Logback，通过 `SecurityLogger` 使用 `SECURITY` / `OPERATION` 两个 Logger name）
- **持久化**：无数据库——所有数据存放于进程内 `HashMap` / `ConcurrentHashMap`，重启即失
- **外部通信**：无 HTTP/RPC 客户端——唯一 outbound 为 `ProcessBuilder` 执行 `/opt/change_device.sh`（内部用 expect+ssh）

## 模块布局（包结构）

```
com.weihua
├── DeviceManagementApplication.java     # 入口
├── config/
│   └── SecurityConfig.java              # Spring Security 配置
├── controller/
│   ├── DeviceController.java            # /api/device/* 基础设备操作
│   ├── DeviceConfigController.java      # /api/device/config/* 配置管理
│   ├── DeviceMonitorController.java     # /api/device/monitor/* 监控
│   ├── UserController.java              # /api/user/* 用户认证
│   ├── BatchOperationController.java    # /api/batch/* 批量操作
│   └── HealthController.java            # /api/system/* 系统运维
├── service/
│   ├── DeviceManagementService.java     # 设备管理核心逻辑
│   ├── AuditService.java                # 审计记录
│   └── NotificationService.java         # 通知（仅日志）
├── security/
│   ├── AuthenticationService.java       # 认证：内存用户表 + token 校验
│   └── AuthorizationService.java        # 授权：权限检查 + 部门访问控制
├── repository/
│   ├── DeviceRepository.java            # 设备内存数据库
│   └── OperationLogRepository.java      # 操作日志内存存储
├── model/
│   ├── ChangePasswordRequest.java       # 密码变更 DTO
│   ├── DeviceConfigRequest.java         # 配置更新 DTO
│   ├── DeviceInfo.java                  # 设备信息实体
│   ├── UserLoginRequest.java            # 登录 DTO
│   ├── OperationLog.java                # 操作日志实体
│   ├── OperationResult.java             # 统一操作结果
│   └── AuthToken.java                   # Token 模型（定义但未使用）
└── util/
    ├── ParameterValidator.java          # IP/密码/用户名校验
    ├── ScriptExecutor.java              # 脚本执行封装
    ├── CommandExecutor.java             # ProcessBuilder 封装
    └── SecurityLogger.java              # 安全/操作日志工具
```

## 对外接口风格约定

- **路径模式**：`/api/{domain}/{action}` 或 `/api/{domain}/{resource}/{identifier}`
- **鉴权方式**：
  - 所有接口统一由 Spring Security HTTP Basic 拦截（`.anyRequest().authenticated()`）
  - 部分接口额外校验 `X-Auth-Token` header（自定义 token，非 JWT）
  - 操作身份通过 `X-Operator-Id` header 传递
- **响应格式**：不统一——有的返回 `OperationResult {success, message, errorCode, timestamp, data}`，有的直接返回 `Map` 或 `ResponseEntity<String>`
- **内容协商**：`application/json`（Spring Boot 默认）
- **无认证放行路径**：未配置 `/api/public/*` 等匿名放行规则

## 跨模块共用机制

- **统一 Token 校验**：`validateAuthToken()` 仅在 `DeviceController` 中实现（`token != null && length > 10`），非全局 Filter
- **安全日志**：`SecurityLogger` 组件（`@Component`），使用 `SECURITY` 和 `OPERATION` 两个 Logger name 输出 SLF4J 日志
- **参数校验**：`ParameterValidator` 组件提供 IP 格式、密码强度、弱口令判断、内网 IP 判断
- **操作审计**：`AuditService` 记录操作成功/失败到 `OperationLogRepository`（内存）
- **设备数据源**：`DeviceRepository` 提供统一设备查询接口（内存 HashMap）
- **脚本执行**：`ScriptExecutor` → `CommandExecutor`（ProcessBuilder）执行 shell 脚本

## 特殊查找线索

- 所有数据源位于进程内 `static` 初始化块（`HashMap` / `ConcurrentHashMap`），无配置文件、无数据库迁移脚本
- 应用配置文件仅 `src/main/resources/application.properties`
- Swagger 文档路径 `/api-docs`
- 脚本路径硬编码 `/opt/change_device.sh`
- 多端点存在**桩实现**（`updateConfig`、`restoreConfig`、`rebootDevice`、`reloadConfig` 直接返回成功，无实际操作）
- 批量作业无异步消费方——`POST /api/batch/execute` 仅创建记录，无后台线程执行
