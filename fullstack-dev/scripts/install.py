#!/usr/bin/env python3
"""Install the fullstack-dev skill into any coding agent (stdlib only).

Skill-folder agents (open SKILL.md format):
  install.py --agent neutral            # .agents/skills/  (read by Codex, Gemini CLI, Copilot, Cursor, others)
  install.py --agent claude             # .claude/skills/
  install.py --agent cursor             # .cursor/skills/
  install.py --agent copilot            # .github/skills/
  install.py --agent gemini             # .gemini/skills/
  install.py --agent claude --agent neutral --scope user    # several, in your home directory
  install.py --dest path/to/skills      # any other skills directory

Agents without skill support (instructions file fallback):
  install.py --rules-file AGENTS.md           # also: GEMINI.md, CONVENTIONS.md, .clinerules, ...
  install.py --cursor-rule                    # .cursor/rules/fullstack-dev.mdc

Options: --link (symlink instead of copy), --dry-run, --uninstall, --project-dir DIR
Conventions move quickly; if an agent ignores the skill, check its docs for its skills path and use --dest.
"""
import argparse
import os
import re
import shutil
import sys

NAME = "fullstack-dev"
SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = {  # agent: (project-relative dir, home-relative dir)
    "neutral": (".agents/skills", ".agents/skills"),
    "claude": (".claude/skills", ".claude/skills"),
    "cursor": (".cursor/skills", ".cursor/skills"),
    "copilot": (".github/skills", ".copilot/skills"),
    "gemini": (".gemini/skills", ".gemini/skills"),
}
BEGIN, END = f"<!-- {NAME}:begin -->", f"<!-- {NAME}:end -->"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".git", ".DS_Store")


def is_ours(path):
    f = os.path.join(path, "SKILL.md")
    if not os.path.isfile(f):
        return False
    head = open(f, encoding="utf-8", errors="ignore").read(600)
    return re.search(rf"^name:\s*{re.escape(NAME)}\s*$", head, re.M) is not None


def remove(path, dry):
    if os.path.lexists(path):
        if os.path.islink(path):
            print(f"remove link {path}")
            if not dry:
                os.unlink(path)
        elif is_ours(path):
            print(f"remove {path}")
            if not dry:
                shutil.rmtree(path)
        else:
            sys.exit(f"refusing to touch {path}: not a {NAME} skill directory")


def install_dir(dest_root, link, dry):
    dest = os.path.join(dest_root, NAME)
    if os.path.abspath(dest) == SRC:
        print(f"already at {dest}")
        return dest
    remove(dest, dry)
    print(f"{'link' if link else 'copy'} {SRC} -> {dest}")
    if not dry:
        os.makedirs(dest_root, exist_ok=True)
        if link:
            try:
                os.symlink(SRC, dest, target_is_directory=True)
                return dest
            except OSError as e:
                print(f"symlink failed ({e}); copying instead")
        shutil.copytree(SRC, dest, ignore=IGNORE)
    return dest


def snippet(skill_path):
    text = open(os.path.join(SRC, "adapters", "rules-snippet.md"), encoding="utf-8").read()
    return text.replace("{SKILL_PATH}", skill_path.replace("\\", "/")).strip()


def update_block(path, block, dry, remove_only=False):
    cur = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    pat = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
    cur = pat.sub("", cur).rstrip("\n")
    new = cur if remove_only else (cur + "\n\n" if cur else "") + f"{BEGIN}\n{block}\n{END}"
    print(f"{'remove block from' if remove_only else 'write block to'} {path}")
    if not dry:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        if remove_only and not new.strip():
            if os.path.exists(path):
                os.unlink(path)
        else:
            open(path, "w", encoding="utf-8").write(new + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--agent", action="append", choices=sorted(TARGETS), default=[])
    p.add_argument("--scope", choices=["project", "user"], default="project")
    p.add_argument("--dest", action="append", default=[], help="custom skills directory")
    p.add_argument("--rules-file", help="append an instructions block to this file (AGENTS.md, GEMINI.md, ...)")
    p.add_argument("--cursor-rule", action="store_true", help="write .cursor/rules/fullstack-dev.mdc")
    p.add_argument("--project-dir", default=os.getcwd())
    p.add_argument("--link", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--uninstall", action="store_true")
    a = p.parse_args()

    proj, home = os.path.abspath(a.project_dir), os.path.expanduser("~")
    roots = []
    for ag in a.agent:
        rel_p, rel_h = TARGETS[ag]
        roots.append(os.path.join(proj, rel_p) if a.scope == "project" else os.path.join(home, rel_h))
    roots += [os.path.abspath(d) for d in a.dest]
    needs_files = bool(a.rules_file or a.cursor_rule)
    if needs_files and not roots:  # rules point at a skill copy, so make sure one exists
        roots.append(os.path.join(proj, TARGETS["neutral"][0]))
    if not roots and not needs_files:
        p.error("choose --agent, --dest, --rules-file or --cursor-rule (see --help)")

    installed = []
    for r in roots:
        if a.uninstall:
            remove(os.path.join(r, NAME), a.dry_run)
        else:
            installed.append(install_dir(r, a.link, a.dry_run))
    ref = installed[0] if installed else os.path.join(roots[0], NAME)
    rel = os.path.relpath(ref, proj) if ref.startswith(proj) else ref

    if a.rules_file:
        path = a.rules_file if os.path.isabs(a.rules_file) else os.path.join(proj, a.rules_file)
        update_block(path, snippet(rel), a.dry_run, remove_only=a.uninstall)
    if a.cursor_rule:
        mdc = os.path.join(proj, ".cursor", "rules", f"{NAME}.mdc")
        if a.uninstall:
            print(f"remove {mdc}")
            if not a.dry_run and os.path.exists(mdc):
                os.unlink(mdc)
        else:
            print(f"write {mdc}")
            if not a.dry_run:
                os.makedirs(os.path.dirname(mdc), exist_ok=True)
                fm = ("---\ndescription: Full stack development workflow (DB, API, frontend, tests, security, "
                      "performance). Use when building or reviewing a full stack app for a given tech stack.\n"
                      "alwaysApply: false\n---\n\n")
                open(mdc, "w", encoding="utf-8").write(fm + snippet(rel) + "\n")
    print("done" + (" (dry run)" if a.dry_run else ""))


if __name__ == "__main__":
    main()
