<!--
风险分析汇总模板。risk-aggregator 子代理写入 _risk-results/_risk-summary.md。
可被被分析项目内的同名文件覆盖。

按严重等级从 Critical 到 Low 排列全部发现，每条含 Finding ID + 标题 + 关联接口 +
置信度 + CWE。汇总不重复 finding 正文——仅列标题、严重等级、接口链接；
阅读细节点击对应 finding 文件。

接口链接使用相对路径指向 _results/ 下的 endpoint-*.md（如
../_results/endpoint-POST-api-files-upload.md）。
Finding 链接使用同目录相对路径（如 finding-injection-api-files-upload-1.md）。

路径 / URL / 引用一律原样保留，禁止 ... / … 截断。
-->

# {项目名} 风险分析摘要

生成时间：{ISO}
分析范围：`_results/` 中 {N} 个接口，其中 {M} 个含观测点（已分析）
数据来源：事实分析产物 + 源码追溯验证

## 执行摘要

2-5 句话描述整体风险态势：是否存在 Critical/High 级别漏洞、主要风险领域、最需优先修复的问题。

## 统计

| 严重等级 | 数量 |
|---|---|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |

| 置信度 | 数量 |
|---|---|
| Confirmed | {n} |
| Probable | {n} |
| Possible | {n} |

## 漏洞类型分布

| CWE 类型 | 数量 | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| CWE-XX: {name} | {n} | {n} | {n} | {n} | {n} |

## 按严重等级排列的全部发现

### Critical

- [FIND-{...}] {标题} — [{METHOD} {path}](../_results/endpoint-{METHOD}-{slug}.md) · {置信度} · CWE-{number}

### High

- ...

### Medium

- ...

### Low

- ...

（无某等级发现时写"无"）

## 按接口聚合

| 接口 | finding 数量 | 最高严重等级 | 不可利用观测点数 |
|---|---|---|---|
| [POST /api/files/upload](../_results/endpoint-POST-api-files-upload.md) | 3 | Critical | 1 (黄) |
| ... | ... | ... | ... |

## 不可利用观测点

从 `_dismissed.md` 汇总：

| 接口 | 观测点档位 | 不可利用原因 |
|---|---|---|
| ... | ... | ... |

（无不可利用观测点时写"无"）

## 未覆盖的接口

以下接口因分析失败未产出 finding（如无此情况写"无"）：

- {METHOD} {path} — 分析失败原因