# Awesome Skills

Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. This marketplace provides battle-tested skills for startup founders and technical teams building with AI agents.

For more information about Skills, check out:
- [What are Skills?](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Using Skills in Claude](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [How to create custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

## About This Repository

This repository contains production-ready skills designed for entrepreneurs and software architects. Whether you're validating a startup idea, crafting a comprehensive business plan, or designing scalable Python architectures, these skills provide repeatable workflows that extend Claude's capabilities.

**Note:** These skills represent real-world expertise distilled into reusable agent capabilities. They're designed for practical application in startup creation and software development workflows.

---

## Available Skills

This repository includes skills organized into two main categories:

### Startup Advisor

**business-plan-advisor**  
Creates comprehensive, investor-ready business plans following proven frameworks. Guides you through market analysis, competitive positioning, financial projections, go-to-market strategy, and risk assessment. Perfect for founders preparing pitch decks or validating business models.

**mvp-validator**  
Validates minimum viable product concepts using lean startup methodology. Analyzes product-market fit, identifies core features vs. nice-to-haves, estimates development complexity, and provides actionable go-to-market recommendations. Essential for de-risking product launches.

### Technical Roles

**python-architect**  
Designs production-ready Python architectures following enterprise best practices. Covers system design patterns, scalability considerations, testing strategies, dependency management, and deployment architectures. Ideal for technical leads planning robust backend systems.

---

## Try in Claude Code, Claude.ai, and the API

### Claude Code

You can register this repository as a Claude Code Plugin marketplace by running the following command in Claude Code:

```
/plugin marketplace add yourusername/awesome-skills
```

Then, to install a specific set of skills:

1. Select `Browse and install plugins`
2. Select `awesome-skills`
3. Select `startup-advisor` or `technical-roles`
4. Select `Install now`

Alternatively, directly install either plugin via:

```
/plugin install startup-advisor@awesome-skills
/plugin install technical-roles@awesome-skills
```

After installing the plugin, you can use the skills by mentioning them. For instance: "Use the business-plan-advisor skill to create a plan for my SaaS idea" or "Help me architect a Python microservices system using the python-architect skill."

### Claude.ai

To use any skill from this repository in Claude.ai, follow the instructions in [Using Skills in Claude](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

You can upload these skills directly to your Claude.ai Projects or use them through the API.

### Claude API

You can upload and use these custom skills via the Claude API. See the [Skills API Quickstart](https://docs.anthropic.com/en/docs/claude-code/skills) for integration details.

### Other Agent Frameworks

no other agent framework currently supports skills

---

## Contributing

We welcome contributions! To add a new skill:

1. Fork this repository
2. Create a new folder for your skill
3. Add a `SKILL.md` file with proper frontmatter and instructions
4. Update the appropriate plugin section in `.claude-plugin/marketplace.json`
5. Submit a pull request with a clear description of your skill

Please ensure your skills follow these guidelines:
- Clear, actionable instructions
- Real-world applicability
- Proper documentation and examples
- Compatible with the skills-use framework

---

## Community & Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/maxvaega/awesome-skills/issues)
- **Discussions**: Share use cases and improvements in [GitHub Discussions](https://github.com/maxvaega/awesome-skills/discussions)
- **Framework**: Learn more about the underlying [skills-use framework](https://github.com/maxvaega/skills-use)

---

## About

Skills marketplace for LLM agents focused on startup creation and technical excellence.

**License:** Apache 2.0  
**Maintainer:** Massimo Olivieri (olivmassimo@gmail.com)

---

**Star this repo** if you find these skills useful! ⭐
