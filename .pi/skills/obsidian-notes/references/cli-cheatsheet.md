# Obsidian CLI cheatsheet

Default sandbox vault:

- name: `pi_sandbox`
- path: `/home/trval/vaults/pi_sandbox`

## Availability checks

```bash
command -v obsidian
obsidian vaults verbose
```

## Vault info

```bash
obsidian vault=pi_sandbox vault
obsidian vault=pi_sandbox vault info=path
obsidian vault=pi_sandbox folders
obsidian vault=pi_sandbox files total
```

## Notes

```bash
obsidian vault=pi_sandbox create path="Inbox/Test.md" content="# Test"
obsidian vault=pi_sandbox append path="Inbox/Test.md" content="\nhello"
obsidian vault=pi_sandbox open path="Inbox/Test.md"
obsidian vault=pi_sandbox read path="Inbox/Test.md"
obsidian vault=pi_sandbox move path="Inbox/Test.md" to="Projects/Test.md"
```

## Daily note

```bash
obsidian vault=pi_sandbox daily:path
obsidian vault=pi_sandbox daily:read
obsidian vault=pi_sandbox daily:append content="- note"
```

## Search

```bash
obsidian vault=pi_sandbox search query="pi agent"
rg -n "pi agent" /home/trval/vaults/pi_sandbox
```

## Graph maintenance

```bash
obsidian vault=pi_sandbox backlinks path="Projects/pi_sandbox/pi_sandbox.md" counts
obsidian vault=pi_sandbox unresolved counts
obsidian vault=pi_sandbox orphans
obsidian vault=pi_sandbox deadends
```

## Properties

```bash
obsidian vault=pi_sandbox properties
obsidian vault=pi_sandbox property:set path="Inbox/Test.md" name=type value=scratch type=text
obsidian vault=pi_sandbox property:read path="Inbox/Test.md" name=type
```

## Tasks

```bash
obsidian vault=pi_sandbox tasks todo
obsidian vault=pi_sandbox tasks daily
obsidian vault=pi_sandbox task path="Inbox/Test.md" line=5 done
```

## Bookmarks and navigation

```bash
obsidian vault=pi_sandbox bookmark file="Projects/pi_sandbox/pi_sandbox.md"
obsidian vault=pi_sandbox recents
obsidian vault=pi_sandbox random:read folder="References"
obsidian vault=pi_sandbox tabs ids
```

## Linking reminder

When writing notes for this vault, mark important references as Obsidian links:

- people and usernames as `[[Name]]`
- projects and repos as `[[Project]]`
- tools, skills, and concepts as `[[Concept]]`
- lightweight recurring themes as `#tags`

Example:

```md
Worked with [[trval]] on [[pi_sandbox]] using [[obsidian-notes]] and [[Obsidian CLI]].
```

## Reminder

Many CLI actions require the Obsidian desktop app to be running.
