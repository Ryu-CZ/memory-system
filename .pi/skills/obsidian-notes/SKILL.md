---
name: obsidian-notes
description: Manage an Obsidian vault from pi using direct Markdown file edits plus the Obsidian CLI when the desktop app is running. Use for creating notes, appending journal entries, searching vault content, and keeping agent/tool-development notes isolated in the pi_sandbox vault.
---

# Obsidian Notes

Use this skill when the user wants work captured in Obsidian instead of loose markdown files.

## Vault for this project

Use this vault by default for sandbox work:

- Vault name: `pi_sandbox`
- Vault path: `/home/trval/vaults/pi_sandbox`

Keep tool experiments, pi skill drafts, and agent scratch notes in this vault so they stay separate from the user's other Obsidian content.

## First choice: direct file editing

When you only need to create or update notes, prefer normal pi file tools against the vault files:

- create notes with `write`
- update notes with `edit`
- inspect notes with `read`
- search notes with `bash` + `rg`

This works even when the Obsidian desktop app is closed.

Common note locations:

- `/home/trval/vaults/pi_sandbox/Inbox/`
- `/home/trval/vaults/pi_sandbox/Projects/`
- `/home/trval/vaults/pi_sandbox/Daily/`
- `/home/trval/vaults/pi_sandbox/References/`

## When to use the Obsidian CLI

Use the `obsidian` CLI when the user specifically wants app-level behavior such as:

- open a note in the GUI
- append to the active daily note
- list vault metadata from the app
- run an Obsidian command or search inside the app

Check that the app is available first:

```bash
command -v obsidian
obsidian vaults verbose
```

If a command fails with:

- `The CLI is unable to find Obsidian. Please make sure Obsidian is running and try again.`

then tell the user the desktop app must be running for that command. Fall back to direct file editing when possible.

## Useful CLI commands

Target the sandbox vault explicitly:

```bash
obsidian vault=pi_sandbox vault info=path
obsidian vault=pi_sandbox files total
obsidian vault=pi_sandbox search query="term"
obsidian vault=pi_sandbox create path="Inbox/New Note.md" content="# New Note"
obsidian vault=pi_sandbox append path="Inbox/New Note.md" content="\nMore text"
obsidian vault=pi_sandbox open path="Inbox/New Note.md"
obsidian vault=pi_sandbox daily:path
obsidian vault=pi_sandbox daily:append content="- captured by pi"
```

## Full linking specification

Every note created or updated with this skill should be written for Obsidian knowledge-graph use, not plain markdown only.

### Core rule

When a note mentions any reusable concept, convert it into an Obsidian reference whenever reasonable.

Prefer these forms:

- `[[Person Name]]` for people and usernames when they identify a person
- `[[Project Name]]` for projects, repos, products, initiatives, games, apps, and codebases
- `[[Concept Name]]` for important concepts, systems, features, workflows, tools, commands, and recurring topics
- `[[Folder/Note Name]]` when disambiguation or exact path matters
- `#keyword` for lightweight tags when a full note would be too heavy
- frontmatter `tags:` for stable categorization

### What to mark as links

Link these by default when they appear in notes:

- user names
- person names
- team names
- project names
- repository names
- product names
- app names
- feature names
- plugin names
- tool names
- important commands
- important keywords
- recurring topics
- technologies
- libraries
- frameworks
- documents and specs

Examples:

- `trval` → `[[trval]]`
- `pi` or `pi agent` → `[[pi]]` or `[[pi agent]]` depending on the note naming convention in the vault
- `obsidian-notes` skill → `[[obsidian-notes]]`
- `pi_sandbox` project or vault → `[[pi_sandbox]]`
- `Obsidian CLI` → `[[Obsidian CLI]]`
- keyword `automation` may stay `#automation` if it does not deserve a full note yet

### Linking behavior rules

