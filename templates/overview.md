<!--
Aggregator 索引模板。每个接口的详情都在各自的 endpoint-*.md 里——这里只一句话概述 + 链接。
- 小项目：直接列所有 endpoint-*.md（按子功能分组）。
- 大项目：列各 features-{slug}.md（每个子功能一份子索引），endpoint-*.md 链接挂在 features-{slug}.md 里。
-->

# {项目名} 业务流讲解

## 核心功能总结

150-300 字成段叙述：系统在做什么、给谁用、主要角色怎么协作、关键流程怎么串起来。读完没看过代码的人也能复述。

## 接口索引

**小项目** — 直接按子功能分组列接口：

### 子功能 1：文件管理
- [GET /api/files/{name}](endpoint-GET-api-files-name.md) —— 下载导出文件
- [POST /api/jobs/run-report](endpoint-POST-api-jobs-run-report.md) —— 触发离线对账
- [GET /api/users/me](endpoint-GET-api-users-me.md) —— 读取自己的资料

### 子功能 2：...
...

**大项目** — 改用一级子功能索引（替代上面的接口分组）：

- **认证与会话** — [features-auth.md](features-auth.md)：登录、会话、权限校验
- **订单管理** — [features-order.md](features-order.md)：下单、修改、查询
- **支付** — [features-pay.md](features-pay.md)：支付、对账、退款
- ...

## 未跟到的引用

合并所有 `endpoint-*.md`（小项目）或 `features-*.md`（大项目）末尾的"未跟到的引用"，去重后集中列出；没有就**整节略掉**。
