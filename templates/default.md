<!--
单接口产物（endpoint-*.md）的格式参考。可被被分析项目内的同名文件覆盖。

每个 subagent 撰写自身的 endpoint-*.md 时，将下文 `#### {METHOD} {URL}` 一节的
标题升级为顶层 `# {METHOD} {URL} — 一句话功能`，正文格式照搬。本文件的顶层
"业务流讲解" / "整体在做什么" / "子功能 N" 等结构面向 aggregator（overview.md /
features.md）使用——单接口产物文件不包含此类外层包装。
-->

# {范围名} 业务流讲解

## 整体在做什么

80-200 字段落形式叙述：本范围内代码的功能、触发者、关键流程的串接关系。

## 业务流

### 子功能 1：文件管理

#### POST /api/files/upload

已登录用户向系统提交一份业务文件（合同、表单、附件等）进行存档（com.acme.file.UploadController#upload，UploadController.java:48）。controller 先按用户提供的文件名将原始内容落地到本地存储，随后调用扫描脚本对该文件做内容检查（具体检查项由脚本决定），扫描结果以 JSON 形式归档至结果目录，供后续业务消费。

由于用户传入的 `filename` 同时贯穿落地路径、扫描命令参数、结果路径三个高危动作，绘图揭示传播链路：

```mermaid
flowchart TD
    IN["body.filename (用户输入)"] --> WRITE["写 /data/uploads/{filename} (写文件)"]
    IN --> SCAN["ProcessBuilder bash scripts/scan.sh /data/uploads/{filename} (拼命令 + 外部进程)"]
    WRITE --> SCAN
    SCAN --> RESULT["写 /data/scan-results/{filename}.json (写文件)"]
```

- **请求**：multipart/form-data，含 `file`（binary，原始内容）+ form 字段 `filename` (string!)
- **输入流向**：
  - `body.filename` → `Paths.get("/data/uploads/" + filename)` → `Files.write`（UploadController.java:62）—— 拼接到路径
  - `body.filename` → `ProcessBuilder("bash", "scripts/scan.sh", "/data/uploads/" + filename)`（UploadController.java:71）—— 拼接到命令
  - `body.filename` → `Paths.get("/data/scan-results/" + filename + ".json")` → `Files.write`（UploadController.java:84）—— 拼接到路径
- **文件**：写入 `/data/uploads/{body.filename}`（用户传入文件名，原始上传内容落盘）；写入 `/data/scan-results/{body.filename}.json`（JSON，扫描结果）
- **命令**：`ProcessBuilder` 执行 `bash scripts/scan.sh /data/uploads/{body.filename}`（UploadController.java:71）

## 未能追溯的引用

仅在存在未能定位的下游目标时撰写本节，按 `<引用> — 调用点 (文件:行号)` 一条一行；无则**略去整节**。

- `scripts/scan.sh` — 调用点 com.acme.file.UploadController#upload（UploadController.java:71），未在工作区找到该脚本
