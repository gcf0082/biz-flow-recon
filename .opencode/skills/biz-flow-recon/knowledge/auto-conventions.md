# 观察到的团队约定（auto 提取）

> 自动提取自产物与代码。部分约定源于"demo"性质，实际团队项目可能不同。

## 代码组织约定

- **Controller 层**：`@RestController` + `@RequestMapping("/api/{domain}")`，使用 `@Autowired` 字段注入（非构造器注入）
- **Service 层**：`@Service`，单一职责，如 `DeviceManagementService` 处理设备业务、`AuditService` 处理审计、`NotificationService` 处理通知
- **Repository 层**：`@Repository`，数据访问层，全部基于内存集合（`HashMap` / `ConcurrentHashMap`）
- **DTO 与 Entity 混合**：`model/` 包同时包含请求 DTO（`ChangePasswordRequest`）和实体（`DeviceInfo`、`OperationLog`），无严格分层
- **Lombok 广泛使用**：`@Data`、`@AllArgsConstructor`、`@NoArgsConstructor`

## 鉴权约定

- 全局 Spring Security HTTP Basic，CSRF 禁用
- 自定义 token 校验（`X-Auth-Token`）仅在 `DeviceController` 中做不健壮的长度检查
- `X-Operator-Id` 作为**应用层操作员标识**，但未被一致验证——部分端点仅记录日志，部分用于授权判断，部分完全忽略
- `AuthorizationService.checkAuthorization()` 要求 `DEVICE_MANAGE` 权限，已在类路径但**不是每个端点都调用**
- 应用层认证（`AuthenticationService` 内存用户）与 Spring Security HTTP Basic 认证**相互独立、互不关联**

## 日志约定

- 通过 `SecurityLogger` 组件（`@Component`）统一写日志
- 两个 Logger name：`SECURITY`（安全事件）、`OPERATION`（操作日志）
- 日志事件类型（`logSecurityEvent` 的第一个参数）使用大写蛇形命名：`LOGIN_SUCCESS`、`LOGIN_FAILED`、`PASSWORD_CHANGE_START`、`BATCH_START`、`API_REQUEST` 等
- 访问拒绝使用 `logAccessDenied` 方法，输出 WARN 级别

## 密码策略约定

- 长度 6–32 字符
- 无大写/小写/数字/特殊字符复杂度要求
- 新旧密码不可相同
- 硬编码 6 个弱口令黑名单
- 密码**明文存储**于内存 `HashMap`，**明文比对**（`String.equals()`）

## IP 校验约定

- 格式校验：`ParameterValidator.validateIpAddress()`（IPv4 四段 `0-255` 正则+数值验证）
- 内网判断：`ParameterValidator.isInternalIp()` 仅前缀匹配 `10.` / `192.168.` / `172.16.`
- **以上校验方法存在但各端点调用不一致**——部分端点两个都调用，部分不调用任何校验

## 统一响应约定

- `OperationResult` 类提供 `success()` / `failure()` 静态工厂方法
- 响应包含 `success` / `message` / `errorCode` / `timestamp` / `data` 字段
- 但不是所有 Controller 都使用 `OperationResult`——部分端点直接返回 `ResponseEntity<Map>` 或 `ResponseEntity<String>`

## API 路径命名约定

- 资源标识使用 path variable（`{deviceIp}`、`{jobId}`、`{username}`）
- 动作通过 HTTP Method（`POST` 创建/修改、`GET` 查询、`DELETE` 删除）+ 路径后缀（`/changePassword`、`/config/update`、`/monitor/list`）
- 无版本前缀（如 `/api/v1/` 不存在）

## 配置位置

- 单配置文件：`src/main/resources/application.properties`
- 无多环境 profile（无 `application-dev.yml`、`application-prod.yml` 等）
- Spring Security 默认用户在 `application.properties` 中配置

## 已知的桩代码 / 占位实现

以下方法标注为"stub"——接受请求、返回成功但**不执行实际操作**：

- `DeviceConfigController.updateDeviceConfiguration()`（`/api/device/config/update`）
- `DeviceConfigController.restoreConfig()`（`/api/device/config/restore`）
- `DeviceMonitorController.rebootDevice()`（`/api/device/monitor/{deviceIp}/reboot`）
- `HealthController.reloadConfig()`（`/api/system/reload`）

## 批量作业约定

- 任务 ID 格式：`"job_" + System.currentTimeMillis()`
- 任务状态流转：`RUNNING` → `COMPLETED` / `FAILED` / `CANCELLED`
- 所有任务数据存放于内存 `ConcurrentHashMap`，无持久化
- 无异步/定时消费后台线程——作业状态仅在被其他端点查询/取消时变化

## 缺少的通用机制（demo 项目特点）

- 无统一异常处理（`@ControllerAdvice`）
- 无请求/响应日志拦截器
- 无 X-Trace-Id 等分布式追踪 header
- 无速率限制
- 无单元测试验证到的安全控制逻辑
