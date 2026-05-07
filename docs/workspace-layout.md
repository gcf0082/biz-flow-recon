# 工作目录约定

biz-flow-recon 把"通用框架"和"项目专属信息"分开。

- **skill 仓本身**（gcf0082/biz-flow-recon）：通用方法论 + 默认模板，放在 `templates/`。
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
    │   ├── default.md             # 同 skill 里的文件名（粒度 B）
    │   ├── overview.md            # 同（粒度 A）
    │   └── endpoint.md            # 同（粒度 C）
    └── output/                    # skill 自动写产物到这里
        └── *.md
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

如果默认模板的格式不合你团队的口味，复制 skill 仓里的对应文件改：

```bash
mkdir -p biz-flow-recon/templates
cp ~/.claude/skills/biz-flow-recon/templates/default.md biz-flow-recon/templates/
# 改 biz-flow-recon/templates/default.md
```

skill 看到项目里有同名文件就用项目版本，没有就用 skill 默认版本。

## 输出（output/）

skill 按下面的命名规则写产物到 `output/`：

| 粒度 | 文件名 |
|---|---|
| 整项目 | `overview.md` |
| 子功能（默认） | `features.md`，或在限定范围时 `features-{slug}.md` |
| 单接口 | `endpoint-{METHOD}-{path-slug}.md`（如 `endpoint-POST-api-login.md`） |

默认**覆盖同名文件**——便于 git diff。要留快照请自己改名或用 git。

## 大项目自动拆分

项目大到一次分析装不下时（几十个 Controller、多 maven 模块、6+ 子功能等），skill 会**自动**进入"大项目模式"：

1. 先盘子功能，写 `output/_plan.md` 列出子任务（每个含名称、slug、scope 目录、目标文件名）
2. 简短告诉你拆分方案
3. 逐个子任务执行，每个产出一份 `output/features-{slug}.md`
4. 全部完成后写 `output/overview.md`：核心功能总结 + 子功能索引（链接到各 features 文件）+ 未跟到的引用汇总

最终目录大概是：

```
biz-flow-recon/output/
├── _plan.md              拆分方案（可改）
├── features-auth.md
├── features-order.md
├── features-pay.md
├── ...
└── overview.md           入口文件（含索引）
```

### 你能怎么干预

- **改拆分**：在 plan 阶段让 skill 等你确认；或者直接改 `_plan.md` 再让它接着跑
- **打开并行**：在 `knowledge/conventions.md` 里加：

  ```
  ## 执行模式
  并行
  ```

  这时 skill 用 Task 工具并行派发 subagent 同时分析多个子功能，更快但消耗 token 更多

- **重做某条**：删掉对应的 `features-X.md` 重跑，skill 默认跳过已存在的、只补做缺的
- **全部重做**：删整个 `output/`，或明确告诉 skill"全部重做"

## 建议 gitignore

`biz-flow-recon/output/` 通常包含项目内部信息，**建议不要提交到公开仓库**。在被分析项目的 `.gitignore` 加：

```
biz-flow-recon/output/
```

如果 knowledge 也含敏感信息，按需也忽略：

```
biz-flow-recon/knowledge/
```
