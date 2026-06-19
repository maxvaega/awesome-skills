<div align="center">
<h1 align="center" style="font-size:4em">🚀 awesome-skills</h1>
</div>
<p align="center" style="max-width:80%; margin-bottom:40px">Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. This marketplace provides battle-tested skills for startup founders and technical teams building with AI agents. Think of them as superpowers for your AI! ⚡</p>

<p align="center">
<a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" /></a>
<a href="https://github.com/maxvaega/awesome-skills/stargazers">
    <img src="https://img.shields.io/github/stars/maxvaega/awesome-skills" /></a>
</p>

---

For more information about Skills, check out the following links 🔗:
- [What are Skills?](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Using Skills in Claude](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [How to create custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

## 📚 About This Repository

This repository contains production-ready skills designed for entrepreneurs and software architects. Whether you're validating a startup idea, crafting a comprehensive business plan, or designing scalable Python architectures, these skills provide repeatable workflows that extend Claude's capabilities.

**Note:** These skills represent real-world expertise distilled into reusable agent capabilities. They're designed for practical application in startup creation and software development workflows. (No fluff, just the good stuff! ✨)

---

## 💎 Available Skills

This repository includes skills organized into two main categories:

### 🧠 Agent Self-Improvement

#### 🧠 **dream**
A self-improving memory loop for Claude Code. Capture your preferences, corrections, and standing rules as project-level memories (`/dream`), consolidate them periodically with a "REM sleep" pass that merges, verifies, and decays old memories (`/dream rem`), and let it propose improvements to your skills and CLAUDE.md that you approve before anything changes (`/dream proposals`). Optional fully-automated mode via SessionEnd hook + nightly cron (`/dream setup`). Inspired by the Hermes Agent reflection/curator architecture, built on plain markdown + hooks + cron. Your AI, your rules — and it gets better while you sleep! 🎯

### 💰 Cost & Usage

#### 💰 **cost**
Estimate what your **Claude Cowork / Claude Code** conversations would cost if run on the **pay-per-token Claude API** instead of the subscription. It reads the JSONL transcripts under `~/.claude/projects/`, sums the **actual** token usage (cache-aware), and prices it at Anthropic list rates — reporting token counts and cost in **USD and EUR** for the current conversation or your whole history (`/cost`). A faithful replay cost, not a guess — perfect for comparing subscription vs API pricing! 💸

### 🚀 Startup Advisor

#### 📋 **business-plan-advisor**
Expert business planning consultant for creating comprehensive, investor-ready business plans from scratch or refining existing plans.
Applies to startups and established businesses across all industries seeking funding or strategic planning.

#### ✅ **mvp-validator**
Review startup MVPs for realism, agility, and business viability. This skill conducts critical but objective analysis of MVP ideas, requirements, and implementation plans, identifying strengths and pain points to provide constructive feedback. Get honest feedback without the sugar-coating! 🍬➡️💯

#### 🔥 **reddit-social-media-strategist**
This skill transforms users into effective Reddit marketers by providing actionable strategies for content creation, community engagement, and sustainable growth.
It covers everything from identifying the right subreddits and optimizing post titles, to timing strategies and first-hour engagement tactics that maximize visibility.

#### 🎤 **elevator-pitch-advisor**
Expert elevator pitch consultant for creating compelling, concise 30-60 second introductions tailored to specific audiences and contexts. This skill should be used when users need to craft elevator pitches for job interviews, networking events, investor meetings, or social media profiles. Guides users through structured discovery, applies proven frameworks (Three C's, Four-Part Structure), integrates storytelling techniques, and delivers multiple pitch versions with industry-specific hooks and closing lines.

### 🏗️ Technical Roles

#### 🐍 **python-architect**
Specialized skill for designing, architecting, and reviewing production-grade Python libraries. Guide library structure, API design, testing strategies, and implementation. Build Python like you mean it! 💪

#### 📊 **app-analytics-strategist**
Expert data analytics consultant for designing and implementing data-driven growth strategies for mobile and digital applications. Provides comprehensive guidance on analytics frameworks (descriptive, diagnostic, predictive, prescriptive), North Star metrics, cohort analysis, user segmentation, A/B testing, customer journey mapping, and retention optimization. Applies to product managers, growth teams, and developers building data-driven applications across all platforms seeking to optimize user engagement, retention, and revenue through analytics. Turn data into decisions! 📈

### 🔮 ... and more yet to come!

---

## 🔗 Compatible Agent Platforms

### 💻 Claude Code

You can register this repository as a Claude Code Plugin marketplace by running the following command in Claude Code:

```
/plugin marketplace add maxvaega/awesome-skills
```

Then, to install a specific set of skills:

1. Select `Browse and install plugins`
2. Select `awesome-skills`
3. Select a plugin (`cost`, `startup-advisor`, `technical-roles`, or `developer-productivity`)
4. Select `Install now`

After installing the plugin, you can use the skills by mentioning them. For instance: "Use the business-plan-advisor skill to create a plan for my SaaS idea" or "Help me architect a Python microservices system using the python-architect skill."

### 🌐 Claude.ai

To use any skill from this repository in Claude.ai, follow the instructions in [Using Skills in Claude](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

You can upload these skills directly to your Claude.ai Projects or use them through the API.

### ⚙️ Claude API

You can upload and use these custom skills via the Claude API. See the [Skills API Quickstart](https://docs.anthropic.com/en/docs/claude-code/skills) for integration details. Integrate with confidence! 🎯

### 🤝 Other Agent Frameworks

Not yet—but we're keeping an eye on the horizon! 👀

---

## 🤲 Contributing

We welcome contributions! To add a new skill:

1. Fork this repository
2. Create a new folder for your skill
3. Add a `SKILL.md` file with proper frontmatter and instructions
4. Update the appropriate plugin section in `.claude-plugin/marketplace.json`
5. Submit a pull request with a clear description of your skill

Please ensure your skills follow these guidelines:
- Clear, actionable instructions ✍️
- Real-world applicability 💼
- Proper documentation and examples 📖
- Compatible with the skills-use framework 🔧

---

## 💬 Community & Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/maxvaega/awesome-skills/issues) 🐛
- **Discussions**: Share use cases and improvements in [GitHub Discussions](https://github.com/maxvaega/awesome-skills/discussions) 💭
- **Framework**: Learn more about the underlying [skills-use framework](https://github.com/maxvaega/skills-use) 🔨

---

## 🎯 About

Skills marketplace for LLM agents focused on startup creation and technical excellence. Built for founders and architects who demand the best. 🏆

**Maintainer:** Massimo Olivieri (maxvaega)

---

**Star this repo** if you find these skills useful! ⭐ (Your stars fuel our superpowers! 💫)
