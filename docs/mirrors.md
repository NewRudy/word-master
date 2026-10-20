# 镜像仓库（AtomGit / Gitee）

GitHub 在国内经常慢或不通。为了让项目可达，维护者需要把它同步到 AtomGit 和 Gitee。

## 为什么不是自动的

建仓需要访问令牌。这个仓库里没有、也不应该有令牌。所以：

- **首次建仓 + 首次推送**：本地跑一次 `scripts/mirror.py`（需要你的 token）
- **之后的持续同步**：GitHub Actions 的 `mirror.yml` 自动完成（需要仓库 secrets）

## 一次性设置

> **当前状态**：Gitee 镜像已建立（账号 `hhhsbgitee`，仓库
> https://gitee.com/hhhsbgitee/word-master）。AtomGit 尚未建立。
> 下面第 4 节的 README 片段已经应用。

### 1. 拿 token

| 平台 | 地址 | 需要的作用域 |
|---|---|---|
| Gitee | https://gitee.com/profile/personal_access_tokens | `projects`（读写） |
| AtomGit | https://atomgit.com/-/profile/personal_access_tokens | `repo`（读写） |

### 2. 建仓并首次推送

**推荐：用令牌文件**（令牌不会进 shell 历史，也不会进进程列表）

```bash
cd word-master

# 写一个只有你能读的文件（Git Bash / Linux / macOS）
printf 'GITEE_TOKEN=你的gitee令牌
ATOMGIT_TOKEN=你的atomgit令牌
' > ~/.word-master-tokens
chmod 600 ~/.word-master-tokens

python scripts/mirror.py --all --token-file ~/.word-master-tokens

# 用完删掉
rm ~/.word-master-tokens
```

**或者用环境变量**（注意：在某些 shell 里会进历史记录）

```bash
GITEE_TOKEN=xxxxx ATOMGIT_TOKEN=yyyyy python scripts/mirror.py --all

# 只做其中一个：
GITEE_TOKEN=xxxxx python scripts/mirror.py --gitee
ATOMGIT_TOKEN=yyyyy python scripts/mirror.py --atomgit
```

脚本不会把令牌写在命令行上（`git push` 走临时 credential helper + 环境变量），
所以 `ps aux` 和错误输出里都看不到它。

脚本会：读取账号 → 建仓（已存在则跳过）→ 设置描述和 topics → 推送 `main` 和 tags。
可重复执行，幂等。

> AtomGit 的公开 API 前缀不稳定。如果脚本报"API 不可用"，去
> https://atomgit.com/projects/new 手动建一个空仓库（不要初始化 README），
> 然后重跑脚本——推送部分仍然有效。

### 3. 配置自动同步

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 里加两个 secret：

- `ATOMGIT_TOKEN`
- `GITEE_TOKEN`

之后每次 push 到 `main` 或打 `v*` tag，`.github/workflows/mirror.yml` 会自动同步。
没配 secret 时该 workflow 会跳过对应步骤，不会失败。

### 4. 把镜像链接补回 README

两个都建好之后，在 `README.md` 的 "Updating later" 之前、`README_CN.md` 的
"以后更新" 之前，加回镜像段落：

```markdown
#### Mirrors

Mirrored to [AtomGit](https://atomgit.com/NewRudy/word-master) and
[Gitee](https://gitee.com/NewRudy/word-master). Mirrors are push-only and may
lag by a few minutes; issues and pull requests belong on GitHub.
```

```markdown
#### 国内镜像

同步镜像到 [AtomGit](https://atomgit.com/NewRudy/word-master) 和
[Gitee](https://gitee.com/NewRudy/word-master)。镜像单向同步，可能滞后几分钟；
Issue 和 PR 请提到 GitHub。
```

> 在镜像真正存在之前不要加这两段——死链比没有镜像更伤。

## 注意

- 镜像**只读单向**：从 GitHub 推到镜像，不要反向。
- Gitee 的仓库名区分大小写，用 `word-master`。
- AtomGit 和 Gitee 的 CI 能力与 GitHub Actions 不同，`ci.yml` 不保证在镜像上能跑。
  真正需要 CI 时优先 GitHub；镜像只是为了让别人能 `git clone`。
