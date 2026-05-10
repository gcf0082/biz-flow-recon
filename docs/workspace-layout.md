# 工作目录约定

biz-flow-recon 将"通用框架"与"项目专属信息"分离：

- **skill 仓本身**：通用方法论 + 默认模板 + 子代理定义模板（`agents/`）
- **被分析项目内**：约定一个 `biz-flow-recon/` 子目录存放该项目的知识库、模板覆盖与产物；opencode runtime 还需要 `.opencode/agents/` 目录

## 目录结构

被分析项目根目录下：

```
<被分析项目>/
├── biz-flow-recon/
│   ├── knowledge/                # 可选：项目专属知识库
│   │   ├── glossary.md           # 用户手填：术语
│   │   ├── conventions.md        # 用户手填：团队约定 + 配置开关
│   │   ├── modules/*.md          # 用户手填：子模块说明
│   │   └── auto-*.md             # 自动提取（knowledge-extractor 写入）
│   ├── templates/                # 可选：覆盖 skill 默认模板
│   │   ├── default.md
│   │   ├── overview.md
│   │   └── _plan.md
│   └── output/                   # skill 自动写入产物
│       ├── _plan.md / interfaces.md / outbound.md
│       ├── endpoint-*.md
│       ├── cross-cuts.md
│       ├── features*.md / overview.md
│       └── _audit.md
└── .opencode/agents/             # 可选（仅 opencode runtime）
    └── *.md                      # 8 份子代理定义，从 skill 包 agents/ 复制
```

`biz-flow-recon/` 与 `.opencode/agents/` 目录名为**固定约定**。

## 知识库（knowledge/）

skill 在分析开始前**完整读取本目录所有 .md** 作为先验。建议存放：

- **`glossary.md`**：项目特有术语
- **`conventions.md`**：团队约定（鉴权方式、加密库、日志规范）+ skill 行为开关（见下）
- **`modules/*.md`**：每个子模块一份说明
- **`auto-*.md`**：`knowledge-extractor` 自动写入；与上述用户文件**并存且不覆盖**

内容**应保持精炼**——这是给 Claude 的先验提示，冗余反而降低准确度。

## conventions.md 配置开关

```markdown
## 内部服务定位
- charge-svc → 代码在 ../services/charge-svc/
- billing    → 黑盒（外部团队维护）

## 递归追溯深度
3

## 执行模式
并行

## 知识库自我演化
关闭
```

skill 见到调用 `http://charge-svc/...` 即按指定路径定位接收端代码；标注黑盒的按外部处理。深度默认 2，可调。执行模式默认并行，可改串行（更稳但慢）。"知识库自我演化: 关闭"则跳过步骤 6.5。

## 模板覆盖（templates/）

将 skill 包 `templates/` 下对应文件复制到项目 `biz-flow-recon/templates/` 后修改。skill 检测到项目内同名文件即优先使用。

支持的文件名：`default.md`、`overview.md`、`_plan.md`。粒度 C（单接口）也走 `default.md`（仅截取单接口块）。

## 输出（output/）

产物结构 = 每接口一份独立文件 + 三个横向产物（`interfaces.md` / `outbound.md` / `cross-cuts.md`）+ aggregator 索引 + `_audit.md`。

每份产物由对应**子代理**独立完成（默认并行）；**主 agent 全程仅调度，不直接产出任何内容文件**。aggregator 仅列概述与链接，**不重复接口正文**。

| 场景 | aggregator 产物 |
|---|---|
| 单接口（粒度 C） | 仅 `endpoint-{METHOD}-{slug}.md` |
| 默认（粒度 B 全量）/ A 小型项目 | `features.md` 或 `overview.md` |
| 限定范围（如"支付下单"） | `features-{slug}.md` |
| A 大型项目 | 每子功能一份 `features-{slug}.md` + 顶层 `overview.md` |

默认覆盖同名文件便于 git diff。

## 增量重跑 / 中断恢复

- **跳过已完成项**：检测到 `endpoint-X.md` 等已存在即跳过
- **重做单个接口**：删除对应 `endpoint-X.md` 后重新执行
- **完全重做**：删除整个 `output/`
- **调整拆分**：直接编辑 `_plan.md` 后让 skill 继续执行

## Runtime 兼容性

- **Claude Code**：内置 Task tool 直接派发——**无需** `.opencode/agents/`
- **opencode**：复制 `<skill-pkg>/agents/*.md` 到 `<被分析项目>/.opencode/agents/`（**项目级，不入全局**）。子代理 frontmatter 加 `model:` 可指定不同 provider/model，混用便宜模型并行扫描 + Opus 深度归纳

## 建议的 gitignore 配置

```
biz-flow-recon/output/
biz-flow-recon/knowledge/        # 含敏感信息时按需忽略
```
