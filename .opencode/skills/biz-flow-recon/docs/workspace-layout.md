# 工作目录约定

biz-flow-recon 将 skill 配置（含知识库）与项目级**模板覆盖 / 产物**分离：

- **skill 子树**（`.opencode/skills/biz-flow-recon/`）：SKILL.md / templates/ / docs/ + **knowledge/**（项目专属先验，住此处）
- **项目根 `biz-flow-recon/`**：仅留 `templates/`（项目级覆盖，可选）与 `output/`（分析产物）

## 目录结构

被分析项目根目录下：

```
<被分析项目>/
├── .opencode/                    # opencode runtime 加载入口
│   ├── skills/biz-flow-recon/
│   │   ├── SKILL.md              # 主调度任务说明书
│   │   ├── templates/            # 默认输出模板
│   │   ├── docs/                 # 工作目录约定文档
│   │   └── knowledge/            # 项目专属先验（主 agent 读取后摘要拼入派发 prompt）
│   │       ├── briefing.md       # 用户手填：项目高层说明（结构、外部接口风格、共用机制）
│   │       ├── glossary.md       # 用户手填：术语
│   │       ├── conventions.md    # 用户手填：团队约定 + 配置开关
│   │       └── modules/*.md      # 用户手填：子模块说明
│   └── agents/                   # 5 份子代理 .md
└── biz-flow-recon/               # 项目级工作目录
    ├── templates/                # 可选：覆盖 skill 默认模板
    │   ├── default.md
    │   ├── overview.md
    │   └── _plan.md
    └── output/                   # skill 自动写入产物
        ├── _plan.md / interfaces.md
        ├── endpoint-*.md
        ├── features*.md / overview.md
        └── _audit.md
```

`.opencode/skills/biz-flow-recon/{SKILL.md,knowledge/,templates/,docs/}` 与 `.opencode/agents/`、`biz-flow-recon/{templates,output}/` 目录名为**固定约定**。

## 知识库（knowledge/）

放项目特有说明，给项目结构、术语、约定、内部服务定位等关键线索。**主 agent 在调度前读全量 .md，抽取要点形成"项目先验摘要"**，并把它作为头部块拼入派发给每个子代理的 prompt——子代理不直接读本目录。建议存放：

- **`briefing.md`**：**项目高层说明**——技术栈与版本、模块布局总览、外部接口风格约定（路径命名、版本前缀、错误码规范）、跨模块共用机制（统一鉴权 / trace / 异常）、特殊查找线索。
- **`glossary.md`**：项目特有术语
- **`conventions.md`**：团队约定（鉴权方式、加密库、日志规范）+ skill 行为开关（见下）
- **`modules/*.md`**：每个子模块一份说明

内容**应保持精炼**——冗余反而降低准确度。

## conventions.md 配置开关

```markdown
## 内部服务定位
- charge-svc → 代码在 ../services/charge-svc/
- billing    → 黑盒（外部团队维护）

## 递归追溯深度
3

## 执行模式
并行
```

skill 见到调用 `http://charge-svc/...` 即按指定路径定位接收端代码；标注黑盒的按外部处理。深度默认 2，可调。执行模式默认并行，可改串行（更稳但慢）。

## 模板覆盖（templates/）

将 skill 包 `.opencode/skills/biz-flow-recon/templates/` 下对应文件复制到项目 `biz-flow-recon/templates/` 后修改。skill 检测到项目内同名文件即优先使用。

支持的文件名：`default.md`、`overview.md`、`_plan.md`。粒度 C（单接口）也走 `default.md`（仅截取单接口块）。

## 输出（output/）

产物结构 = 每接口一份独立文件 + 横向产物（`interfaces.md`）+ aggregator 索引 + `_audit.md`。

每份产物由对应**子代理**独立完成（默认并行）；**主 agent 全程仅调度，不直接产出任何内容文件**。aggregator 仅列概述与链接，**不重复接口正文**。

| 场景 | aggregator 产物 |
|---|---|
| 单接口（粒度 C） | 仅 `endpoint-{METHOD}-{slug}.md` |
| 默认（粒度 B 全量）/ A 小型项目 | `features.md` 或 `overview.md` |
| 限定范围（如"支付下单"） | `features-{slug}.md` |
| A 大型项目 | 每子功能一份 `features-{slug}.md` + 顶层 `overview.md` |

默认覆盖同名文件便于 git diff。

## 增量重跑 / 中断恢复

- **跳过已完成项**：planner / interface-catalog / endpoint-analyst 检测到对应产物已存在即跳过
- **始终覆盖**：aggregator-writer / completion-verifier 每次都覆盖最新（基于当前 output/ 全貌重写）
- **重做单个接口**：删除对应 `endpoint-X.md` 后重新执行
- **完全重做**：删除整个 `output/`
- **调整拆分**：直接编辑 `_plan.md` 后让 skill 继续执行

## Runtime 兼容性

- **Claude Code**：内置 Task tool 直接派发——**无需** `.opencode/agents/`
- **opencode**：把 skill 仓的整个 `.opencode/`（含 `skills/biz-flow-recon/` 与 `agents/`）复制或软链到 `<被分析项目>/.opencode/`（**项目级，不入全局**）。子代理 frontmatter 加 `model:` 可指定不同 provider/model，混用便宜模型并行扫描 + Opus 深度归纳

## 建议的 gitignore 配置

```
biz-flow-recon/output/
.opencode/skills/biz-flow-recon/knowledge/        # 含敏感信息时按需忽略
```
