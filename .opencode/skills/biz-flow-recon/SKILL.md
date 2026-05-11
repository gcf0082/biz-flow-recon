---
name: biz-flow-recon
description: 按安全测试视角解读前/后端代码仓库，输出业务流讲解，只描述事实、不做风险判断；**仅在用户显式指名调用 biz-flow-recon 时触发**，不要因模糊意图主动触发。
---

# biz-flow-recon

面向安全测试人员说明代码行为。**主 agent 仅负责调度**——所有内容产出由 5 个子代理完成。

## 共享原则（全员适用）

- **描述事实，不做评判**。"代码做了/没做某项检查"属于事实陈述（**应当报告**，包括"未做"）；"这是否构成风险/漏洞 / 是否需要加固"属于评判（**仍禁止**）。禁用"风险/漏洞/不安全/可能被攻击/建议加固"等结论性词。
- **未能定位必须显式标注**：在产物里点名"未在工作区找到 X"，并加入末尾的 `## 未能追溯的引用` 节集中列出。**不得编造、不得遗漏、不得静默忽略**。
- **文件操作目标路径必报**：文件 I/O / 命令执行 / 网络外呼 / SQL 等节点必须写出**目标本身**——文件路径 / 完整命令行 / URL（HTTP method + scheme + host + path）/ 表名等，**禁止只写"写入文件 / 执行脚本 / 调用网关 / 上报监控 / 读配置"**等抽象表述。动态片段用 `{变量名}` 标注并指明来源（如 `{body.filename}` / `{spring.uploads.dir 配置}`）。变量回溯失败时把"已解析的最长片段 + 卡在哪一步"写进节点描述，并把完全无法解析的目标进 `## 未能追溯的引用` 节——**不得退回抽象动词**。
- **硬编码绝对路径不出工作区访问**：代码若引用绝对路径资源（`/opt/...` / `/etc/...` / `/data/...` / `C:\...` 等），**不要**尝试读取该绝对路径本身——无授权且源码仓里通常找不到。改用**工作区后缀匹配**寻找同名源文件用于内容追溯：把绝对路径按目录层级倒序生成后缀候选，在工作区内 glob 搜索，**取最长命中的后缀**作为内容追溯候选；并列最长则列全部并标注"存在多个候选"。无命中按"未能追溯"处理。**节点描述里的目标路径永远写代码硬编码原值**，后缀匹配仅服务于内容深读。
- **不中断、不询问**：skill 一旦显式调用即全自动跑到底——不论项目规模、未追溯引用数量、解析歧义。错误按"显式标注 + 继续"处理，**绝不暂停等待用户输入**。用户事后可改 `_plan.md` / 删除产物文件重跑。
- **每接口一个 subagent**：每个接口由独立 subagent 完成。
- **跳过 vs 覆盖**：planner / interface-catalog / endpoint-analyst 默认跳过已存在产物（增量重跑友好）；aggregator-writer / completion-verifier 始终覆盖（始终基于最新产物重写）。

## 取舍

**保留**：用户输入入口、文件读写、外部进程、网络外呼、加解密/签名、鉴权与会话、数据持久化。
**剔除**：CSS/i18n/纯计算/单测/构建脚本/健康检查/静态资源/Spring Actuator 等纯运维端点。

## 方法（主 agent 纯调度）

| 步骤 | 主 agent 动作 | 派发的子代理 / 决策 |
|---|---|---|
| 0 | 读 knowledge/ 并形成"项目先验摘要" | 读 `<cwd>/.opencode/skills/biz-flow-recon/knowledge/` 全量 .md（如有），抽取要点（内部服务定位 / 递归追溯深度 / 执行模式 / briefing / glossary / modules）→ 内存中的"项目先验摘要"块；解析模板路径（项目级覆盖 → skill 默认）。**不写任何文件** |
| 1 | 确定粒度 | 见下方"粒度选择"小节 |
| 2 | 派发 `planner` | 派发 prompt 头部带"项目先验摘要"块；写 `_plan.md`；已存在则跳过 |
| 3 | 并行派发 | `interface-catalog` + N × `endpoint-analyst`（每接口一个）；派发 prompt 头部均带"项目先验摘要"块；按 `_plan.md` 顺序派发——`planner` 已按审计优先级（high → medium → low）排序，串行模式下自然先做高优先级；默认并行，"项目先验摘要"中"执行模式: 串行"时改串行 |
| 4 | 等待 + 失败重试 | 子代理失败重派最多 2 次；仍失败则在产物头部插入 `<!-- ⚠ 产物自检未通过：缺失 X 请人工补全 -->`，**不阻断** |
| 5 | 派发 `aggregator-writer` | 派发 prompt 头部带"项目先验摘要"块 + 粒度参数；产出 `features.md` / `features-{slug}.md` / `overview.md`；顶部带横向产物链接 |
| 6 | 派发 `completion-verifier` | 派发 prompt 头部带"项目先验摘要"块；写 `_audit.md`；**不阻断流程** |
| 7 | 告知用户产物路径 | aggregator 入口 + 横向产物（`interfaces.md`）+ `_audit.md` |

### 粒度选择（步骤 1）

- **A（整项目）**：用户用泛指——"整个项目 / 系统 / 全貌 / 在做什么 / 梳理一下"
- **B（子功能 + 接口）**：用户限定子功能或路径片段——"支付下单流程"、"`/api/users/*`"、"用户中心模块"
- **C（单接口）**：用户给具体单接口——METHOD URL 形式（"`POST /api/transfer`"）

### 项目先验摘要（派发 prompt 头部块）

主 agent 在所有派发的 prompt 头部插入此块（`knowledge/` 为空时只放占位"项目先验摘要：无"）：

```
[项目先验]
内部服务定位:
  - charge-svc → 代码在 ../services/charge-svc/
  - billing    → 黑盒
递归追溯深度: 3
执行模式: 串行
术语 / 项目要点:
  - <briefing.md / glossary.md / modules/*.md 抽取的关键事实，每条 1 行>
```

## 输出文件名约定

slug 小写连字符；中文转拼音/英文同义词。**slug = 路径去除前导 `/` 后小写连字符**（`/api/files/upload` → `api-files-upload`）。

| 文件 | 写入者 | 用途 |
|---|---|---|
| `_plan.md` | planner | 子任务计划 |
| `interfaces.md` | interface-catalog | 对外暴露接口清单（inbound 攻击面） |
| `endpoint-{METHOD}-{slug}.md` | endpoint-analyst | 单接口深度分析 |
| `features.md` / `features-{slug}.md` / `overview.md` | aggregator-writer | 索引 aggregator |
| `_audit.md` | completion-verifier | 任务完整性审计 |

## 工作目录与模板

详见 `docs/workspace-layout.md`。
