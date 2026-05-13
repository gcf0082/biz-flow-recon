---
name: biz-risk-analyzer
description: 面向安全测试视角的风险分析——读取 _results/ 中观测点产物，重新追溯源码验证可利用性，产出独立漏洞 finding 文件；**仅在用户显式指名调用 biz-risk-analyzer 时触发**，不要因模糊意图主动触发。
---

# biz-risk-analyzer

面向安全测试视角的风险分析。**主 agent 仅负责调度**——所有内容产出由子代理完成。

## 核心定位

- **消费事实产物**：读取 `<cwd>/_results/` 下的 `endpoint-*.md`，提取观测点作为分析入口
- **重新追溯源码验证可利用性**：不信任 facts 层标记，必须回到源码确认攻击路径真实可达
- **产出风险判断**：对确认可利用的漏洞产出独立 finding 文件；不可利用的观测点记录到 `_dismissed.md`
- **只读事实产物**：只读 `_results/`，所有输出写入 `_risk-results/`

## 前提条件

运行前 `<cwd>/_results/` 必须存在且包含至少一个 `endpoint-*.md`。若前置条件不满足，主 agent 告知用户："_results/ 目录不存在或为空，请先生成事实产物（endpoint-*.md），再运行 biz-risk-analyzer 进行风险分析。"

## 共享原则（子代理适用）

- **做风险判断**——这是本 skill 的核心定位。"代码未做 X 校验" 是事实（从 `_results/` 读取），"攻击者可利用此缺陷做 Y" 是判断（由 **risk-analyst 产出**）
- **验证优先于推断**：每个 finding 必须沿源码数据流确认攻击路径可达。若无法完整追溯（如跨黑盒服务），标注置信度为 `Possible` 而非 `Confirmed`
- **不中断、不询问**：skill 一旦显式调用即全自动跑到底。错误按"显式标注 + 继续"处理
- **每个漏洞一个文件**：独立、可 grep、可 diff
- **代码引用 / 路径一律原样保留**：路径/命令/URL 不截断，与事实产物相同的原样保留原则

## 观测点优先级到分析优先级的映射

观测点档位（描述事实严重程度）→ 分析优先级（决定分析顺序）：

| 观测点档位 | 观测点配色 | 分析优先级 | 说明 |
|---|---|---|---|
| 高 | 红 `#FCE4E4` | P1 必须分析 | 用户输入直接拼入敏感操作等 |
| 中 | 橙 `#FDF2E0` | P2 应当分析 | 部分缓解但仍有风险 |
| 低 | 黄 `#FEF9E7` | P3 选择性分析 | 边缘事实，仅在攻击路径明确时产出 finding |

**非观测点分析**：仅当 risk-analyst 在源码追溯中发现明确的 Critical/High 级别问题且该问题未被标记为观测点时，才额外产出 finding。禁止对无源码证据的推断产出 finding。

## 严重等级与置信度

严重等级独立于观测点档位判定——观测点档位是事实标记，风险严重等级是判断结果：

| 严重等级 | 标准 |
|---|---|
| **Critical** | 攻击者可控输入直接到达敏感操作且无任何前置校验阻断；可导致 RCE / 任意文件读写 / SQL 注入提取全量数据 / 认证绕过 |
| **High** | 攻击者可控输入到达敏感操作但有部分缓解；或需要认证但影响面广 |
| **Medium** | 攻击者输入需特定前置条件才能到达敏感操作；或影响限于当前用户上下文且不跨信任边界 |
| **Low** | 安全事实存在但实际可利用性低（需内部网络/管理员/罕见配置）；信息价值为主 |

| 置信度 | 标准 |
|---|---|
| **Confirmed** | 完整追溯，攻击路径清晰可复现 |
| **Probable** | 总体清晰但有少量不确定环节 |
| **Possible** | 缺乏完整追溯证据（跨黑盒/依赖运行时） |

## 方法（主 agent 纯调度）

