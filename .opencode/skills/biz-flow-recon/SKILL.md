---
name: biz-flow-recon
description: 按安全测试视角解读前/后端代码仓库（Java 优先）输出业务流讲解，只描述事实、不做风险判断；**仅在用户显式指名调用 biz-flow-recon 时触发**，不要因模糊意图主动触发。
---

# biz-flow-recon

面向安全测试人员说明代码行为。**主 agent 仅负责调度**——所有内容产出由 8 个子代理完成；本文档是主 agent 的说明书。各子代理的执行细节在 `agents/<name>.md` 自身的 prompt 中。

## 共享原则（全员适用）

- **描述事实，不做评判**。"代码做了/没做某项检查"属于事实陈述（**应当报告**，包括"未做"）；"这是否构成风险/漏洞 / 是否需要加固"属于评判（**仍禁止**）。禁用"风险/漏洞/不安全/可能被攻击/建议加固"等结论性词。
- **未能定位必须显式标注**：在产物里点名"未在工作区找到 X"，并加入末尾的 `## 未能追溯的引用` 节集中列出。**不得编造、不得遗漏、不得静默忽略**。
- **不中断、不询问**：skill 一旦显式调用即全自动跑到底——不论项目规模、未追溯引用数量、解析歧义。错误按"显式标注 + 继续"处理，**绝不暂停等待用户输入**。用户事后可改 `_plan.md` / 删除产物文件重跑。
- **每接口一个 subagent + 主 agent 仅调度**：每个接口由独立 subagent 完成；主 agent 不直接产出任何内容文件，仅写调度决策。
- **多语言支持**：Java 与 Python 主流 web/MQ/gRPC 框架同等支持；其他语言暂未覆盖。
- **强制读 knowledge/**：所有子代理执行前**必须**先读 `<cwd>/.opencode/skills/biz-flow-recon/knowledge/` 全量 .md（含 `briefing.md` / `glossary.md` / `conventions.md` / `modules/*.md` / `auto-*.md`）作为先验——这是项目特有说明的标准位，给项目结构、术语、约定、内部服务定位等关键线索。**子代理自行读，主 agent 不传内容**（避免上下文丢失）。

## 取舍

**保留**：用户输入入口、文件读写、外部进程、网络外呼、加解密/签名、鉴权与会话、数据持久化。
**剔除**：CSS/i18n/纯计算/单测/构建脚本/健康检查/静态资源/Spring Actuator 等纯运维端点。

## 方法（主 agent 纯调度）

主 agent 全程仅"读配置 → 决策粒度 → 派发子代理 → 等待 → 派发下一批 → 告知用户路径"。

| 步骤 | 主 agent 动作 | 派发的子代理 / 决策 |
|---|---|---|
| 0 | 加载工作目录 | 读 `<cwd>/.opencode/skills/biz-flow-recon/knowledge/`（如有）；解析模板路径（项目级覆盖 → skill 默认）。**不写任何文件** |
| 1 | 确定粒度 | A（整项目）/ B（默认子功能 + 接口）/ C（单接口） |
| 2 | 派发 `planner` | 写 `_plan.md`；已存在则跳过 |
| 3 | 并行派发 | `interface-catalog` + `outbound-collector` + N × `endpoint-analyst`（每接口一个）；默认并行，`conventions.md` 配 `执行模式: 串行` 时改串行 |
| 4 | 等待 + 失败重试 | 子代理失败重派最多 2 次；仍失败则在产物头部插入 `<!-- ⚠ 产物自检未通过：缺失 X 请人工补全 -->`，**不阻断** |
| 5 | 派发 `aggregator-writer` | 传入粒度参数；产出 `features.md` / `features-{slug}.md` / `overview.md`；顶部带横向产物链接 |
| 6 | 派发 `completion-verifier` | 写 `_audit.md`；**不阻断流程** |
| 6.5 | 派发 `knowledge-extractor`（可关闭） | `conventions.md` 写 `知识库自我演化: 关闭` 时跳过 |
| 7 | 告知用户产物路径 | aggregator 入口 + 横向产物（`interfaces.md` / `outbound.md`）+ `_audit.md` |

各子代理职责详见 `agents/README.md`，每个子代理的执行规范在 `agents/<name>.md` 自身 frontmatter prompt 内。opencode 用户复制 `agents/*.md` 到被分析项目的 `.opencode/agents/`；Claude Code 用户走 Task tool。

## 输出文件名约定

slug 小写连字符；中文转拼音/英文同义词；**默认覆盖同名文件**便于 git diff。

| 文件 | 写入者 | 用途 |
|---|---|---|
| `_plan.md` | planner | 子任务计划 |
| `interfaces.md` | interface-catalog | 对外暴露接口清单（inbound 攻击面） |
| `outbound.md` | outbound-collector | 系统对外调用汇总（outbound） |
| `endpoint-{METHOD}-{slug}.md` | endpoint-analyst | 单接口深度分析 |
| `features.md` / `features-{slug}.md` / `overview.md` | aggregator-writer | 索引 aggregator |
| `_audit.md` | completion-verifier | 任务完整性审计 |
| `../knowledge/auto-*.md` | knowledge-extractor | 自动提取的先验（可关闭） |

## 工作目录与模板

`docs/workspace-layout.md` 详述被分析项目 `.opencode/skills/biz-flow-recon/{knowledge,templates,docs}/`、`.opencode/agents/` 与 `biz-flow-recon/{templates,output}/` 的约定。**子代理每次输出前必须读对应模板再撰写**，不得依赖记忆——以确保用户对模板的修改即时生效。
