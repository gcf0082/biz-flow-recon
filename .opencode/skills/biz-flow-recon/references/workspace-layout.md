# 工作目录约定

biz-flow-recon 将 skill 配置（含知识库）与项目级**模板覆盖 / 产物**分离：

- **skill 子树**（`.opencode/skills/biz-flow-recon/`）：SKILL.md / references/ / knowledge/
- **项目根 `biz-flow-recon/`**：仅留 `references/`（项目级覆盖，可选）
- **项目根 `_results/`**：分析产物（与 `.opencode/`、`biz-flow-recon/` 并列在被分析项目根）

## 目录结构

被分析项目根目录下：

```
<被分析项目>/
├── .opencode/                    # opencode runtime 加载入口
│   ├── skills/biz-flow-recon/
│   │   ├── SKILL.md              # 主调度任务说明书
│   │   ├── references/           # 默认输出模板 & 参考文档
│   │   └── knowledge/            # 项目专属先验（主 agent 读取后摘要拼入派发 prompt）
│   └── agents/                   # 5 份子代理 .md
├── biz-flow-recon/               # 项目级覆盖（可选）
│   └── references/
│       ├── default.md
│       ├── overview.md
│       └── _plan.md
└── _results/                     # skill 自动写入产物
    ├── _plan.md / interfaces.md
    ├── endpoint-*.md
    ├── features*.md / overview.md
    └── _audit.md
```

`.opencode/skills/biz-flow-recon/{SKILL.md,knowledge/,references/}` 与 `.opencode/agents/`、`biz-flow-recon/references/`、`_results/` 目录名为**固定约定**。

## 知识库（knowledge/）

放项目特有说明，给项目结构、术语、约定、内部服务定位等关键线索。**主 agent 在调度前读全量 .md，抽取要点形成"项目先验摘要"**，并把它作为头部块拼入派发给每个子代理的 prompt——子代理不直接读本目录。文件根据需要增减，不做固定限制。内容**应保持精炼**——冗余反而降低准确度。

## 模板覆盖（references/）

将 skill 包 `.opencode/skills/biz-flow-recon/references/` 下对应文件复制到项目 `biz-flow-recon/references/` 后修改。skill 检测到项目内同名文件即优先使用。

支持的文件名：`default.md`、`overview.md`、`_plan.md`。粒度 C（单接口）也走 `default.md`（仅截取单接口块）。

## 输出（_results/）

产物结构 = 每接口一份独立文件 + 横向产物（`interfaces.md`）+ aggregator 索引 + `_audit.md`。

每份产物由对应**子代理**独立完成（默认并行）；**主 agent 全程仅调度，不直接产出任何内容文件**。aggregator 仅列概述与链接，**不重复接口正文**。

| 场景 | aggregator 产物 |
|---|---|
| 单接口（粒度 C） | 仅 `endpoint-{TYPE}-{slug}.md` |
| 默认（粒度 B 全量）/ A 小型项目 | `features.md` 或 `overview.md` |
| 限定范围（如"支付下单"） | `features-{slug}.md` |
| A 大型项目 | 每子功能一份 `features-{slug}.md` + 顶层 `overview.md` |

默认覆盖同名文件便于 git diff。

## 增量重跑 / 中断恢复

- **跳过已完成项**：planner / interface-catalog / endpoint-analyst 检测到对应产物已存在即跳过
- **重做单个接口**：删除对应 `endpoint-X.md` 后重新执行
- **完全重做**：删除整个 `_results/`
- **调整拆分**：直接编辑 `_plan.md` 后让 skill 继续执行

## Runtime 兼容性

- **Claude Code**：内置 Task tool 直接派发——**无需** `.opencode/agents/`
- **opencode**：把 skill 仓的整个 `.opencode/`（含 `skills/biz-flow-recon/` 与 `agents/`）复制或软链到 `<被分析项目>/.opencode/`（**项目级，不入全局**）。子代理 frontmatter 加 `model:` 可指定不同 provider/model，混用便宜模型并行扫描 + Opus 深度归纳

## 建议的 gitignore 配置

```
_results/
.opencode/skills/biz-flow-recon/knowledge/        # 含敏感信息时按需忽略
```
