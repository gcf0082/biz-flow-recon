# 工作目录约定

biz-flow-recon 把"通用框架"和"项目专属信息"分开。

- **skill 仓本身**：通用方法论 + 默认模板，放在 `templates/`。
- **被分析项目里**：约定一个 `biz-flow-recon/` 子目录，存放你这个项目的知识库、模板覆盖、产物。skill 会自动到这里去找。

## 目录结构

在你想分析的项目根目录下建：

```
<被分析项目>/
└── biz-flow-recon/
    ├── knowledge/                 # 可选：项目专属知识库
    │   ├── glossary.md            # 术语、模块名、角色名
    │   ├── conventions.md         # 团队约定（鉴权方式、加密库、日志规范、命名）
    │   └── modules/               # 按子模块写的预先说明
    │       └── order-service.md
    ├── templates/                 # 可选：覆盖默认模板
    │   ├── default.md             # 单接口产物 endpoint-*.md 的格式
    │   ├── overview.md            # aggregator 索引格式
    │   └── _plan.md               # 子任务计划
    └── output/                    # skill 自动写产物到这里
        ├── endpoint-*.md          # 每接口一份（subagent 写）
        ├── features.md / features-{slug}.md   # aggregator 索引（主 agent 写）
        └── overview.md            # 整项目顶层索引（主 agent 写）
```

`biz-flow-recon/` 这个目录名是**固定**的，skill 会在当前工作目录下查找。

## 知识库（knowledge/）

skill 在分析前会**先把这个目录里所有 .md 读一遍**作为先验。建议放：

- **术语表**（`glossary.md`）：项目里出现的特定名词。例如 `BizContext = 会话上下文，跨 RPC 调用透传`、`AcmeCrypto = 内部加密 SDK，封装了 AES-GCM`。
- **团队约定**（`conventions.md`）：鉴权统一走什么、密钥怎么拿、敏感字段加密用什么库、日志写哪、配置文件命名。**还可以在这里告诉 skill：内部服务的代码在哪、下钻深度调多少**——见下面"下钻配置"。
- **模块说明**（`modules/*.md`）：每个子模块一个文件，写它在做什么、与谁交互。

写得**精炼**就好——这是给 Claude 提示词，不是给人写文档。多写不是越好。

### 下钻配置（写在 `conventions.md`）

skill 看到调脚本/内部服务/SQL/反射时会尝试**在工作区里找目标读它**，把下游做了什么也讲进同一段。两条配置可以影响这个行为：

**内部服务定位**（让跨仓下钻变可能）：

```markdown
## 内部服务定位
- charge-svc → 代码在 ../services/charge-svc/
- idp-svc    → 代码在 ../services/idp-svc/
- billing    → 黑盒（独立外部团队维护，不要尝试找）
```

skill 看到调用 `http://charge-svc/...` 就会去 `../services/charge-svc/` 下找接收方代码。标注为黑盒的就当外部，不递归。

**递归深度**（默认 2 层，按需加深）：

```markdown
## 下钻深度
3
```

写一个数字就行。深度大了 brief 会变长，按需。

走不通的目标 skill 会**显式列在产物末尾的"未跟到的引用"节**，方便你逐个排查（真外部？仓没拉？路径写错？）。

## 模板覆盖（templates/）

如果默认模板的格式不合你团队的口味，把 skill 包里 `templates/` 下的对应文件复制一份到项目的 `biz-flow-recon/templates/` 里改即可。skill 看到项目里有同名文件就用项目版本，没有就用 skill 默认版本。

支持的文件名：`default.md`、`overview.md`、`_plan.md`。粒度 C（单接口）也走 `default.md`（只取一个接口块）。

## 输出（output/）

skill 的产物总是**每个接口一份独立文件 + 一个或多个 aggregator 索引**：

```
biz-flow-recon/output/
├── endpoint-GET-api-files-name.md         每接口一份（必产出，subagent 写）
├── endpoint-POST-api-jobs-run-report.md
├── endpoint-GET-api-users-me.md
├── ...
├── features.md                            索引：核心总结 + 链接到各 endpoint-*.md（小项目）
└── overview.md                            索引（粒度 A 或大项目顶层）
```

每个 endpoint 文件由独立 subagent 完成（默认并行派发，互不影响）。aggregator 索引由主 agent 在所有 subagent 完成后汇编——只列概述和链接，**不重复接口正文**。

| 场景 | 产物 |
|---|---|
| 单接口（粒度 C） | 一份 `endpoint-{METHOD}-{slug}.md`，无 aggregator |
| 默认（粒度 B 全量）/ 整项目小项目 | 多份 `endpoint-*.md` + `features.md` 或 `overview.md` 索引 |
| 限定范围（如"支付下单"） | 多份 `endpoint-*.md` + `features-{slug}.md` 索引 |
| 整项目大项目 | 多份 `endpoint-*.md` + 每子功能一份 `features-{slug}.md` + 顶层 `overview.md` |

默认**覆盖同名文件**便于 git diff；要留快照自己改名或用 git。

## 增量重跑 / 中断恢复

- **跳过已做过的**：skill 看到 `endpoint-X.md` 已存在就直接跳过，只补做缺的——不浪费 token
- **重做单个**：删掉对应 `endpoint-X.md` 重跑
- **全部重做**：删整个 `output/`，或明确告诉 skill"全部重做"
- **改拆分（大项目）**：直接编辑 `_plan.md`，再让 skill 接着跑

## 执行模式

默认**并行**派发各接口 subagent——速度快、互不影响。token 消耗也大（每个 subagent 独立 context）。可在 `knowledge/conventions.md` 改为串行：

```
## 执行模式
串行
```

## 建议 gitignore

`biz-flow-recon/output/` 通常包含项目内部信息，**建议不要提交到公开仓库**。在被分析项目的 `.gitignore` 加：

```
biz-flow-recon/output/
```

如果 knowledge 也含敏感信息，按需也忽略：

```
biz-flow-recon/knowledge/
```
