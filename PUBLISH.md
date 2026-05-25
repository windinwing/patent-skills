# ClawHub 发布指南 · Publishing to ClawHub

[中文](#中文) · [English](#english)

ClawHub **仅支持 MIT-0**（MIT No Attribution）。仓库根目录 [LICENSE](LICENSE) 已采用 MIT-0。

---

## 中文

### 发布前检查清单

- [ ] 已登录 ClawHub（GitHub 账号注册 **满 1 周** 才能发布）
- [ ] 在发布页 **勾选**「I have the rights…」并 **Accept MIT-0 license terms**
- [ ] 上传目录为 **`dist/patent-search`**（或 transaction / disclosure），**不是** 整个 monorepo 根目录
- [ ] 该目录根下有 **`SKILL.md`**（小写 `skill.md` 也可）
- [ ] 未包含 `config.json`、真实 token、`.env`
- [ ] `SKILL.md` 里 **不要** 写「本技能采用 MIT 许可证」等与 MIT-0 冲突的条款（平台统一 MIT-0）

### 构建纯净包

```bash
cd /path/to/patent-skills
bash scripts/build-dist.sh
```

### 方式 A：网页上传

1. 打开 <https://clawhub.ai/> 并登录  
2. 新建 Skill → 选择文件夹：**`dist/patent-search`**（一次只发一个技能）  
3. 勾选 **MIT-0** 同意框 → 发布  
4. 对 `dist/patent-transaction`、`dist/patent-disclosure` 重复（三个独立 listing）

### 方式 B：CLI（推荐，可先 dry-run）

```bash
npm install -g clawhub   # 或按 ClawHub 文档安装 CLI
clawhub login

cd /path/to/patent-skills

# 预检（不上传）
clawhub skill publish ./dist/patent-search \
  --slug patent-search \
  --name "Patent Search (9235)" \
  --version 1.0.0 \
  --changelog "Initial release" \
  --dry-run

# 正式发布（需在 UI/CLI 确认 MIT-0）
clawhub skill publish ./dist/patent-search \
  --slug patent-search \
  --name "Patent Search (9235)" \
  --version 1.0.0 \
  --changelog "Initial release"
```

交易、交底书：

```bash
clawhub skill publish ./dist/patent-transaction --slug patent-transaction --version 1.0.0 --changelog "Initial release"
clawhub skill publish ./dist/patent-disclosure --slug patent-disclosure --version 1.0.0 --changelog "Initial release"
```

### 常见「发不了」原因

| 现象 | 处理 |
|------|------|
| 要求 Accept MIT-0 | 在网页 **勾选同意**；仓库 LICENSE 须为 MIT-0（已更新） |
| 找不到 SKILL.md | 路径必须是 **`dist/技能名/`**，不是仓库根 |
| GitHub 账号太新 | 账号需满 **7 天** 才能发布 |
| 元数据校验失败 | `install.kind` 仅支持 `brew` / `node` / `go` / `uv`，**不要用 `pip`**（已改为 `uv`） |
| 密钥泄漏扫描 | 删除包内 `config.json`；`config.example.json` 里勿填真实 token |
| 安全扫描未通过 | 在 `SKILL.md` 的 `metadata.openclaw.requires.env` 中声明用到的环境变量（已配置） |
| 发布后搜不到 | 新版本需审核，通过后才在 install 列表显示 |

### Slug 命名

须小写：`patent-search`、`patent-transaction`、`patent-disclosure`（与文件夹名一致）。

---

## English

### Pre-flight checklist

- [ ] Logged in to ClawHub (GitHub account must be **at least 1 week old**)
- [ ] Checked **MIT-0 acceptance** on the publish form
- [ ] Publish folder is **`dist/<skill-name>/`**, not the monorepo root
- [ ] `SKILL.md` exists at that folder root
- [ ] No `config.json`, real tokens, or `.env` in the bundle
- [ ] Do not add conflicting license text in `SKILL.md` (platform license is MIT-0 only)

### Build clean package

```bash
bash scripts/build-dist.sh
```

### CLI publish

```bash
clawhub login
clawhub skill publish ./dist/patent-search \
  --slug patent-search \
  --version 1.0.0 \
  --changelog "Initial release" \
  --dry-run
```

Remove `--dry-run` after the preview succeeds. Repeat for `patent-transaction` and `patent-disclosure`.

### License

All ClawHub skills are released under **MIT-0**. See [LICENSE](LICENSE).