| 步骤 | 主 agent 动作 | 派发的子代理 / 决策 |
|---|---|---|
| 0 | 读 knowledge/ 并形成"项目先验摘要" | 读 `<cwd>/.opencode/skills/biz-risk-analyzer/knowledge/` 全量 .md（如有），抽取要点（内部服务定位 / 追溯深度策略 / 执行模式 / 严重等级阈值 / briefing / glossary / modules）→ 内存中的"项目先验摘要"块。**不写任何文件** |
| 1 | 扫描 `_results/` 收集观测点 | 1. 验证 `<cwd>/_results/` 存在且含至少一个 `endpoint-*.md`；否则告知用户前提条件不满足并停止<br>2. 列出所有 `endpoint-*.md` 文件<br>3. 对每个文件，提取 mermaid 流程图中具有观测点配色（红 `#FCE4E4`、橙 `#FDF2E0`、黄 `#FEF9E7`）的节点——搜索 `style <node-id> fill:#FCE4E4` / `fill:#FDF2E0` / `fill:#FEF9E7` 声明，将节点 ID 映射回节点描述文本<br>4. 按 P1 → P2 → P3 排序，写入 `<cwd>/_risk-results/_risk-plan.md`（参考 `templates/_risk-plan.md`）<br>5. 无观测点的接口不出现在计划中 |
| 2 | 并行派发 risk-analyst | 对 `_risk-plan.md` 中每个接口条目，派发一个 `risk-analyst` 子代理。派发 prompt 头部带"项目先验摘要"块 + 接口 scope + endpoint 文件路径 + 观测点列表 + 输出目录 + 严重等级阈值。按 `_risk-plan.md` 优先级排序。默认并行；"项目先验摘要"中"执行模式: 串行"时改串行 |
| 3 | 等待 + 失败重试 | 子代理失败重派最多 2 次；仍失败则在 `<cwd>/_risk-results/` 写占位 `finding-{category}-{endpoint-slug}-0.md` 内容为 `<!-- ⚠ 分析失败：{原因} -->`，**不阻断** |
| 4 | 派发 risk-aggregator | 派发 prompt 头部带"项目先验摘要"块；读取所有 `_risk-results/finding-*.md` + `_risk-results/_dismissed.md`，产出 `_risk-results/_risk-summary.md` |
| 5 | 告知用户产物路径 | `_risk-summary.md` 入口 + finding 文件数 + `_dismissed.md` 不可利用观测点数 |

### 项目先验摘要（派发 prompt 头部块）

主 agent 在所有派发的 prompt 头部插入此块（knowledge 为空时只放占位"项目先验摘要：无"）：

```
[项目先验]
内部服务定位:
  - charge-svc → 代码在 ../services/charge-svc/
  - billing    → 黑盒
追溯深度策略: 智能按需——risk-analyst 根据源码复杂度和攻击路径清晰度自行决定追溯深度，不预设固定层级
执行模式: 串行
严重等级阈值: Low
术语 / 项目要点:
  - <briefing.md / glossary.md / modules/*.md 抽取的关键事实，每条 1 行>
```

## 观测点提取方法（步骤 1）

主 agent 扫描每个 `endpoint-*.md`，按以下规则提取观测点：

1. 搜索文件内 mermaid `flowchart` 块中的 `style` 声明
2. 识别所有 `style <node-id> fill:#FCE4E4`（高/红）、`fill:#FDF2E0`（中/橙）、`fill:#FEF9E7`（低/黄）
3. 将节点 ID 映射回节点描述文本（菱形节点取 `{...}` 内文本、方框节点取 `[...]` 内文本）
4. 预估漏洞类别（injection / path-traversal / xss / authz / authn / crypto / ssrf / deserialization / data-exposure / hardcoded / config / logic / other），基于节点描述中的关键词与关键控制点标注
5. 整合为观测点列表，每个观测点含：节点 ID、档位（高/中/低）、节点描述摘要、预估漏洞类别

## Finding 文件命名

slug 派生规则：路径去除前导 `/` 后小写连字符（`/api/files/upload` → `api-files-upload`）。

| 文件 | 写入者 | 用途 |
|---|---|---|
| `_risk-results/_risk-plan.md` | 主 agent | 观测点扫描计划 |
| `_risk-results/finding-{category}-{endpoint-slug}-{seq}.md` | risk-analyst | 单漏洞独立报告 |
| `_risk-results/_dismissed.md` | risk-analyst | 不可利用观测点记录（无则不写） |
| `_risk-results/_risk-summary.md` | risk-aggregator | 汇总索引 |

**category** 取值：injection / path-traversal / xss / authz / authn / crypto / ssrf / deserialization / data-exposure / hardcoded / config / logic / other

**seq**：同一接口同一 category 从 1 开始递增。

**Finding ID**：`FIND-{category}-{endpoint-slug}-{seq}`（如 `FIND-injection-api-files-upload-1`）

## 工作目录与模板

详见 `docs/workspace-layout.md`。