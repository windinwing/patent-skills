# 专利 Skill 套件 · Patent Skills Suite

[![ClawHub](https://img.shields.io/badge/ClawHub-clawhub.ai-orange.svg)](https://clawhub.ai)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)

[English](#english) · [中文](#中文)

三个可独立使用的 OpenClaw / Agent 技能，对接 [9235](https://www.9235.net) 专利检索与交易 API。

> **安装**：请阅读 **[INSTALL.md](INSTALL.md)**（GitHub 一仓、`dist/` 一次加载三技能、ClawHub、凭证配置）。

---

## 中文

### 技能一览

| 技能 | 开发目录 | 安装目录 (`dist/`) | 凭证 |
|------|----------|-------------------|------|
| 专利检索 | [patent-search/](patent-search/) | `dist/patent-search/` | `PATENT_API_TOKEN` |
| 专利交易 | [patent-transaction/](patent-transaction/) | `dist/patent-transaction/` | `TRADE_API_TOKEN` |
| 技术交底书 | [patent-disclosure/](patent-disclosure/) | `dist/patent-disclosure/` | 无（导出需 `python-docx`） |

### 快速开始（GitHub）

```bash
git clone https://github.com/<你的用户名>/patent-skills.git
cd patent-skills
# 配置 OpenClaw extraDirs → 本仓库的 dist/ 绝对路径（见 INSTALL.md）
export PATENT_API_TOKEN='你的token'
```

### 目录说明

| 路径 | 用途 |
|------|------|
| **`dist/`** | 对外安装与 ClawHub 发布用 **纯净包**（提交到 Git） |
| `patent-*/` | 日常开发源码（含调试脚本，不直接对外分发） |
| `scripts/build-dist.sh` | 从源码重新生成 `dist/` |
| [INSTALL.md](INSTALL.md) | 安装与配置（中英） |
| [README.clawhub.md](README.clawhub.md) | ClawHub 发布者说明 |

### 协作场景

- **尽调**：`patent-search` + `patent-transaction` → [due-diligence.md](patent-transaction/due-diligence.md)
- **交底书**：`patent-disclosure` + `patent-search` 现有技术检索

### 安全

- 切勿提交 `config.json`、`.env` 或真实 Token（已写入 [.gitignore](.gitignore)）
- 检索技能合规说明：[patent-search/COMPLIANCE.md](patent-search/COMPLIANCE.md)
- ClawHub 发布：[PUBLISH.md](PUBLISH.md)（须勾选 MIT-0、从 `dist/` 上传）

---

## English

### Skills

| Skill | Dev tree | Install from (`dist/`) | Credential |
|-------|----------|------------------------|------------|
| Patent search | [patent-search/](patent-search/) | `dist/patent-search/` | `PATENT_API_TOKEN` |
| Patent trade | [patent-transaction/](patent-transaction/) | `dist/patent-transaction/` | `TRADE_API_TOKEN` |
| Invention disclosure | [patent-disclosure/](patent-disclosure/) | `dist/patent-disclosure/` | none (`python-docx` for export) |

### Quick start (GitHub)

```bash
git clone https://github.com/<your-user>/patent-skills.git
cd patent-skills
# Point OpenClaw skills.load.extraDirs at .../patent-skills/dist (see INSTALL.md)
export PATENT_API_TOKEN='your-token'
```

### Layout

| Path | Purpose |
|------|---------|
| **`dist/`** | Clean install bundles (committed for clone-and-use) |
| `patent-*/` | Development sources |
| [INSTALL.md](INSTALL.md) | Full install guide (ZH/EN) |
| [PUBLISH.md](PUBLISH.md) | ClawHub publish (MIT-0, dist path, CLI) |
| [README.clawhub.md](README.clawhub.md) | ClawHub overview |

### License

**MIT-0** (MIT No Attribution) — required for [ClawHub](https://clawhub.ai/). See [LICENSE](LICENSE). Publish guide: [PUBLISH.md](PUBLISH.md).

**Contact**: xxiao98@gmail.com · Data: [9235.net](https://www.9235.net)
