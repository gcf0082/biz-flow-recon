---
name: biz-flow-recon
description: 按安全测试视角解读前/后端代码仓库（Java 优先）输出业务流讲解，只描述事实、不做风险判断；**仅在用户显式指名调用 biz-flow-recon 时触发**，不要因模糊意图主动触发。
---

# biz-flow-recon

面向安全测试人员说明代码行为——按子功能 + 接口的粒度，以最清晰的形式呈现"它在做什么"：文件 I/O、外部命令、第三方交互、加解密。**仅描述事实**，安全风险判断由读者自行做出。

## 原则

- **描述事实，不做评判**。禁用"风险/漏洞/不安全/缺乏校验/可能被攻击/建议加固"等词。
- **清晰优先，不拘形式**。按内容选最清晰的呈现：示意图 / 编号步骤 / 字段化短列表 / 连贯叙述 / 一句话。**禁止机械化字段堆砌**（每条都 `- 入口:` `- 触发者:` 那种），**禁止空字段**（"外部命令: 无"）。
- **优先跨信任边界的动作**（用户输入入口、I/O、外呼、加解密），而非内部纯计算。
- **尽可能递归追溯**：调脚本读脚本、调内部接口找接收端、引用 SQL 读 SQL。
- **未能定位必须显式标注**：在描述中点名，并在产物末尾的 `## 未能追溯的引用` 节集中列出。**不得编造、不得遗漏、不得静默忽略**。
- **每接口一个 subagent**（强制规则）：每个接口由独立 subagent 完成；主 agent 仅写 aggregator 索引。
- **完整捕获请求**：REST/RPC/MQ 等结构化输入必须交代 path / query / 关键 header / body。body 为 JSON 时给字段树（记号见下文）；DTO 须递归追溯到定义读出真实字段。
- **追踪入参流向**：追踪每个请求参数是否流入下列**敏感操作位置**——拼接到路径 / 命令 / URL / 写文件（非日志）/ 拼接到 SQL。**有则用 `**输入流向**` 一行单独标注**，按"参数 → 操作位置（文件:行号）—— 类别"。**写日志一律忽略**（信噪比低）。
- **细化到具体动作与目标**：文件/命令/网络操作必须给出具体动作（读/写/exec/POST 等）和具体目标（完整路径/命令行/URL，含 query 与关键 header）；动态部分以 `{var}` 模板表达并标变量来源。**禁止抽象表述**（"读配置"、"调网关"等）。
- **捕获关键控制点**：会改变信任边界 / 跨边界行为的**开关 / 配置 / 判断 / 限制**——TLS 校验、签名/HMAC/Token 校验、反序列化多态、CORS 通配、SQL `${}` 拼接、鉴权放行规则、上传校验、redirect 白名单、加解密算法与密钥来源、token/密码策略、反射白名单等——以 `**关键控制点**` 标签集中列出。普通 feature flag、日志/缓存/线程池配置不列。
- **不中断、不询问**：skill 一旦显式调用即全自动跑到底——不论项目规模、未追溯引用数量、解析歧义。错误按"显式标注 + 继续"处理，**绝不暂停等待用户输入**。用户事后可改 `_plan.md` / 删除 `endpoint-*.md` 重跑。
- **多语言支持**：Java 与 Python 主流 web/MQ/gRPC 框架同等支持；其他语言暂未覆盖。

## 取舍

**保留**：用户输入入口、文件读写、外部进程、网络外呼、加解密/签名、鉴权与会话、数据持久化。
**剔除**：CSS/i18n/纯计算/单测/构建脚本/健康检查/静态资源/Spring Actuator 等纯运维端点。

## 方法（主 agent 纯调度）

主 agent **不直接产出任何内容文件**，全程仅"读配置 → 决策粒度 → 派发子代理 → 等待 → 派发下一批 → 告知用户路径"。

