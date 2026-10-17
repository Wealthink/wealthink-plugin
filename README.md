# wealthink-plugin

Understand Indian markets with Wealthink from your AI agent, over MCP.

**Wealthink for agents** reads Wealthink's coherence engine, a connected map of
recent news:
stories linked to their causes and consequences, tagged with the sectors, macro
drivers and companies they move, and their knock-on effects. Ask what's moving
markets, what's happening to a company or sector and why, or whether the news
supports or challenges your view. The agent fills the gaps with its own web
search.

## Install (Claude Code)

```bash
claude plugin marketplace add Wealthink/wealthink-plugin
claude plugin install wealthink@wealthink
```

Restart Claude Code, then connect: run `/mcp`, choose **`plugin:wealthink:mcp`**,
then **Authenticate**.
OAuth opens in your browser; there is no token to copy.

Cowork and claude.ai install it the same way, from **Customize → Plugins**.

## Any other agent

The skills follow the open [Agent Skills](https://agentskills.io) standard, so
any skills-compatible agent can use them: Codex, Cursor, Gemini CLI, OpenCode,
GitHub Copilot, Goose, Amp and more.

```bash
npx skills add Wealthink/wealthink-plugin
```

Then connect the MCP server (`https://api.thewealthink.com/mcp`, OAuth) in that
agent. [`docs/connect.md`](./docs/connect.md) has a snippet for each client.
Or paste the one setup prompt from [`docs/connect.md`](./docs/connect.md) into any agent.
Agents without skills support (e.g. ChatGPT) can use
[`docs/agent-instructions.md`](./docs/agent-instructions.md) as a system prompt.

Skills, tools and usage are documented in
[`wealthink-plugin/README.md`](./wealthink-plugin/README.md).

## License

MIT. See [LICENSE](./LICENSE).
