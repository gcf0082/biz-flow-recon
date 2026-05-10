<!-- 大型项目子任务拆分计划。skill 判定无法一次性处理时写入 output/_plan.md。可被被分析项目内的同名文件覆盖。 -->

# {项目名} — 子任务拆分

总体策略：按 {目录/包/maven 模块/业务域} 划分。

## 子任务

```yaml
sub_features:
  - name: 认证与会话
    slug: auth
    scope:
      - src/main/java/com/acme/auth/
      - src/main/java/com/acme/session/
    output: features-auth.md

  - name: 支付
    slug: pay
    scope:
      - src/main/java/com/acme/pay/
      - services/pay-gw/
    output: features-pay.md
```