- Prefer linking the first meaningful mention in a section.
- Link repeated mentions again only when it improves readability or cross-section scanning.
- Do not overlink every single repeated word in the same paragraph.
- Preserve normal reading flow; links should help, not clutter.
- If the target note does not exist yet, it is still fine to create a wikilink. Obsidian will track it as unresolved.
- If a topic is central to the note, consider creating the target note as well.
- If a name is ambiguous, use a more specific note title such as `[[trval (user)]]` or `[[pi_sandbox (vault)]]`.

### Note naming guidance for links

Use consistent note names so links stay stable:

- People/users: `People/<name>.md` or a simple top-level note name like `trval.md`
- Projects: `Projects/<project-name>/<project-name>.md` or `Projects/<project-name>.md`
- Concepts/tools: `References/<concept>.md` when you decide to create them

When writing markdown text, the visible wikilink may omit folders if the vault can resolve it cleanly:

- file path: `Projects/pi_sandbox/pi_sandbox.md`
- in note text: `[[pi_sandbox]]`

### Required writing pattern

For newly created notes:

1. Add frontmatter with `created` and `tags` when useful.
2. Add a clear H1 title.
3. Convert important entities into wikilinks.
4. Add tags for lightweight indexing.
5. When mentioning people, projects, and concepts together, prefer a mixed structure of wikilinks plus tags.

Example:

```md
---
created: 2026-04-27
tags:
  - pi
  - obsidian
  - automation
---

# [[pi_sandbox]] Obsidian workflow

Discussed with [[trval]] while refining the [[obsidian-notes]] skill for [[pi agent]] usage.

## Related

- [[Obsidian CLI]]
- [[Skills]]
- #knowledge-management
- #tooling
```

## Recommended note patterns

### Scratch capture

Create a new inbox note:

- path: `Inbox/YYYY-MM-DD-topic.md`
- template:

```md
---
created: 2026-04-27
tags:
  - inbox
---

# Topic

## Context

## Notes

## Next steps
```

### Project note

Store project-specific work in `Projects/<project-name>/`.

Suggested sections:

```md
# Project Name

## Goal
## Constraints
## Decisions
## Open questions
## Next actions
```

## Search workflow

For quick search across the vault, use ripgrep on the filesystem first:

```bash
rg -n "query" /home/trval/vaults/pi_sandbox
```

Use the Obsidian CLI search only when the user wants app-aware vault search behavior.

## Structured metadata and properties

Use frontmatter and properties deliberately so notes are filterable and queryable.

Preferred baseline properties:

- `created`
- `updated`
- `tags`
- `status` for project/workflow state
- `type` for note class such as `person`, `project`, `reference`, `daily`, `meeting`, `scratch`
- `project` when a note belongs to a project
- `people` for related people notes
- `source` for URLs, repos, or origin references

When appropriate, set or inspect properties with CLI:

```bash
obsidian vault=pi_sandbox properties
obsidian vault=pi_sandbox property:set path="Projects/pi_sandbox/pi_sandbox.md" name=status value=active type=text
obsidian vault=pi_sandbox property:read path="Projects/pi_sandbox/pi_sandbox.md" name=status
```

Prefer list-like frontmatter values for fields such as `tags`, `people`, and related topics.

## Knowledge-graph maintenance

Do not just create notes. Maintain the graph.

Regularly inspect:

```bash
obsidian vault=pi_sandbox unresolved counts
obsidian vault=pi_sandbox orphans
obsidian vault=pi_sandbox deadends
obsidian vault=pi_sandbox backlinks path="Projects/pi_sandbox/pi_sandbox.md" counts
```

Meaning:

- `unresolved` finds links that should probably get supporting notes
- `orphans` finds notes with no incoming links
- `deadends` finds notes with no outgoing links
- `backlinks` shows where a note is referenced

Maintenance rules:

- if a central note is an orphan, add links to it from related notes or hub notes
- if a note is a dead end, add a `Related` section with outgoing links
- if unresolved links are important, create the missing notes
- for dense topics, create an index or map-of-content note linking subtopics

## Note relationship patterns

Prefer explicit relationship sections near the bottom of important notes:

```md
## Related
- [[Person A]]
- [[Project B]]
- [[Concept C]]

## See also
- [[Adjacent Topic]]
- [[Reference Note]]
```

