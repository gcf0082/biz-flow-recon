# 工作目录约定

biz-flow-recon 将"通用框架"与"项目专属信息"分离：

- **skill 仓本身**：通用方法论与默认模板，置于 `templates/`。
- **被分析项目内**：约定一个 `biz-flow-recon/` 子目录，存放该项目的知识库、模板覆盖与产物。skill 自动从此处加载。

## 目录结构

在被分析项目根目录下创建：

```
<被分析项目>/
└── biz-flow-recon/
    ├── knowledge/                 # 可选：项目专属知识库
    │   ├── glossary.md            # 术语、模块名、角色名
    │   ├── conventions.md         # 团队约定（鉴权方式、加密库、日志规范、命名）
    │   └── modules/               # 按子模块的预先说明
    │       └── order-service.md
    ├── templates/                 # 可选：覆盖默认模板
    │   ├── default.md             # 单接口产物 endpoint-*.md 的格式
    │   ├── overview.md            # aggregator 索引格式
    │   └── _plan.md               # 子任务计划
    └── output/                    # skill 自动写入产物
        ├── endpoint-*.md          # 每接口一份（subagent 写入）
        ├── features.md / features-{slug}.md   # aggregator 索引（主 agent 写入）
        └── overview.md            # 整项目顶层索引（主 agent 写入）
```

`biz-flow-recon/` 这一目录名为**固定约定**，skill 在当前工作目录下查找。

## 知识库（knowledge/）

skill 在分析开始前会**完整读取本目录下所有 .md 文件**作为先验。建议存放：

- **术语表**（`glossary.md`）：项目特有名词。例如 `BizContext = 会话上下文，跨 RPC 调用透传`、`AcmeCrypto = 内部加密 SDK，封装 AES-GCM`。
- **团队约定**（`conventions.md`）：统一鉴权方式、密钥获取方式、敏感字段加密所用库、日志位置、配置文件命名等。**亦可在此声明：内部服务代码位置、递归追溯深度**——详见下文"递归追溯配置"。
- **模块说明**（`modules/*.md`）：每个子模块一份文件，说明其功能与协作对象。

内容**应保持精炼**——此为 Claude 的先验提示，而非用户文档；冗余信息会反向降低准确度。

### 递归追溯配置（写入 `conventions.md`）

skill 在遇到调用脚本 / 内部服务 / SQL / 反射时会尝试**在工作区内定位目标并读取**，将下游行为一并纳入同一描述。两项配置可调整该行为：

**内部服务定位**（启用跨仓追溯）：

```markdown
## 内部服务定位
- charge-svc → 代码在 ../services/charge-svc/
- idp-svc    → 代码在 ../services/idp-svc/
- billing    → 黑盒（独立外部团队维护，不予追溯）
```

skill 在调用 `http://charge-svc/...` 时即按指明路径定位接收端代码。标注为黑盒的服务按外部处理，不递归。

**递归深度**（默认 2 层，按需调整）：

```markdown
## 递归追溯深度
3
```

填写一个整数。深度增大会使产物增长，按需配置。

未能定位的目标 skill 将**在产物末尾的"未能追溯的引用"节中显式列出**，便于逐项核查（属真正外部 / 未拉取仓 / 路径配置错误）。

## 模板覆盖（templates/）

若默认模板的格式不符合团队偏好，将 skill 包内 `templates/` 下对应文件复制至项目 `biz-flow-recon/templates/` 后修改即可。skill 检测到项目内同名文件即优先使用，否则回退至 skill 默认。

支持的文件名：`default.md`、`overview.md`、`_plan.md`。粒度 C（单接口）同样走 `default.md`（仅截取单个接口块）。

## 输出（output/）

skill 产物结构为**每接口一份独立文件 + 一个或多个 aggregator 索引**：

```
biz-flow-recon/output/
├── endpoint-GET-api-files-name.md         每接口一份（必产出，subagent 写入）
├── endpoint-POST-api-jobs-run-report.md
├── endpoint-GET-api-users-me.md
├── ...
├── features.md                            索引：核心总结 + 链接至各 endpoint-*.md（小型项目）
└── overview.md                            索引（粒度 A 或大型项目顶层）
```

每份 endpoint 文件由独立 subagent 完成（默认并行派发，彼此独立）。aggregator 索引由主 agent 在全部 subagent 完成后汇编——仅列概述与链接，**不重复接口正文**。

| 场景 | 产物 |
|---|---|
| 单接口（粒度 C） | 一份 `endpoint-{METHOD}-{slug}.md`，无 aggregator |
| 默认（粒度 B 全量）/ 整项目小型项目 | 多份 `endpoint-*.md` + `features.md` 或 `overview.md` 索引 |
| 限定范围（如"支付下单"） | 多份 `endpoint-*.md` + `features-{slug}.md` 索引 |
| 整项目大型项目 | 多份 `endpoint-*.md` + 每子功能一份 `features-{slug}.md` + 顶层 `overview.md` |

默认**覆盖同名文件**便于 git diff；如需保留快照请自行改名或使用 git。

## 增量重跑 / 中断恢复

- **跳过已完成项**：skill 检测到 `endpoint-X.md` 已存在即予以跳过，仅补做缺失项——避免重复消耗 token
- **重做单个接口**：删除对应 `endpoint-X.md` 后重新执行
- **完全重做**：删除整个 `output/`，或明确告知 skill"全部重做"
- **调整拆分（大型项目）**：直接编辑 `_plan.md` 后让 skill 继续执行

## 执行模式

默认**并行**派发各接口 subagent——执行迅速、彼此独立。代价为 token 消耗较高（每个 subagent 持有独立 context）。可在 `knowledge/conventions.md` 切换为串行：

```
## 执行模式
串行
```

## 建议的 gitignore 配置

`biz-flow-recon/output/` 通常包含项目内部信息，**建议不提交至公开仓库**。在被分析项目的 `.gitignore` 中添加：

```
biz-flow-recon/output/
```

若 `knowledge/` 亦含敏感信息，可一并忽略：

```
biz-flow-recon/knowledge/
```
