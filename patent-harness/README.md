# 9235 Patent Harness

轻量任务执行包，通过远程 MCP 执行多步专利任务，保存原始结果并支持断点恢复。
Python 3.10+，macOS / Linux；只需标准库。它不包含大模型：需要自然语言编排、图表和 Office 报告时，在 https://mchat.9235.net 使用现有专利工作流。

## 运行

1. 在 https://www.9235.net/api/open 申请 API Token。
2. 在当前终端设置 `PATENT_API_TOKEN`。凭证只通过 Authorization 请求头传输，不写进计划或 checkpoint。
3. 在解压目录执行：

```bash
python3 harness.py doctor
python3 harness.py run --plan research.example.json --dry-run
python3 harness.py run --plan research.example.json --out runs/battery --max-calls 5
python3 harness.py resume --plan research.example.json --out runs/battery --max-calls 5
```

示例计划最多调用 5 次付费/配额工具：检索、首条详情、首条权利要求、年度统计、申请人统计。空结果或权限错误会停止，已成功步骤不会再次执行。统计、全文等权限由已有 Token 套餐决定。

每个 `tool` 使用 `tools` 命令返回的名称与参数；`{"$ref":"search#/patents/0/id"}` 引用前面步骤的 JSON 结果。先改完所有检索式，再运行。

`checkpoint.json` 保存每步状态和原始数据，`report.md` 提供执行概览。目录绑定计划、服务地址和 Token；改变其中一项应使用新的输出目录。

## 中断与重试

恢复会跳过成功步骤。如果上次调用失败、超时或执行中断，先检查 checkpoint；确认愿意承担可能的重复计次后使用 `--retry-failed`。预算是此任务累计尝试次数，需要时显式提高 `--max-calls`，最多 50 次。不会后台无限重试，也不会自动退回 REST。

可选 `PATENT_MCP_URL` 默认为 `https://www.9235.net/api/mcp`。仅允许 HTTPS；本地开发可以使用 loopback HTTP。

## mchat 整合

mchat 的 `patent-search` 技能使用相同客户端：在技能 Secrets 中设置 `PATENT_TRANSPORT=mcp` 和已有的 `PATENT_API_TOKEN`，可选 `PATENT_MCP_URL`。原有 search / analysis 节点、`patent-report` 导出与工作流恢复继续使用原格式。不要将 mchat 登录 Token 当作 9235 API Token。