| 步骤 | 主 agent 动作 | 派发的子代理 / 决策 |
|---|---|---|
| 0 | 加载工作目录 | 读 `<cwd>/biz-flow-recon/knowledge/`（如有）；解析模板路径（项目级覆盖 → skill 默认）。**不写任何文件** |
| 1 | 确定粒度 | A（整项目）/ B（默认子功能 + 接口）/ C（单接口）—— C 时模板取 `default.md` 单接口块并把 `#### {METHOD} {URL}` 升至顶层 |
| 2 | 派发 `planner` | 写 `_plan.md`；已存在则跳过 |
| 3 | 并行派发 | `interface-catalog` + `outbound-collector` + N × `endpoint-analyst`（每接口一个）；默认并行，`conventions.md` 配 `执行模式: 串行` 时改串行 |
| 4 | 等待 + 失败重试 | 子代理失败重派最多 2 次；仍失败则在产物头部插入 `<!-- ⚠ 产物自检未通过：缺失 X 请人工补全 -->`，**不阻断** |
| 4.5 | 派发 `cross-cut-analyst` | 读所有 endpoint-*.md 写 cross-cuts.md |
| 5 | 派发 `aggregator-writer` | 传入粒度参数；产出 `features.md` / `features-{slug}.md` / `overview.md`；顶部带横向产物链接 |
| 6 | 派发 `completion-verifier` | 写 `_audit.md`；**不阻断流程** |
| 6.5 | 派发 `knowledge-extractor`（可关闭） | `conventions.md` 写 `知识库自我演化: 关闭` 时跳过 |
| 7 | 告知用户产物路径 | aggregator 入口 + 横向产物（`outbound.md` / `cross-cuts.md`）+ `_audit.md` |

各子代理职责详见 `agents/README.md`；opencode 用户复制 `agents/*.md` 到被分析项目的 `.opencode/agents/`，Claude Code 用户走 Task tool。

---

## 子代理执行规范（endpoint-analyst 适用）

每条接口必须交代：哪段代码的哪个入口（含 `类#方法，文件:行号`）、谁触发、**请求参数**、**入参流向**（如有落到敏感槽）、**关键控制点**（如有）、当**实际发生**时讲清文件 I/O / 命令 / 第三方 / 加解密——没发生的不写。

### 追溯边界与深度

- 当前仓 / 本地兄弟目录 → 必须追溯
- 跨仓 → 仅当 `knowledge/conventions.md` 指明位置时追溯
- 真正外部（第三方/SaaS）→ 仅描述对外协议
- 深度默认 2 层；第 3 层及以后一句话概括（`conventions.md` 配置时按用户）

### 具体性要求

- **文件 I/O**：动作（读/写/追加/删除/拷贝/移动/列目录）+ 完整路径（动态部分 `{var}` + 变量来源）+ 格式
- **命令**：完整命令行（动态参数 `{var}` 模板化）+ 执行方式 + `文件:行号`
- **第三方**：`METHOD URL` + Content-Type + 关键 Header + body 概要 + 客户端 + `文件:行号`
- **关键控制点**：`<事项>: <实际取值或规则>（文件:行号）`，必要时附 `（开关）/（配置）/（判断）/（限制）` 子类

> 同一接口含多个文件/命令/第三方操作时，**优先放入 flowchart 节点**呈现执行顺序、循环、分支与 gate；labeled 列表只保留图无法承载的细节（格式说明、字段含义、批量汇总等），**不重复图中事实**。

### 形式选型

