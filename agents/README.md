# biz-flow-recon 项目级子代理（opencode）

本目录下的 8 份子代理定义文件配合 opencode runtime 使用。**Claude Code 用户不需要这些文件**——其内置 Task tool 可由主 agent 直接派发等价子任务。

## 项目级 placement（重要）

将本目录下文件复制到**被分析项目**的 `.opencode/agents/` 目录：

```bash
mkdir -p <被分析项目>/.opencode/agents
cp <skill-pkg>/agents/*.md <被分析项目>/.opencode/agents/
```

**不要放到全局** `~/.config/opencode/agents/`——这些子代理只服务于 biz-flow-recon 工作流，全局可见会污染其他项目的子代理选择。

## 子代理职责

| 文件 | 职责 | 派发时机 | 产物 |
|---|---|---|---|
| `planner.md` | 枚举所有候选接口入口、按子功能划分 | 步骤 2（首发） | `output/_plan.md` |
| `interface-catalog.md` | 扫全仓汇总系统对外暴露的 inbound 接口（攻击面索引） | 步骤 3（并行） | `output/interfaces.md` |
| `outbound-collector.md` | 扫全仓汇总系统作为 client 的 outbound 调用（按目标主机分组） | 步骤 3（并行） | `output/outbound.md` |
| `endpoint-analyst.md` | 单接口深度分析（每接口一个独立实例） | 步骤 3（并行） | `output/endpoint-{METHOD}-{slug}.md` |
| `cross-cut-analyst.md` | 跨接口横向洞察（共享 DTO / Service / 重复模式 / 同源数据流 / 公共控制点） | 步骤 4.5 | `output/cross-cuts.md` |
| `aggregator-writer.md` | 读全部产物撰写 aggregator 索引 | 步骤 5 | `output/features.md` / `features-{slug}.md` / `overview.md` |
| `completion-verifier.md` | 任务收尾审计：缺失 / 孤儿 / 不一致 / 警告统计 | 步骤 6 | `output/_audit.md` |
| `knowledge-extractor.md` | 自动提取项目术语 / 内部服务清单 / 团队约定，写入 knowledge/auto-*.md（可关闭） | 步骤 6.5 | `knowledge/auto-glossary.md` 等 |

主 agent 在 opencode 下**只负责调度**——读配置、读 `_plan.md`、按粒度依次/并行派发上述子代理；不直接产出任何内容文件。

## 默认设定

- 全部子代理 `hidden: true`——不出现在 `@` 自动补全中，仅由主 agent 程序化派发
- 全部子代理 `tools` 限制为 `read / grep / glob / list / bash / write`（关闭 `edit`），并通过 `permission.edit` glob 仅允许写指定的产物文件
- 子代理可在 frontmatter 加 `model: <provider/model>` 指定不同模型——例如让 endpoint-analyst 用便宜模型并行扫描，aggregator-writer / cross-cut-analyst 用 Opus 做深度归纳

## 多语言支持

**Java 优先**（Spring / JAX-RS / Servlet / gRPC / MQ Listener 等）；**Python 同等支持**（FastAPI / Flask / Django / DRF）。其他语言（Go / Node / TS）暂未覆盖。

## 关闭知识库自我演化

在被分析项目的 `biz-flow-recon/knowledge/conventions.md` 写入：

```
## 知识库自我演化
关闭
```

主 agent 即跳过步骤 6.5（不派发 knowledge-extractor）。
