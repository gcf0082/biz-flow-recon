# biz-flow-recon 项目级子代理（opencode）

7 份子代理定义，配合 opencode runtime 使用。**Claude Code 用户不需要这些文件**——内置 Task tool 由主 agent 直接派发等价子任务。

## 项目级 placement

本仓根目录的 `.opencode/` 已是标准 opencode 项目级布局——把整个 `.opencode/` 复制或软链到**被分析项目**根目录即用：

```bash
cp -r <skill-pkg>/.opencode <被分析项目>/.opencode
# 或软链以便 skill 升级自动同步
ln -s <skill-pkg>/.opencode/skills/biz-flow-recon  <被分析项目>/.opencode/skills/biz-flow-recon
ln -s <skill-pkg>/.opencode/agents                 <被分析项目>/.opencode/agents
```

复制后被分析项目结构：

```
<被分析项目>/
└── .opencode/
    ├── skills/biz-flow-recon/    # 含 SKILL.md / templates/ / docs/
    └── agents/                   # 7 份子代理 .md
```

**不要放到全局** `~/.config/opencode/agents/`——本套子代理仅服务 biz-flow-recon 工作流。

## 子代理职责

| 文件 | 职责 | 派发时机 | 产物 |
|---|---|---|---|
| `planner.md` | 枚举入口、按子功能划分 | 步骤 2 | `output/_plan.md` |
| `interface-catalog.md` | 系统对外暴露接口（inbound 攻击面） | 步骤 3 并行 | `output/interfaces.md` |
| `outbound-collector.md` | 系统对外调用（outbound 全局视图） | 步骤 3 并行 | `output/outbound.md` |
| `endpoint-analyst.md` | 单接口深度分析（每接口一实例） | 步骤 3 并行 | `output/endpoint-*.md` |
| `aggregator-writer.md` | 索引 aggregator | 步骤 5 | `output/{features*.md,overview.md}` |
| `completion-verifier.md` | 任务完整性审计 | 步骤 6 | `output/_audit.md` |
| `knowledge-extractor.md` | 知识库自我演化（可关闭） | 步骤 6.5 | `knowledge/auto-*.md` |

主 agent 在 opencode 下**只负责调度**——不直接产出任何内容文件。

## 关闭知识库自我演化

`<被分析项目>/biz-flow-recon/knowledge/conventions.md` 写：

```
## 知识库自我演化
关闭
```

## 多模型混用（opencode 独有）

子代理 frontmatter 加 `model: <provider/model>` 可指定独立模型——例如让
`endpoint-analyst` 用便宜模型并行扫描，`aggregator-writer` 用 Opus 做归纳。
