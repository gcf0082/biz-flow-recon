# 项目专属知识库（用户填充）

本目录是 biz-flow-recon skill 的**项目级先验知识库**。所有 7 个子代理在执行前都会**强制完整读取**本目录下所有 `.md` 文件作为先验上下文——给项目结构、术语、约定、内部服务定位等关键线索，让 agent 的搜索与判断更准确。

## 建议存放

- **`briefing.md`** —— 项目高层说明：技术栈与版本、模块布局总览、外部接口风格约定（路径命名、版本前缀、错误码规范）、跨模块共用机制（统一鉴权 / trace / 异常）、特殊查找线索
- **`glossary.md`** —— 项目特有术语（如 `BizContext = 会话上下文`、`AcmeCrypto = 内部加密 SDK`）
- **`conventions.md`** —— 团队约定（鉴权方式、加密库、日志规范、配置文件命名）+ skill 行为开关（内部服务定位 / 递归追溯深度 / 执行模式 / 知识库自我演化）
- **`modules/*.md`** —— 每个子模块一份说明：功能、协作对象
- **`auto-*.md`** —— 由 `knowledge-extractor` 子代理自动写入（含 `auto-briefing.md` / `auto-glossary.md` / `auto-internal-services.md` / `auto-conventions.md`）；与上述用户文件**并存且不覆盖**

## 配置开关示例（写在 `conventions.md`）

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

## 原则

内容**应保持精炼**——这是给 Claude 的先验提示，冗余反而降低准确度。
