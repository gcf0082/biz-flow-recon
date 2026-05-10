<!--
本目录放 biz-flow-recon 项目特有说明。主 agent 在调度前会读取本目录全量
.md 后形成"项目先验摘要"块，并把它拼入派发给每个子代理的 prompt——子代
理不直接读本目录，所以摘要要点必须能被主 agent 抽出。

把这份示例文件复制改名为对应职责的文件后填写：

  briefing.md       项目高层说明（技术栈、模块布局、外部接口风格、共用机制等）
  glossary.md       项目特有术语
  conventions.md    团队约定 + 配置开关（结构见下方样例）
  modules/*.md      每个子模块一份说明

内容保持精炼——冗余反而降低准确度。
-->

# conventions.md 配置开关样例

```markdown
## 内部服务定位
- charge-svc → 代码在 ../services/charge-svc/
- idp-svc    → 代码在 ../services/idp-svc/
- billing    → 黑盒（外部团队维护，不予追溯）

## 递归追溯深度
3

## 执行模式
并行
```

主 agent 据此组装"项目先验摘要"：内部服务定位决定 endpoint-analyst 跨仓追溯落点；递归追溯深度覆盖 endpoint-analyst 默认值（默认 2）；执行模式决定主 agent 是并行还是串行派发子代理。