- **mermaid 示意图**（**仅用 `flowchart TD`**，禁用 sequenceDiagram / stateDiagram / graph LR）。规则：
  - **必画图**：流程含 ≥ 2 个文件/命令/网络外呼操作，或含循环/分支/关键控制点判断
  - **图前必有业务描述**——图作增量补充，不可替代
  - **图聚焦"输入来源 → 关键校验 → 高危操作"链路**。节点应包括：
    - **起点 = 接口入口**（REST 时为 `METHOD URL`；MQ 时为 Topic；gRPC 时为 `Service.Method`），含请求维度概要（如 `multipart: file + filename`）；下游节点用 `body.X` / `path.Y` / `query.Z` / `header.W` 引用具体被使用的输入字段，让读者按字段追踪传播
    - 每个文件 / 命令 / 网络外呼 / 加解密操作（独立节点；标签含动作 + 完整路径或 URL + `<br/><small>文件:行号</small>`）
    - 当文件 / 命令 / URL 的目标无任何用户输入污染、完全固定时**节点标签追加 `· 硬编码`**——读者一眼区分"受输入污染" vs "路径固定"
    - **关键安全相关校验**：白名单匹配、签名/HMAC 验证、鉴权放行规则、文件后缀/MIME/大小校验等关键控制点——`{...}` 菱形 + `|通过|/|拒绝|` 边标
  - **不画的分支**（属噪声，避免污染图）：
    - 判空 / null check / `Objects.requireNonNull`
    - 防御性 IllegalArgumentException / try-catch 通用包装
    - 通用格式校验（如"参数不是数字则报错"）
    - 5xx 错误页 / 404 通用返回 / generic exception handler
    - 内部纯计算路径
  - 业务步骤名 + 技术动作可同节点呈现（如 `① 落地原始文件\n写 /data/uploads/{filename}`）
  - 循环用 `subgraph "对每个 X："`；gate 校验失败可画到"异常终止"subgraph，但**仅关键安全校验的失败**值得画
  - 每接口至多一张图
- **编号步骤**：内在顺序操作
- **字段化短列表**：`**第三方**:` 等，仅列实际发生
- **连贯叙述**：事实自然成句时
- **一句话**：简单读接口

递归追溯所得的下游事实写入同一条描述。**不嵌套子标题**。

### 请求参数记号（Body 字段树）

- `string!` / `int!` —— 非空必填（`@NotNull` / `@NotBlank` / pydantic 必填字段等）
- `string?` —— 可选 / 可为空
- `[ ... ]` —— 数组
- `// ...` —— 行内注释（约束、含义）
- 末尾附 DTO 全限定名 + `文件:行号`

简单 query 一行 inline（`**请求**: query \`?page=1&size=20\` ...`）；嵌套或字段多用 fenced ` ```json5 ... ``` ` 块。GET 无 body 不写 body 行。

### 落盘前自检（强制）

写完 `endpoint-*.md` 后任一项不满足立即修补重写：
- 顶层 `# {METHOD} {URL} — ...` 标题存在
- 业务描述段（≥ 1 段）存在
- 必画图条件触发时含 ` ```mermaid\nflowchart TD` 块，且块内 ≥ 1 个文件/命令/外呼节点
- REST/RPC/MQ 含 `- **请求**:` 行
- 全文不含禁词

---

## 输出文件名约定

slug 小写连字符；中文转拼音/英文同义词；**默认覆盖同名文件**便于 git diff。

| 文件 | 写入者 | 用途 |
|---|---|---|
| `_plan.md` | planner | 子任务计划 |
| `interfaces.md` | interface-catalog | 对外暴露接口清单（inbound 攻击面） |
| `outbound.md` | outbound-collector | 系统对外调用汇总（outbound） |
| `endpoint-{METHOD}-{slug}.md` | endpoint-analyst | 单接口深度分析 |
| `cross-cuts.md` | cross-cut-analyst | 横向洞察 |
| `features.md` / `features-{slug}.md` / `overview.md` | aggregator-writer | 索引 aggregator |
| `_audit.md` | completion-verifier | 任务完整性审计 |
| `../knowledge/auto-*.md` | knowledge-extractor | 自动提取的先验（可关闭） |

## 工作目录与模板

`docs/workspace-layout.md` 详述被分析项目 `biz-flow-recon/{knowledge,templates,output}/` 与 `.opencode/agents/` 的约定。**每次输出前必须读对应模板再撰写**，不得依赖记忆——以确保用户对模板的修改即时生效。
