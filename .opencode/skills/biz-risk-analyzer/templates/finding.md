<!--
单漏洞产物（finding-*.md）的格式参考。可被被分析项目内的同名文件覆盖。

每个 finding 独立成文件，文件名格式：finding-{category}-{endpoint-slug}-{seq}.md
category 取值：injection / path-traversal / xss / authz / authn / crypto / ssrf /
  deserialization / data-exposure / hardcoded / config / logic / other
seq：同一接口同一 category 从 1 开始递增。

严重等级与置信度必须基于源码追溯证据判定，禁止仅依赖观测点档位推断。
观测点档位（红/橙/黄）是事实分析产物中的标记，仅用于决定分析优先级，
不直接映射到本产物的严重等级。

Finding ID 格式：FIND-{category}-{endpoint-slug}-{seq}

关联接口链接使用相对路径指向 _results/ 下的 endpoint-*.md（如
../_results/endpoint-POST-api-files-upload.md）。

路径 / URL / 命令 / file:line 引用一律原样保留，禁止 ... / … 截断。
-->

# {漏洞标题}

**Finding ID**: FIND-{category}-{endpoint-slug}-{seq}

| 字段 | 值 |
|---|---|
| 严重等级 | Critical / High / Medium / Low |
| 置信度 | Confirmed / Probable / Possible |
| CWE | CWE-{number}: {name} |
| 关联接口 | [{METHOD} {path}](../_results/endpoint-{METHOD}-{slug}.md) |
| 观测点来源 | {红/橙/黄} 档 —— 节点 {node-id}：{节点描述一句话摘要} |

## 漏洞描述

2-5 句话描述漏洞的本质：什么缺陷、在哪个位置、为什么构成安全风险。
引用代码时带 `file:line` 格式。

## 可利用性分析

### 攻击向量

从用户输入到敏感操作的**完整数据流路径**，每步标注 `类#方法 (文件:行号)`。
示例：
1. 攻击者构造 `body.filename = "../../etc/passwd"`
2. `UploadController#upload`（UploadController.java:48）接收 MultipartFile
3. 文件名未经路径规范化直接拼接到存储路径
4. `File dest = new File("/data/uploads/" + body.filename)` （UploadController.java:62）
5. `dest.createNewFile()` （UploadController.java:63）写入任意路径

### 攻击者可控输入

列出攻击者**可直接控制**的输入参数，标注可控度：
- `body.filename` — 完全可控，可注入路径分隔符 `../`
- `Header: X-Forwarded-For` — 可控但仅限 IP 格式

### 前置条件

利用此漏洞需要满足的条件：
- 需要已认证用户（任何角色即可）
- 需要 Spring profile 非 production（默认 profile 即满足）
- 目标文件系统需存在写权限

### 影响范围

- **机密性**：可读取 `/etc/passwd` 等系统文件
- **完整性**：可覆盖任意可写文件，可能实现 RCE（如覆盖 .bashrc）
- **可用性**：可删除/覆盖关键文件导致服务不可用
- **影响范围**：全系统（不仅限单用户上下文）

## 代码证据

### 触发路径（数据流图）

```mermaid
flowchart LR
    ATTACKER["攻击者<br/>构造恶意输入"] -->|body.filename| CONTROLLER["UploadController<br/>#upload<br/>UploadController.java:48"]
    CONTROLLER -->|无路径规范化| SINK["new File(...)<br/>UploadController.java:62"]
    SINK -->|write| FS["文件系统"]

    style ATTACKER fill:#FCE4EC,stroke:#C62828,stroke-width:2px
    style SINK fill:#FCE4EC,stroke:#C62828,stroke-width:2px
    style CONTROLLER fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style FS fill:#E8EEF2,stroke:#5B7B94,stroke-width:2px
```

攻击者节点与 sink 节点用红色高亮；中间跳转节点用橙色；普通节点用默认蓝灰。

### 关键代码片段

```java
// UploadController.java:62 — 无路径规范化，直接拼接用户输入
File dest = new File("/data/uploads/" + body.filename);
```

仅列出关键片段，每段不超过 15 行，标注 `file:line`。

## 与源观测点的差异

若本 finding 的严重等级或漏洞类别与源观测点档位有显著差异，在此说明原因：
- 观测点标记为"中(橙)"，但源码追溯发现无任何前置校验因此升级为 High
- 或：观测点标记为"高(红)"，但验证发现已有充分补偿控制因此降级为 Medium

无需说明时略去本节。

## 缓解建议

1. **首要建议**：具体、可操作的修复方案（不写"加强安全"等空话）
2. 防纵深（defense-in-depth）：额外缓解措施
3. 检测：如何检测该漏洞是否被利用

## 参考链接

- [CWE-{number}: {name}](https://cwe.mitre.org/data/definitions/{number}.html)
- {OWASP / 其他相关参考链接}