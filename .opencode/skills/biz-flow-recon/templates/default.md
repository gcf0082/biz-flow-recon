<!--
单接口产物（endpoint-*.md）的格式参考。可被被分析项目内的同名文件覆盖。

每个 subagent 撰写自身的 endpoint-*.md 时，将下文 `#### {METHOD} {URL}` 一节的
标题升级为顶层 `# {METHOD} {URL} — 一句话功能`，正文格式照搬。本文件的顶层
"业务流讲解" / "整体在做什么" / "子功能 N" 等结构面向 aggregator（overview.md /
features.md）使用——单接口产物文件不包含此类外层包装。

约定：图自包含——优先把输入流向、关键控制点、硬编码标注等事实**嵌入节点标签**；
图能承载的下方文字 labeled 列表不再重复，仅保留图无法承载的（如 DTO 全限定名 /
请求体字段树）。起点节点统一用 `START([开始])`，接口 URL / 请求维度由标题与
`**请求**` 行承载。

观测点（审计标记）：命中 A/B/C/D 任一类的图节点 `<small>` 行末追加 `🔍 (X)`，
节点 `style` 按观测优先级配色——高（红 #FCE4E4 / #C0392B）/ 中（橙 #FDF2E0 /
#D68910）/ 低（浅黄 #FEF9E7 / #B7950B）；未命中节点保持默认蓝灰 #E8EEF2 /
#5B7B94。下例中 ③/④/⑤/⑥ 均高观测优先级（用户输入直接拼到敏感槽 + TLS 校验
关闭 + 内部 host 硬编码）。
-->

# {范围名} 业务流讲解

## 整体在做什么

80-200 字段落形式叙述：本范围内代码的功能、触发者、关键流程的串接关系。

## 业务流

### 子功能 1：文件管理

#### POST /api/files/upload

用户向系统提交一份业务文件（合同、表单、附件等）进行存档（com.acme.file.UploadController#upload，UploadController.java:48）。处理流程分为**前置校验 → 核心处理 → 异常终止**三组：先校验文件后缀与大小，通过后落地原始文件、触发扫描、归档结果、上报监控；任一校验失败直接返回 4xx。

```mermaid
flowchart TD
    START([开始]) --> CHECK_EXT

    subgraph 前置校验
        CHECK_EXT{"① 校验 body.filename 后缀<br/>白名单 .pdf / .docx / .jpg / .png<br/><small>UploadController.java:41 · 关键控制点（判断）</small>"}
        CHECK_SIZE{"② 校验 file 大小<br/>≤ 50 MB<br/><small>application.yml:67 · 关键控制点（限制）</small>"}
    end

    subgraph 异常终止
        REJECT_EXT["❌ 返回 400 不支持类型<br/><small>UploadController.java:52</small>"]
        REJECT_SIZE["❌ 返回 413 体积超限<br/><small>UploadController.java:55</small>"]
    end

    subgraph 核心处理
        WRITE["③ 落地原始文件<br/>写 /data/uploads/{body.filename}<br/>—— body.filename 拼接到路径<br/><small>UploadController.java:62 🔍 (A)</small>"]
        SCAN["④ 触发内容扫描<br/>ProcessBuilder bash scripts/scan.sh /data/uploads/{body.filename}<br/>—— body.filename 拼接到命令；scripts/scan.sh · 硬编码<br/><small>UploadController.java:71 · 关键控制点（配置） 🔍 (A)</small>"]
        ARCHIVE["⑤ 归档扫描结果<br/>写 /data/scan-results/{body.filename}.json<br/>—— body.filename 拼接到路径<br/><small>UploadController.java:84 🔍 (A)</small>"]
        REPORT["⑥ 上报到监控<br/>POST https://monitor.internal/scan-events · 硬编码<br/>OkHttp · TLS 校验关闭（trustAll X509TrustManager + HostnameVerifier 恒真）<br/><small>MonitorClient.java:33 · 关键控制点（开关） 🔍 (C,D)</small>"]
    end

    CHECK_EXT -->|否| REJECT_EXT
    CHECK_EXT -->|是| CHECK_SIZE
    CHECK_SIZE -->|否| REJECT_SIZE
    CHECK_SIZE -->|是| WRITE
    WRITE --> SCAN
    SCAN --> ARCHIVE
    ARCHIVE --> REPORT

    style START fill:#E8EEF2,stroke:#5B7B94,stroke-width:2px,color:#2C3E50
    style CHECK_EXT fill:#E8EEF2,stroke:#5B7B94,stroke-width:2px,color:#2C3E50
    style CHECK_SIZE fill:#E8EEF2,stroke:#5B7B94,stroke-width:2px,color:#2C3E50
    style REJECT_EXT fill:#E8EEF2,stroke:#5B7B94,stroke-width:2px,color:#2C3E50
    style REJECT_SIZE fill:#E8EEF2,stroke:#5B7B94,stroke-width:2px,color:#2C3E50
    style WRITE fill:#FCE4E4,stroke:#C0392B,stroke-width:2px,color:#641E16
    style SCAN fill:#FCE4E4,stroke:#C0392B,stroke-width:2px,color:#641E16
    style ARCHIVE fill:#FCE4E4,stroke:#C0392B,stroke-width:2px,color:#641E16
    style REPORT fill:#FCE4E4,stroke:#C0392B,stroke-width:2px,color:#641E16
```

## 未能追溯的引用

仅在存在未能定位的下游目标时撰写本节，按 `<引用> — 调用点 (文件:行号)` 一条一行；无则**略去整节**。

- `scripts/scan.sh` — 调用点 com.acme.file.UploadController#upload（UploadController.java:71），未在工作区找到该脚本
