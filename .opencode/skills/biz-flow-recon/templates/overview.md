<!--
Aggregator 索引模板。每个接口的详情位于各自的 endpoint-*.md 中——本文件仅提供
一句话概述与链接。
- 小型项目：直接列出全部 endpoint-*.md（按子功能分组）。
- 大型项目：列出各 features-{slug}.md（每个子功能一份子索引），endpoint-*.md
  链接挂在 features-{slug}.md 内。

子功能与接口均按 _plan.md 的审计优先级 high → medium → low 排序展示；每条接口
链接旁附 `· 优先级 高/中/低` 标签便于扫读。
-->

[对外接口清单](interfaces.md)

# {项目名} 业务流讲解

## 核心功能总结

150-300 字段落形式叙述：系统的功能、目标用户、主要角色之间的协作、关键流程的串接关系。读完后未阅读代码者亦能复述系统功能。

## 接口索引

**小型项目** — 按子功能分组直接列出接口（子功能与接口均 high → medium → low 排序）：

### 文件管理
- [POST /api/files/upload](endpoint-POST-api-files-upload.md) · 优先级 高 —— 上传业务文件并触发扫描
- [GET /api/files/{name}](endpoint-GET-api-files-name.md) · 优先级 高 —— 下载已上传文件

### 用户中心
- [POST /api/users/login](endpoint-POST-api-users-login.md) · 优先级 高 —— 用户名 + 密码登录签发 token
- [GET /api/users/search](endpoint-GET-api-users-search.md) · 优先级 中 —— 按昵称模糊查询
- [GET /api/users/me](endpoint-GET-api-users-me.md) · 优先级 低 —— 读取当前会话自身资料

**大型项目** — 改用一级子功能索引（替代上述接口分组）：

- **认证与会话** · 优先级 高 — [features-auth.md](features-auth.md)：登录、会话、权限校验
- **支付** · 优先级 高 — [features-pay.md](features-pay.md)：支付、对账、退款
- **订单管理** · 优先级 中 — [features-order.md](features-order.md)：下单、修改、查询
- **用户中心** · 优先级 低 — [features-user.md](features-user.md)：资料读写

## 未能追溯的引用

合并所有 `endpoint-*.md`（小型项目）或 `features-*.md`（大型项目）末尾的"未能追溯的引用"，去重后集中列出；无则**略去整节**。
