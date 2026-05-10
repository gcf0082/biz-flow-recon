# 项目特有术语（auto 提取）

> 自动提取——用户手填的 `glossary.md` 中已存在的条目不会出现在这里。

## 包名 / 模块名规律

| 术语 | 说明 |
|------|------|
| `com.weihua` | 项目根包名，非 `com.example`（虽 pom.xml groupId 为 `com.example`） |
| `controller` | REST 接口层，所有 `@RestController` 在此 |
| `service` | 业务逻辑层，含 `DeviceManagementService` / `AuditService` / `NotificationService` |
| `security` | 认证与授权组件——`AuthenticationService`（用户/密码/token）+ `AuthorizationService`（权限检查） |
| `repository` | 数据访问层——全部基于内存 `HashMap` / `ConcurrentHashMap` |
| `model` | DTO + 实体 |
| `util` | 工具类——参数校验、脚本执行、日志 |

## 高频 DTO 与业务含义

| DTO 类 | 文件 | 业务含义 | 关键字段 |
|--------|------|---------|---------|
| `ChangePasswordRequest` | `model/ChangePasswordRequest.java` | 设备密码变更请求 | deviceIp, username, oldPassword, newPassword, operatorId, department |
| `DeviceConfigRequest` | `model/DeviceConfigRequest.java` | 设备配置更新请求 | deviceIp, configType, configContent, operatorId |
| `UserLoginRequest` | `model/UserLoginRequest.java` | 用户登录请求 | username, password |
| `DeviceInfo` | `model/DeviceInfo.java` | 设备信息实体 | deviceIp, deviceName, deviceType, status, location, lastModified, managedBy |
| `OperationLog` | `model/OperationLog.java` | 操作日志实体 | id, operatorId, operationType, targetDevice, operationStatus, operationTime |
| `OperationResult` | `model/OperationResult.java` | 统一操作响应（带 `success`/`message`/`errorCode`/`timestamp`/`data`） | success, message, errorCode, timestamp, data |
| `AuthToken` | `model/AuthToken.java` | Token 模型——已定义（含 userId/username/expireTime/permissions/department）但**未在真实流程中使用** | token, userId, username, expireTime, permissions, department |
| `BatchRequest` | 内部类于 `BatchOperationController.java:124` | 批量操作请求（`operationType` + `deviceIps` 列表） | operationType, deviceIps |

## 内部专有 Header

| Header | 说明 | 使用模式 |
|--------|------|---------|
| `X-Operator-Id` | 操作员标识 | 几乎所有受保护端点均接收，但用法不一致：部分端点仅用于日志记录，部分用于授权检查，部分直接忽略 |
| `X-Auth-Token` | 应用层认证令牌 | 仅 `DeviceController.changeDevicePassword` 与 `UserController.validateToken` 校验；非 JWT、非全局 Filter |

## 预置数据常量

| 数据 | 值 | 所在位置 |
|------|-----|---------|
| 默认认证凭据 | `admin / admin123` | `application.properties:5-6` |
| 硬编码用户池 | admin/admin123, operator1/pass123, engineer/engineer456 | `AuthenticationService.java:18-21` |
| 硬编码设备 | 192.168.1.100（Router-Core-01）, 192.168.1.101（Switch-Access-01）, 10.0.0.50（Firewall-Main） | `DeviceRepository.java:22-24` |
| 弱口令列表 | 123456, password, 12345678, qwerty, admin, letmein | `ParameterValidator.java:97` |
| 权限字符串 | DEVICE_MANAGE, USER_VIEW, CONFIG_EDIT, DEVICE_VIEW, DEVICE_CONFIG | `AuthenticationService.java:19-21` |

## 内网 IP 判断逻辑

`ParameterValidator.isInternalIp()`（`ParameterValidator.java:106-108`）仅通过 `String.startsWith()` 前缀匹配以下三段：

- `10.`（覆盖 10.0.0.0/8）
- `192.168.`（覆盖 192.168.0.0/16）
- `172.16.`（**仅覆盖 172.16.0.0/16 单段，未覆盖 172.17.0.0–172.31.255.255**）

## 错误码约定

注意：`OperationResult.errorCode` 字段使用大写蛇形命名，非 HTTP 状态码：

| errorCode | 含义 | 出现端点 |
|-----------|------|---------|
| `VALIDATION_ERROR` | 参数校验失败 | changePassword |
| `AUTHORIZATION_FAILED` | 授权校验失败 | changePassword |
| `DEVICE_NOT_FOUND` | 设备未注册 | changePassword, updateConfig, backupConfig |
| `DEVICE_UNREACHABLE` | 设备不可达 | changePassword |
| `SCRIPT_EXECUTION_FAILED` | 脚本执行失败 | changePassword |
| `INVALID_IP` | 无效 IP 地址 | validate |
| `DEVICE_UNKNOWN` | 设备未在数据库中找到 | validate |
| `AUTH_REQUIRED` | 需要认证 | changePassword |
| `ACCESS_DENIED` | 访问被拒绝 | changePassword |
| `JOB_NOT_FOUND` | 批量作业未找到 | cancelJob |
| `INVALID_STATE` | 作业状态不允许操作 | cancelJob |

## Token 生成 / 校验规则

- 生成：`"token_" + System.currentTimeMillis()`（`UserController.java:32`）——无签名、无 JWT 格式
- 校验：`token != null && token.length() > 10`（`AuthenticationService.java:49` / `DeviceController.java:95`）——无签名验证、无过期判断、无存储比对
