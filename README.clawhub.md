# Patent Skills Suite — ClawHub Publish Guide

[English](#english) · [中文](#中文)

---

## 中文

### 套件说明

本仓库包含三个可独立发布的 OpenClaw / Agent 技能，对接 [9235](https://www.9235.net) 专利数据服务：

| 技能 | 目录 | 凭证 | 能力摘要 |
|------|------|------|----------|
| **patent-search** | `dist/patent-search/` | `PATENT_API_TOKEN` | 检索、详情、权利要求、说明书、法律信息、引用、相似专利、企业画像、统计、Excel 导出 |
| **patent-transaction** | `dist/patent-transaction/` | `TRADE_API_TOKEN` | 在售专利、成交记录、开放许可、采购需求、Excel 导出 |
| **patent-disclosure** | `dist/patent-disclosure/` | 无第三方 Token | 交底书模板、检查清单、Markdown → Word 导出 |

**纯净版**位于 `dist/`，不含 `config.json`、调试脚本、测试脚本与 `__pycache__`。

### 许可证

ClawHub 要求 **MIT-0**。本仓库 [LICENSE](LICENSE) 已使用 MIT-0；发布时须在网页 **勾选 Accept MIT-0**。

### 发布步骤

详见 **[PUBLISH.md](PUBLISH.md)**。要点：上传 **`dist/patent-search`** 等子目录，不要上传仓库根。

### 安装（终端用户）

完整步骤见 **[INSTALL.md](INSTALL.md)**。

### 重新构建 dist

```bash
bash scripts/build-dist.sh
```

### 发布到 [ClawHub](https://clawhub.ai/)

1. 在 [9235 开放平台](https://www.9235.net/api/open) 申请检索 API Token（`patent-search`）。
2. 向运维申请交易 Skill Token（`patent-transaction`，`trade.9235.net/api/skill`）。
3. 分别将 `dist/patent-search`、`dist/patent-transaction`、`dist/patent-disclosure` 作为独立技能上传（具体以 ClawHub 当前上传流程为准）。
4. 在技能页填写 **中英文描述**（各目录内 `README.md` 与 `SKILL.md` 已提供）。
5. 提醒用户配置环境变量或 OpenClaw `skills.entries.<name>.apiKey`，**勿**在包内提交真实 Token。

### OpenClaw 本地安装（示例）

```bash
openclaw skills install /path/to/patents/dist/patent-search
openclaw config set skills.entries.patent-search.apiKey 'YOUR_PATENT_TOKEN'

openclaw skills install /path/to/patents/dist/patent-transaction
openclaw config set skills.entries.patent-transaction.apiKey 'YOUR_TRADE_TOKEN'

openclaw skills install /path/to/patents/dist/patent-disclosure
```

### 协作关系

- **尽调**：`patent-search`（法律状态、权利要求）+ `patent-transaction`（挂牌、成交）→ 见 `patent-transaction/due-diligence.md`
- **交底书**：`patent-disclosure` 撰写 + `patent-search` 现有技术检索

---

## English

### Suite overview

Three publishable skills for OpenClaw-compatible agents, backed by [9235](https://www.9235.net) patent APIs:

| Skill | Path | Credential | Summary |
|-------|------|------------|---------|
| **patent-search** | `dist/patent-search/` | `PATENT_API_TOKEN` | Search, detail, claims, description, legal events, citations, similar patents, company portrait, analytics, Excel export |
| **patent-transaction** | `dist/patent-transaction/` | `TRADE_API_TOKEN` | Listings, deals, open licensing, procurement demands, Excel export |
| **patent-disclosure** | `dist/patent-disclosure/` | None (local docx) | Disclosure template, checklist, Markdown → Word export |

**Clean packages** live under `dist/` (no secrets, no dev/debug scripts).

### Install (end users)

See **[INSTALL.md](INSTALL.md)** at the repo root.

### Rebuild

```bash
bash scripts/build-dist.sh
```

### Publish to [ClawHub](https://clawhub.ai/)

1. Obtain a search API token from [9235 Open API](https://www.9235.net/api/open).
2. Obtain a trade skill token for `patent-transaction` from your operator.
3. Upload each `dist/<skill-name>` folder as a separate listing.
4. Use the bilingual `README.md` and `SKILL.md` in each folder for marketplace copy.
5. Never ship real tokens inside the package.

### OpenClaw install (example)

```bash
openclaw skills install /path/to/patents/dist/patent-search
openclaw config set skills.entries.patent-search.apiKey 'YOUR_PATENT_TOKEN'
```

### Working together

- **Due diligence**: combine `patent-search` + `patent-transaction` (see `due-diligence.md`).
- **Invention disclosure**: `patent-disclosure` + `patent-search` for prior-art search.

---

**Contact**: xxiao98@gmail.com · Data provider: [9235.net](https://www.9235.net)
