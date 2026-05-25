# 安装说明 · Installation Guide

[中文](#中文) · [English](#english)

本仓库为 **一个 GitHub 项目（monorepo）**，内含三个 OpenClaw / Agent 技能。对外安装请使用 **`dist/`** 目录（纯净包，无调试脚本、无密钥）。

---

## 中文

### 仓库结构

```text
patent-skills/                 # 本仓库（根目录不要放 SKILL.md）
├── dist/                      # ★ 安装用：三个技能各一个子目录
│   ├── patent-search/
│   ├── patent-transaction/
│   └── patent-disclosure/
├── patent-search/             # 开发源码（含调试脚本，勿直接当发布包）
├── patent-transaction/
├── patent-disclosure/
├── scripts/build-dist.sh      # 重新生成 dist/
├── INSTALL.md                 # 本文件
└── README.md
```

OpenClaw 会在技能根目录下扫描 **直接子文件夹**；每个子文件夹内须有 `SKILL.md`。因此 clone 本仓库后，将 **`dist` 的路径** 加入技能加载目录即可 **一次加载三个技能**。

### 前置条件

- Python 3.8+
- [OpenClaw](https://openclaw.ai) 或兼容 AgentSkills 的宿主
- （可选）检索 Token：<https://www.9235.net/api/open>
- （可选）交易 Token：由运维签发 `trade.9235.net/api/skill`

### 方式一：GitHub 克隆 + 一次加载三个技能（推荐）

```bash
git clone https://github.com/<你的用户名>/patent-skills.git
cd patent-skills
```

在 OpenClaw 配置（`openclaw.json` 或等价配置）中增加：

```json5
{
  skills: {
    load: {
      extraDirs: ["/绝对路径/patent-skills/dist"]
    },
    entries: {
      "patent-search": {
        apiKey: "YOUR_PATENT_API_TOKEN"
      },
      "patent-transaction": {
        apiKey: "YOUR_TRADE_API_TOKEN"
      }
    }
  }
}
```

或使用环境变量（与 `config.example.json` 一致）：

```bash
export PATENT_API_TOKEN='你的检索token'
export TRADE_API_TOKEN='你的交易token'
```

重启 OpenClaw / 新开 Agent 会话后，应能看到 `patent-search`、`patent-transaction`、`patent-disclosure` 三个技能。

> **说明**：`patent-disclosure` 无需 9235 Token；导出 Word 需 `pip install python-docx`（见 `dist/patent-disclosure/requirements.txt`）。

### 方式二：只安装其中一个技能

将 **单个** 技能目录复制或链接到 OpenClaw 技能目录，例如：

```bash
# 全局技能目录示例（路径以你的 OpenClaw 版本为准）
cp -R dist/patent-search ~/.openclaw/skills/patent-search
```

或仅把 `extraDirs` 指向单个目录（不推荐同时指向 dev 源码目录，其中含调试文件）：

```json5
{ skills: { load: { extraDirs: ["/path/to/patent-skills/dist/patent-search"] } } }
```

### 方式三：ClawHub 市场安装

在 [ClawHub](https://clawhub.ai/) 搜索并安装（三个独立 listing，可按需只装一个）：

```bash
openclaw skills install patent-search
openclaw skills install patent-transaction
openclaw skills install patent-disclosure
```

配置 Token 见上文 `skills.entries` 或环境变量。发布者打包说明见 [README.clawhub.md](README.clawhub.md)。

### 方式四：本地路径安装（已 clone 仓库时）

若你的 OpenClaw 版本支持从本地目录安装：

```bash
cd patent-skills
openclaw skills install ./dist/patent-search --global
openclaw skills install ./dist/patent-transaction --global
openclaw skills install ./dist/patent-disclosure --global
```

### 本地配置文件（可选）

各技能目录下：

```bash
cp dist/patent-search/config.example.json dist/patent-search/config.json
# 编辑 config.json 填入 token（该文件已被 .gitignore 忽略，不会提交）
```

### 重新构建 dist

修改开发目录源码后，发布或提交前请执行：

```bash
bash scripts/build-dist.sh
```

然后将更新的 `dist/` 一并提交到 GitHub。

### 依赖安装

| 技能 | 命令 |
|------|------|
| patent-search | `pip install requests` |
| patent-transaction | `pip install requests` |
| patent-disclosure | `pip install -r dist/patent-disclosure/requirements.txt` |

### 验证

```bash
cd dist/patent-search
export PATENT_API_TOKEN='你的token'
python3 main.py search 锂电池
```

### 常见问题

**Q: clone 整个仓库后只看到一个技能？**  
A: 不要把 `extraDirs` 指到仓库根目录；应指向 **`dist`**，或只复制 `dist` 下的子目录。

**Q: 能否用 `patent-search/` 开发目录安装？**  
A: 开发与 `dist/` 源码一致时可直接用开发目录；**对外分发与 ClawHub 请用 `dist/patent-search/`**。

**Q: Token 会进 Git 吗？**  
A: 不会。`config.json` 与 `.env` 已在 `.gitignore` 中忽略。

---

## English

### Repository layout

This is a **single monorepo** with three skills. Install from **`dist/`** (clean packages only).

```text
patent-skills/
├── dist/                      # ★ install from here
│   ├── patent-search/
│   ├── patent-transaction/
│   └── patent-disclosure/
├── patent-search/             # dev sources (debug scripts)
└── scripts/build-dist.sh
```

Point OpenClaw at `dist/` so all three child folders (each with `SKILL.md`) are discovered at once.

### Prerequisites

- Python 3.8+
- OpenClaw or AgentSkills-compatible host
- Optional: patent API token from <https://www.9235.net/api/open>
- Optional: trade skill token for `patent-transaction`

### Option 1: GitHub clone + load all three (recommended)

```bash
git clone https://github.com/<your-user>/patent-skills.git
cd patent-skills
```

Add to OpenClaw config:

```json5
{
  skills: {
    load: {
      extraDirs: ["/absolute/path/patent-skills/dist"]
    },
    entries: {
      "patent-search": { apiKey: "YOUR_PATENT_API_TOKEN" },
      "patent-transaction": { apiKey: "YOUR_TRADE_API_TOKEN" }
    }
  }
}
```

Or use environment variables:

```bash
export PATENT_API_TOKEN='your-token'
export TRADE_API_TOKEN='your-trade-token'
```

Restart OpenClaw. You should see all three skills. `patent-disclosure` needs no 9235 token; install `python-docx` for Word export.

### Option 2: Install one skill only

```bash
cp -R dist/patent-search ~/.openclaw/skills/patent-search
```

Or set `extraDirs` to a single skill path under `dist/`.

### Option 3: ClawHub

```bash
openclaw skills install patent-search
openclaw skills install patent-transaction
openclaw skills install patent-disclosure
```

See [README.clawhub.md](README.clawhub.md) for publishers.

### Option 4: Local path install

```bash
openclaw skills install ./dist/patent-search --global
# repeat for other skills if needed
```

### Rebuild `dist/`

```bash
bash scripts/build-dist.sh
git add dist/
git commit -m "chore: refresh dist packages"
```

### Verify

```bash
cd dist/patent-search
export PATENT_API_TOKEN='your-token'
python3 main.py search "lithium battery"
```

### FAQ

**Q: Only one skill appears after clone.**  
A: Point `extraDirs` at **`dist`**, not the repository root.

**Q: Should I install from `patent-search/` dev tree?**  
A: Use **`dist/patent-search`** for distribution; dev tree includes debug utilities.

**Q: Will tokens be committed?**  
A: No. `config.json` and `.env` are gitignored.

---

更多细节见各技能目录下的 `README.md` 与 `SKILL.md`。