For major areas, create hub notes such as:

- `Projects/pi_sandbox/pi_sandbox.md`
- `References/Obsidian.md`
- `People/trval.md`

Hub notes should summarize and link out, not duplicate all details.

## Aliases and naming

Use aliases when a note may be referred to in multiple ways.

Examples:

- `pi`
- `pi agent`
- `pi coding agent`
- `Obsidian CLI`
- repository abbreviations

Use frontmatter aliases or inspect them with CLI:

```bash
obsidian vault=pi_sandbox aliases verbose
```

If a note has multiple common names, add aliases rather than creating duplicate notes.

## Task workflow

Use Obsidian tasks inside notes when action items matter.

Pattern:

```md
## Tasks
- [ ] Follow up with [[trval]]
- [ ] Create [[Obsidian CLI]] reference note
- [x] Create [[pi_sandbox]] vault
```

Useful CLI commands:

```bash
obsidian vault=pi_sandbox tasks todo
obsidian vault=pi_sandbox tasks path="Projects/pi_sandbox"
obsidian vault=pi_sandbox task path="Inbox/example.md" line=12 done
obsidian vault=pi_sandbox tasks daily
```

When capturing meeting or project notes, extract clear tasks instead of burying actions in paragraphs.

## Daily note usage

Use daily notes not only as a diary but as an operational inbox.

Recommended daily sections:

```md
# 2026-04-27

## Captured
## In progress
## Decisions
## Tasks
## Links created
```

When appending to the daily note, include links to the people, projects, and notes touched that day.

## Bookmarks and navigation

For frequently revisited notes, searches, or folders, create bookmarks.

Examples:

```bash
obsidian vault=pi_sandbox bookmark folder="Projects"
obsidian vault=pi_sandbox bookmark file="Projects/pi_sandbox/pi_sandbox.md"
obsidian vault=pi_sandbox bookmark search="tag:#pi"
```

Use bookmarks for:

- active project notes
- inbox triage searches
- unresolved-link review
- daily workflow shortcuts

## App-level workflows

When the app is running, use CLI for higher-leverage navigation and maintenance:

```bash
obsidian vault=pi_sandbox recents
obsidian vault=pi_sandbox random:read folder="References"
obsidian vault=pi_sandbox tabs ids
obsidian vault=pi_sandbox workspace ids
obsidian vault=pi_sandbox commands
```

This helps the agent work with the live Obsidian environment, not just raw files.

## Vault conventions to keep

Prefer this folder model:

- `Inbox/` for fast capture
- `Daily/` for day-based logs and operational notes
- `People/` for person notes
- `Projects/` for project hubs and subnotes
- `References/` for evergreen concept and tool notes
- `Archive/` for finished or stale material

Prefer note types:

- scratch note
- daily note
- meeting note
- person note
- project hub
- reference note
- decision note

## Reference maintenance workflow

When updating an existing note:

- scan for unlinked people, projects, and important concepts
- convert them to wikilinks where appropriate
- add missing tags if the note is clearly about recurring themes
- do not rewrite the user's style unnecessarily; just improve linkability

When creating supporting notes for unresolved links, prefer these folders:

- `People/`
- `Projects/`
- `References/`

## Operating checklist

When asked to use Obsidian seriously, follow this checklist:

1. Choose the correct note type and folder.
2. Add frontmatter with useful properties.
3. Write a clear H1 and concise sections.
4. Convert important entities to wikilinks.
5. Add `Related` or `See also` links.
6. Add tasks as checkboxes when actions exist.
7. Add aliases if the note has multiple common names.
8. Review unresolved links, orphans, and dead ends when doing maintenance.
9. Use bookmarks or open notes in the app for active workflows.
10. Keep all sandbox/tooling work in `pi_sandbox`, not `general`.

## Safety

- Do not edit anything in the user's `general` vault unless explicitly asked.
- Default to the `pi_sandbox` vault for experiments.
- Prefer direct markdown edits over GUI automation.
- If you create a new note, put it in a clear folder instead of the vault root unless the user asks otherwise.
