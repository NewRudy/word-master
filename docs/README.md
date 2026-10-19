# word-master 文档索引

[English](./README_EN.md) | 中文

面向用户的文档在 `docs/` 下；工作流与技术参考由 AI 自己读取，位于 [`skills/word-master/`](../skills/word-master/SKILL.md)。

## 入门

| 文档 | 说明 |
|---|---|
| [README_CN](../README_CN.md) / [README](../README.md) | 项目主页，先读这个 |
| [FAQ](./faq_CN.md) / [EN](./faq.md) | 模型选择、成本、门禁规则解释、排错 |
| [为什么选它](./why-word-master_CN.md) / [EN](./why-word-master.md) | 适用与不适用场景，和其他方案的对比 |

## 能力与边界

| 文档 | 说明 |
|---|---|
| [SKILL.md](../skills/word-master/SKILL.md) | 全局纪律、硬规则、路由入口 |
| [路由](../skills/word-master/workflows/routing.md) | 三条路线怎么选 |
| [生成报告](../skills/word-master/workflows/generate-docx.md) | Step 1–7 主流程 |
| [模板入库](../skills/word-master/workflows/create-template.md) | 单位 `.docx` → 模板包 |
| [改已有文档](../skills/word-master/workflows/edit-native-docx.md) | 定点修改，其余字节保留 |
| [内容语法](../skills/word-master/references/content-grammar.md) | `content.md` 的全部语法 |

## 参与

| 文档 | 说明 |
|---|---|
| [CONTRIBUTING_CN](../CONTRIBUTING_CN.md) / [EN](../CONTRIBUTING.md) | 贡献方式，模板包验收清单 |
| [行为准则](../CODE_OF_CONDUCT_CN.md) | 社区规范 |
| [安全策略](../SECURITY_CN.md) | 漏洞报告与不可信文档处理 |
| [CHANGELOG](../CHANGELOG.md) | 版本记录 |

## 示例

| 位置 | 说明 |
|---|---|
| [`projects/_demo/`](../projects/_demo/) | 端到端演示，门禁通过 |
| [`docs/assets/before-after.png`](./assets/before-after.png) | 格式漂移对比图（由 `scripts/make_compare_image.py` 生成） |
