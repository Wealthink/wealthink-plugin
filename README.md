# wealthink-plugin

Operate the Wealthink platform from your AI agent, over MCP.

**Wealthink for agents** turns natural-language requests into real Wealthink
research: browse the market news Wealthink tracks for you, build and run
qualitative + quantitative research modules, and generate and share multi-asset
research reports.

## Install (Claude Code)

```bash
/plugin marketplace add Wealthink/wealthink-plugin
/plugin install wealthink@wealthink
```

Then connect: run `/mcp`, pick the Wealthink server the plugin registered — it is
listed as **`plugin:wealthink:mcp`** — and choose **Authenticate**. OAuth opens in
your browser; there is no token to copy.

Cowork and claude.ai install it the same way, from **Customize → Plugins**.

## Other agents

Any MCP-capable client — Cursor, VS Code, Codex, OpenCode, ChatGPT custom
connectors — can connect to the Wealthink MCP server directly and use its tools.
Config snippets, and what you give up outside the plugin, are in
[`docs/connect.md`](./docs/connect.md).

Full documentation, skills, agents, and usage examples live in
[`wealthink-plugin/README.md`](./wealthink-plugin/README.md).

## License

MIT — see [LICENSE](./LICENSE).
