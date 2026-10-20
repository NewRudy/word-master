# 常见问题

[English](./faq.md) | 中文

## 入门

### 需要装 Microsoft Office 吗？

不需要。WPS 就够，LibreOffice 也能看。整条流水线从不驱动 Word——它直接写 OOXML。

唯一需要 Office/WPS 的地方：**刷新域**。目录和交叉引用是带 `w:dirty="true"` 的真实 Word 域。打开文档，`Ctrl+A`，再按 `F9`。一秒钟的操作，不是构建步骤。

### 需要会 Python 吗？

日常使用不需要。你装一次 Python 让脚本能跑，之后由 agent 调用。

但**初次**安装（`git clone`、`pip install`）需要你能用终端。

### 该用哪个模型？

需要满足两点：(a) 能严格照一份约 60 行的内容语法写；(b) 能在长文档里记住章节大纲。实践上：Claude Sonnet/Opus、GPT-5 级、Gemini Pro、Kimi K2/K3、DeepSeek-V3 级。

弱模型不会破坏门禁——它会产出**通过**门禁但读起来很差的文字。门禁保格式，不保文笔。

### 要花多少钱？

项目免费、MIT 协议。唯一成本是模型 token。一份 6000 字带研究的报告，中端模型通常不到一块钱；换顶配模型加深度思考可能几块到十几块。

## 概念

### "模板包"到底是什么？

`skills/word-master/templates/docs/<name>/` 下的一个目录：

| 文件 | 作用 |
|---|---|
| `template_src.docx` | 单位原件的字节副本，永不修改，审计线索 |
| `template.docx` | 清理后的构建壳：保留样式、编号、页面设置、页眉页脚，剥掉演示内容 |
| `contract.json` | 机器真相：角色 → styleId 映射、白名单、禁用表、编号方案、门禁规则 |
| `template_contract.md` | `contract.json` 的人类可读孪生 |
| `analysis.md` | 入库分析：样式清单、瑕疵登记、缺口清单 |

### 为什么不能让 AI 自己选字体字号？

因为这正是项目要消灭的失效模式。模型一旦被允许做**一个**格式决定，它就会在不同章节、不同次运行之间做出不一致的决定。契约把决定权彻底拿掉：角色映射到 `styleId`，格式由样式承载。

### 为什么 7 级以下序号必须手打？

这是参考模板里固化的单位约定，不是能力限制。理由：多份文档合并成总册时，自动编号会意外重排；手打的 `（1）→ 1) → ① → a)` 合并后原样保留。门禁强制这一点（`C5`）。

如果你们单位没有这条约定，就在你自己的模板契约里写你自己的规则。

### 题注为什么分上下？

图名在图的**下方**，表题在表的**上方**。这是中文工程文档的惯例，由契约固定（`fig_caption_after_figure`、`tbl_caption_before_table`）。

## 使用

### 门禁报 `BLOCKING [C1] 样式不在白名单`

构建产物里出现了不在 `contract.json` 白名单中的段落样式。

最常见原因：`content.md` 里写的东西被 builder 映射到了非预期样式，或者你手改了构建出的 `.docx`（永远不要手改——重新构建）。

如果这个样式确实需要，把它加进契约，**并且**在 `template_contract.md` 里登记对应角色。

### 门禁报 `BLOCKING [C4] 题注疑似手打编号`

你把 `图1.1-1 某某图` 写成了题注文字。只写标题文字（`某某图`），编号由样式的自动编号生成。表格同理。

### 门禁报 `BLOCKING [R1] content 引用了未登记事实`

`content.md` 里有 `<!-- F007 -->`，但 `facts.json` 里没有 `F007`。要么补上事实和来源，要么删掉引用。

反过来的情况（`R2`，事实没被引用）只是 advisory。

### 门禁报 `BLOCKING [C6] 图片段之后不是图名`

每个 `:::figure` 块后面必须紧跟对应的 `:::caption fig <slug> …`。中间不能有空段落，也不能有正文。

### 目录是空的 / 显示 "错误！未找到目录项"

域没刷新。用 WPS 或 Word 打开，`Ctrl+A`，`F9`。如果还不行，在弹出的对话框里选"更新整个目录"。

### 图片不显示

`<img: ...>` 里是相对路径时，按项目目录解析。检查文件是否存在、格式是否被 `python-docx` 支持（PNG、JPEG、GIF、BMP、TIFF）。

### 生成的文档之后还能改吗？

能——它就是一份用你们单位样式的普通 `.docx`，在 Word/WPS 里随便改。

但是：一旦手改过，就不要再拿 `content.md` 覆盖构建。两个方向选一个。改动大就把改动折回 `content.md` 重建；只是最终润色（封面、签署栏）就最后再做。

### 能支持我们单位的模板吗？

能——这就是 *Create Template* 路线。完整模板包需要什么，见 [CONTRIBUTING_CN.md](../CONTRIBUTING_CN.md#新增模板包)。

注意：严重依赖浮动图片、文本框或内容控件的模板可能无法完全复现，入库分析会告诉你。

## 排错

### Windows 上 `UnicodeEncodeError`

所有脚本都加 `-X utf8`：

```bash
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -X utf8 skills/word-master/scripts/doc_checker.py check projects/xxx
```

### 找不到 `python-docx`

```bash
pip install -r requirements.txt
```

机器上有多个 Python 时，装进你实际运行的那个：

```bash
"<python 完整路径>" -m pip install -r requirements.txt
```

### builder 说模板壳不存在

那个模板包还没产出 `template.docx`。走完 *Create Template* 第 4 步，或重新安装该包。

### 看着都对，评审还是有意见

先分清意见是关于**格式**（门禁管）还是**内容**（你管）。门禁不可能知道第 3 章和第 1 章矛盾、某个数字过期了、或者单位要一个特定封面。

## 项目边界

word-master 有意**不做**：

- 生成封面、签署页、审批表（单位各异，设计上留给人工）
- 通过 COM 驱动 Word/WPS（已规划，未发布）
- 原生 PDF 转文本（已规划，当前只复制原件）
- 提供 Web UI 或托管服务
- 替你选模型或 Provider

理由见 [why-word-master_CN.md](./why-word-master_CN.md)。

### 门禁报 `advisory [C9] 交叉引用不在实际标题编号中`

正文写了 `见 9.9 节`，但没有任何标题的实际编号是 9.9。这是 advisory（不拦交付），因为引用可能是有意的、或者那个章节还没写。改掉编号，或者删掉这句引用。

### 门禁报 `advisory [C10] 正文首行缩进被覆盖`

某个正文段自带 `w:ind`，和样式定义的不一样。这正是契约要消灭的漂移，所以会标记——但不拦交付，因为有些文档确实需要局部例外。要么删掉覆盖，要么如果真是单位约定，就把它写进模板契约。
