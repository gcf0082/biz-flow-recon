<!--
biz-flow-recon 子任务拆分计划模板（大项目模式）。
本文件可被被分析项目里的 `biz-flow-recon/templates/_plan.md` 覆盖。
skill 在大项目模式下盘完入口、判完规模后写到 output/_plan.md，
再逐条（或并行）执行每个子任务。
-->

# {项目名} — 子任务拆分

总体策略一句话：按 {目录/包/maven 模块/业务域} 划分。

## 子任务

```yaml
sub_features:
  - name: 认证与会话
    slug: auth
    scope:
      - src/main/java/com/acme/auth/
      - src/main/java/com/acme/session/
    output: features-auth.md

  - name: 订单管理
    slug: order
    scope:
      - src/main/java/com/acme/order/
    output: features-order.md

  - name: 支付
    slug: pay
    scope:
      - src/main/java/com/acme/pay/
      - services/pay-gw/
    output: features-pay.md

  - name: 用户中心
    slug: user
    scope:
      - src/main/java/com/acme/user/
    output: features-user.md
```

## 执行说明

- 默认串行执行，每个子任务跑完写一份 `features-{slug}.md`
- 全部完成后写 `overview.md` 汇总
- 重跑时已存在的 `features-*.md` 默认跳过；要重做请先删除对应文件
- 用户在 `knowledge/conventions.md` 写 `执行模式: 并行` 时用 Task subagent 并行派发
