---
date: '2025-12-16'
description: Pipely 0.1.17 introduces natural language commands, smarter DCC detection
  for Blender, Krita, Godot, Unity, and Unreal, cleaner project management, and Fountain-to-PDF
  exports—making Pipely a creative-first pipeline tool for artists and indie studios.
excerpt: Pipely 0.1.17 is a major step toward an artist-first pipeline. With natural-language
  commands, smarter DCC detection across Blender, Krita, Godot, Unity, and Unreal,
  cleaner project roots, and Fountain-to-PDF exports, Pipely now feels less like a
  CLI and more like a creative assistant.
featured: false
hero_image: null
slug: pipely-0-1-17-when-artists-talk-the-pipeline-listens
title: 'Pipely 0.1.17: When Artists Talk, the Pipeline Listens'
---

I just rolled out **Pipely 0.1.17**, and this is the update where the CLI finally stops feeling like “a tool you operate” and starts feeling like **a creative assistant for artists**. If you’re an indie studio, technical artist, or solo creator juggling folders, versions, and DCCs, this release is about one thing: **reducing friction so you can stay in flow**.

### Natural Language Everywhere (CLI that understands artists)

The interactive prompt now runs on a split brain: **`interactive_commands.py`** handles NLP intent parsing, while **`interactive_ui.py`** renders workspace summaries and artist-friendly menus. The result is a pipeline UX that feels natural: you can type things like **“delete AN_DMO_DemoShort30s,” “work on Forest_BG in krita,”** or **“show recent assets”** and Pipely resolves the right **database records, folders, tasks, and DCC launches** automatically. Less memorizing commands, more getting work done.

### Smarter DCC Detection on Windows + WSL (Blender, Krita, Godot, Unreal, Unity)

Pipely now discovers **Blender, Krita, PureRef, VS Code, Godot, Unity, and Unreal Engine 5.6** automatically across **Windows and WSL**. The launcher searches common install paths (including **`/mnt/<drive>/Program Files/...`**) and **caches results**, so `pipely open --list` reliably shows what’s installed without manual overrides. If you’ve ever lost time fighting PATH issues or launcher configs, this is the kind of “invisible improvement” that adds up fast.

### Cleaner Creative Roots (no more ghost projects)

Deleting a show now removes **both the DB path and any duplicate directories** under your artist root, so the “Projects” picker won’t surface stale entries or “ghost” shows. This behavior is protected by tests, keeping your pipeline clean as your project list grows—especially important for long-running productions where clutter quietly becomes a productivity tax.

### Fountain → PDF (writer-friendly export)

For scriptwriters, Pipely adds a simple workflow:
`pipely workfiles export --file script.fountain`
This generates a polished **PDF screenplay** via **afterwriting** or **screenplain/reportlab**, and the dependencies are installed automatically through the **Ansible playbooks**. That means fewer setup steps, fewer “it works on my machine” moments, and a smoother path from writing to review.

### Quality-of-life fixes that make it feel “tight”

This release also brings practical refinements:

* `pipely open --list` now tolerates **optional DCC names** when listing
* Admin workspace **re-renders summaries** correctly after commands
* Tests now cover **DCC detection**, **interactive parsing**, and **creative-root cleanup**

### Get Pipely 0.1.17

```bash
pipx install https://github.com/Sreyeesh/pipeline-tools/releases/download/v0.1.17/pipely-0.1.17-py3-none-any.whl
pipely
```

**Pipely 0.1.17** makes the pipeline smarter, friendlier, and more aligned with how artists actually think: *type what you want, keep moving, stay creative.* Give it a try—and tell me what you build with it.