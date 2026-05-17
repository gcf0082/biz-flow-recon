# 项目分析约束

## 非分析目标（可参考理解，不作为分析产出）

以下代码可读作参考（理解项目结构、调用关系），但**不写 endpoint-*.md**：

- 测试代码（`test/`、`*Test.java`、`spec/`、`__tests__/` 等）
- 构建脚本（`pom.xml`、`build.gradle`、`Dockerfile`、`Makefile`、CI 配置）
- 纯前端 CSS / i18n 资源文件
- 静态资源、图片、字体
- 文档、README

遇到这些非目标文件时跳过即可。

## 临时脚本

分析过程中如需生成并执行临时脚本（如扫描、提取、转换），统一放在 `<cwd>/_temp/scripts/` 目录下，与 `_results/` 平级。用完即弃，不影响源码和产物。
