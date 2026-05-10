# 内部服务定位（auto 提取）

> 从 outbound.md 结合代码定位。本项目的所有 outbound 调用均在同进程内完成，无远程服务。

## 内部服务（同 JVM 进程内）

所有以下服务均为 `com.weihua` 包内的 `@Service` / `@Component` / `@Repository` 组件，同 JVM 调用。

| 服务名 | 类路径 | 类型 | 说明 |
|--------|--------|------|------|
| `DeviceManagementService` | `service/DeviceManagementService.java` | 内部（同进程） | 设备管理核心业务——密码变更、设备校验。通过 `@Autowired` 注入，无远程调用 |
| `AuthenticationService` | `security/AuthenticationService.java` | 内部（同进程） | 认证服务——内存用户表登录、Token 验证、权限查询 |
| `AuthorizationService` | `security/AuthorizationService.java` | 内部（同进程） | 授权服务——权限检查（`DEVICE_MANAGE`）、部门访问控制 |
| `AuditService` | `service/AuditService.java` | 内部（同进程） | 审计服务——操作记录录入与查询 |
| `NotificationService` | `service/NotificationService.java` | 内部（同进程） | 通知服务——当前仅写日志，无实际推送 |
| `ScriptExecutor` | `util/ScriptExecutor.java` | 内部（同进程） | 脚本执行封装——调用 `CommandExecutor` |
| `CommandExecutor` | `util/CommandExecutor.java` | 内部（同进程） | ProcessBuilder 命令执行封装 |
| `ParameterValidator` | `util/ParameterValidator.java` | 内部（同进程） | 参数校验工具 |
| `SecurityLogger` | `util/SecurityLogger.java` | 内部（同进程） | 安全日志工具，使用 `SECURITY` / `OPERATION` Logger |
| `DeviceRepository` | `repository/DeviceRepository.java` | 内部（同进程） | 设备数据访问层（内存 HashMap） |
| `OperationLogRepository` | `repository/OperationLogRepository.java` | 内部（同进程） | 操作日志数据访问层（内存 ConcurrentHashMap） |

## 外部服务

**无**。项目不存在 HTTP/RPC/消息队列等远程服务调用。

## 黑盒 / 外部脚本

| 目标 | 类型 | 说明 |
|------|------|------|
| `/opt/change_device.sh` | 外部 shell 脚本 | 通过 ProcessBuilder 执行，路径硬编码。该脚本内部使用 `expect` + `ssh` 连接受管网络设备（IP 由用户输入传入）。脚本在项目根目录有开发/测试副本 `change_device.sh` |
