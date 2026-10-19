# 贡献指南

[English](./CONTRIBUTING.md) | 中文

感谢参与。这个项目只有一条不可妥协的理念，其余规则都由它推导：

> **模板契约是唯一的样式权威。** AI 写内容，确定性脚本套格式，fail-closed 门禁决定能不能交付。

任何削弱这条链的改动，无论看起来多方便，都不会被合并。

## 贡献方式

| 类型 | 怎么提 |
|---|---|
| **报 Bug** | 用 [bug 表单](.github/ISSUE_TEMPLATE/bug_report.yml)，附上门禁输出，方便的话附上构建出的 `.docx` |
| **提需求** | 用 [feature 表单](.github/ISSUE_TEMPLATE/feature_request.yml)。描述你要的**格式保证**，而不是实现方式 |
| **新增模板包** | 价值最高的贡献，见下 |
| **改文档** | `README*.md`、`docs/`、`skills/**/*.md` 的修正永远欢迎 |
| **报误判** | 门禁的误报就是 Bug。请指出具体段落和它违反（或没违反）的契约条款 |

## 新增模板包

模板包是复用的最小单位，必须能从一个字节保留的原件复现。

1. 把原件放到 `skills/word-master/templates/docs/<name>/template_src.docx`。**之后永不修改**——它是审计线索。
2. 跑分析并提交产物：
   ```bash
   python skills/word-master/scripts/template_manager.py analyze <src.docx> --out skills/word-master/templates/docs/<name>
   ```
3. 手工补完 `analysis.md`：机器草稿只给清单，你必须补 **瑕疵登记**（发现的缺陷 → 影响 → 处置）和 **缺口清单**（完整报告壳需要但这份 scaffold 没有的东西）。两者都是必填——它们决定下一个维护者能否理解 builder 为什么要在某处补偿。
4. 写 `contract.json`。它是机器真相。每个角色都必须映射到模板里真实存在的 `styleId`，不许发明模板支撑不了的角色。
5. 写 `template_contract.md` 作为 JSON 的人类可读孪生。**先改 JSON，再改文档**，两者不允许漂移。
6. 用脚本生成 `template.docx`（清理壳），不许手工做。保留 `styles.xml`、`numbering.xml`、settings、页眉页脚、页面设置；剥掉演示内容。
7. 在 `templates/docs/templates_index.json` 注册。
8. 证明它能用：建一个项目指向该模板，跑 `docx_builder.py build` 和 `doc_checker.py check`，确认 `blocking = 0`。

> **授权**：只贡献你有权再分发的模板。单位内部模板往往不能公开——这种情况请用一份合成的替代文档贡献**契约结构**，并在 `analysis.md` 里说明。

## 改动 builder / checker

这两个脚本就是保证本身。改之前请确认：

- **checker 只能更严**，除非放宽是由模板本身支撑的契约变更。让 blocking 消失的"修复"如果只是削弱规则，会被拒绝。
- **builder 不许赋予契约之外的格式**：不许内联字号、不许直接段落间距、不许硬编码颜色。模板需要什么，就写进 `styles.xml` 和契约。
- 每条新规则都要有**失败夹具**：一个必须被拦下的最小项目，放在 `tests/fixtures/`。

## 开发环境

```bash
git clone https://github.com/NewRudy/word-master.git
cd word-master
pip install -r requirements.txt
pip install -r requirements-dev.txt   # pytest, ruff

# 冒烟：构建并过门禁内置演示
python skills/word-master/scripts/docx_builder.py build projects/_demo
python skills/word-master/scripts/doc_checker.py check projects/_demo --json
python -m pytest -q
```

中文 Windows 上请始终给 Python 加 `-X utf8`。

## 代码风格

- Python 3.10+，运行时除 `python-docx` 外不引入第三方依赖。
- 脚本是带 argparse 子命令的 CLI，保持可独立运行。
- 面向用户的输出：中文文档里用中文，英文文档里用英文——同一个文件不混用。
- 不写复述代码的注释。注释写**为什么**，尤其是在 builder 为模板缺陷做补偿的地方。

## 提交信息

Conventional Commits，按区域加 scope：

```
feat(builder): 支持表格单元格内多段落
fix(checker): 表格单元格内的图名不再误报
docs(faq): 说明 WPS 里为什么要 F9
feat(template): 新增中国电建 gyec 报告模板包
```

## PR 要求

- 一个 PR 只做一件事。
- 说明行为上改了什么，涉及哪条门禁规则。
- 动过 `contract.json` 的，说明是哪个模板，并贴出角色映射的 diff。
- CI 必须绿：`pytest` + 演示构建 + 演示门禁。

## 行为准则

参与即表示同意 [行为准则](./CODE_OF_CONDUCT.md)。
