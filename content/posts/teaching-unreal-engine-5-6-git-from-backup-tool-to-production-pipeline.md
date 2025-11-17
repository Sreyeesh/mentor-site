---
date: '2025-11-17'
description: A hands-on walkthrough of UEGitWorkshop, a small Unreal Engine 5.6 demo
  project used to teach clean Git + Git LFS + CI/CD workflows for game developers.
  Learn how we set up studio-style branching, automated builds, commit hooks, and
  GitHub Actions checks—training I now offer to studios, schools, and indie teams
  through Toucan Studios (toucan.ee).
excerpt: Learn how to combine Unreal Engine 5.6, Git, and CI/CD into a clean, studio-style
  workflow using the teaching project UEGitWorkshop. In this short recap, I walk through
  how we set up Git LFS, automated builds, enforced Conventional Commits, and used
  GitHub Actions to keep an Unreal project stable and production-ready—skills I now
  teach through Toucan Studios (toucan.ee) for studios, schools, and indie teams.
featured: false
hero_image: null
slug: teaching-unreal-engine-5-6-git-from-backup-tool-to-production-pipeline
title: 'Teaching Unreal Engine 5.6 + Git: From Backup Tool to Production Pipeline'
---

Last week I ran a hands-on lab where we combined **Unreal Engine 5.6**, **Git**, and **CI/CD** to help game developers work more like a studio team and less like a solo dev just “backing up files.”

The session used a small teaching project called **UEGitWorkshop** — an Unreal Engine 5.6 demo built specifically to show **clean, professional Git workflows for game development**.

If you’re building games in Unreal and still feel unsure about Git, branching, or CI, this is exactly the kind of workflow you want in place before your project grows.

📺 **Full workshop video – Unreal Engine 5.6 + Git + CI/CD (UEGitWorkshop):**
[https://www.youtube.com/watch?v=DP2YWmLSV7U](https://www.youtube.com/watch?v=DP2YWmLSV7U)

---

## What We Covered in the Workshop

In about 90 minutes we walked through a complete loop: from cloning the repo to making changes, opening a Pull Request, and letting CI validate everything.

### 1. Setting up a studio-style Unreal repo

We started by looking at how a serious Unreal project should live in Git:

* `.gitattributes` + **Git LFS** for Unreal assets like `.uasset` and `.umap`
* A proper **Unreal `.gitignore`** so `Intermediate`, `Binaries`, autosaves, and DerivedData stay out of the repo
* Shared **editor settings** through `.editorconfig` and `.vscode/settings.json`
* A `.clangd` configuration so **Unreal C++** has working IntelliSense in VS Code

The goal is simple: a repository that is **fast to clone**, **safe to share**, and **easy to maintain** over the lifetime of the game.

### 2. Automating Unreal builds with Python

Instead of right-clicking `.uproject` files and hoping things work, we used a Python script, `build_ue.py`, to:

* Generate Visual Studio project files
* Build the `UEGitWorkshopEditor` target from the command line
* Launch Unreal Engine 5.6 and show a small “Hello World” subsystem running in-game

This is the same pattern you can plug into your **continuous integration** setup later.

### 3. Teaching Git as a workflow, not just a backup

We then focused on Git discipline — the part that really matters in production:

* Configuring **Git LFS** and local Git hooks
* Enforcing **Conventional Commits** via a `commit-msg` hook (no more `stuff_fixed_final_final` commits)
* Creating short-lived `feat/*` branches instead of committing directly to `main`
* Keeping history **linear and readable** so it’s easy to debug and review

Each participant edited a small C++ class, committed with a proper `feat(...)` message, pushed their branch, and opened a Pull Request.

### 4. Using GitHub Actions for Unreal sanity checks

Finally, we looked at **GitHub Actions** and the `unreal-sanity-check.yml` workflow:

* Automatic validation of project structure
* Checks for **asset naming conventions** (e.g. `BP_`, `M_`, `L_` prefixes)
* A downloadable report artifact showing the status of each run

This gives teams a lightweight way to keep their **main branch stable**, even when multiple developers are working on Blueprints, levels, and C++ at the same time.

---

## How Toucan Studios Can Help

I’m **Sreyeesh Garimella**, a technical artist and pipeline engineer. Through my company **Toucan Studios** (🌐 [toucan.ee](https://toucan.ee)), I help:

* **Game studios** design Unreal Engine + Git + CI/CD pipelines that scale
* **Schools and universities** run practical labs like **UEGitWorkshop** for their students
* **Indie and solo developers** structure their Unreal projects so they can safely grow into small teams later

If you’re a **recruiter** looking for someone who can bridge **Unreal Engine, DevOps, and teaching**, or a **team / school** that wants this kind of workflow training for your developers, I’d be happy to chat.

📺 **Watch the full workshop:**
[https://www.youtube.com/watch?v=DP2YWmLSV7U](https://www.youtube.com/watch?v=DP2YWmLSV7U)

🌐 **Learn more:**
[https://toucan.ee](https://toucan.ee)