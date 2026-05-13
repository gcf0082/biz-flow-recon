<!--
本目录放 biz-risk-analyzer 项目特有说明。主 agent 在调度前会读取本目录全量
.md 后形成"项目先验摘要"块，并把它拼入派发给每个子代理的 prompt——子代
理不直接读本目录，所以摘要要点必须能被主 agent 抽出。

风险分析新增的"严重等级阈值"开关写入本目录的 conventions.md。
若 conventions.md 不存在，默认值为 Low。

把这份示例文件复制改名为对应职责的文件后填写：

  briefing.md       项目安全相关说明（已知安全机制、历史漏洞、合规要求等）
  glossary.md       项目特有术语
  conventions.md    团队约定 + 风险分析行为开关（见下方样例）
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

## 严重等级阈值
Low
```

biz-risk-analyzer 新增行为开关：

- **严重等级阈值**：控制 risk-analyst 是否为低严重等级观测点产出 finding。
  - `Low`（默认）：报告所有等级，仅不可利用的写入 `_dismissed.md`
  - `Medium`：Medium 及以上才产出 finding，低等级观测点全部写入 `_dismissed.md`
  - `High`：High 及以上才产出 finding

其余开关（内部服务定位 / 递归追溯深度 / 执行模式）用法相同。
主 agent 据此组装"项目先验摘要"。