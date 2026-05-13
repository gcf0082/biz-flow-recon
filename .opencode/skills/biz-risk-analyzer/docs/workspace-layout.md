# 工作目录约定

biz-risk-analyzer 将 skill 配置（含知识库）与产物分离：

- **skill 子树**（`.opencode/skills/biz-risk-analyzer/`）：SKILL.md / templates/ / docs/ + **knowledge/**（项目专属先验）
- **项目根 `biz-risk-analyzer/`**：仅留 `templates/`（项目级覆盖，可选）
- **项目根 `_risk-results/`**：风险分析产物（与 `_results/` 并列）
- **事实产物 `_results/`**：只读消费，不修改

## 目录结构

被分析项目根目录下：

```
<被分析项目>/
├── .opencode/
│   ├── skills/biz-risk-analyzer/
│   │   ├── SKILL.md              # 主调度任务说明书
│   │   ├── templates/            # 默认输出模板
│   │   │   ├── finding.md        # 单漏洞报告模板
│   │   │   ├── risk-summary.md   # 汇总索引模板
│   │   │   └── _risk-plan.md     # 扫描计划模板
│   │   ├── docs/                 # 工作目录约定文档
│   │   └── knowledge/            # 项目专属先验
│   │       ├── briefing.md       # 用户手填：项目安全相关说明
│   │       ├── glossary.md       # 用户手填：术语
│   │       ├── conventions.md    # 用户手填：团队约定 + 风险分析行为开关
│   │       └── modules/*.md      # 用户手填：子模块说明
│   └── agents/                   # 子代理 .md（含 risk-analyst / risk-aggregator）
├── biz-risk-analyzer/            # 项目级模板覆盖（可选）
│   └── templates/
│       ├── finding.md
│       ├── risk-summary.md
│       └── _risk-plan.md
├── _results/                     # 事实分析产物（只读）
│   ├── endpoint-*.md
│   ├── interfaces.md
│   ├── features*.md / overview.md
│   ├── _plan.md
│   └── _audit.md
└── _risk-results/                # 风险分析产物
    ├── _risk-plan.md             # 观测点扫描计划
    ├── finding-*.md              # 每个漏洞独立文件
    ├── _dismissed.md             # 不可利用观测点记录（无则不写）
    └── _risk-summary.md          # 汇总索引
```

## 知识库

主 agent 在调度前读取 `knowledge/` 目录全量 .md，形成"项目先验摘要"拼入派发 prompt。
若 `knowledge/` 目录为空（无 briefing.md / glossary.md / conventions.md / modules/），项目先验摘要为"项目先验摘要：无"。

`严重等级阈值` 开关写入 `conventions.md`。若 conventions.md 不存在，默认值为 `Low`。

## 模板覆盖

将 skill 包 `.opencode/skills/biz-risk-analyzer/templates/` 下对应文件复制到项目 `biz-risk-analyzer/templates/` 后修改。skill 检测到项目内同名文件即优先使用。

支持的文件名：`finding.md`、`risk-summary.md`、`_risk-plan.md`。

## 增量重跑 / 中断恢复

- **跳过已完成项**：risk-analyst 检测到对应 `finding-*.md` 已存在即跳过（增量重跑友好）
- **始终覆盖**：risk-aggregator 每次都覆盖（基于当前 `_risk-results/` 全貌重写）
- **重新分析单个接口**：删除对应 `finding-{category}-{endpoint-slug}-*.md` 后重新执行
- **完全重做**：删除整个 `_risk-results/`
- **调整分析优先级**：直接编辑 `_risk-plan.md` 后让 skill 继续执行

## 建议的 gitignore 配置

```
_results/
_risk-results/
.opencode/skills/biz-risk-analyzer/knowledge/
```