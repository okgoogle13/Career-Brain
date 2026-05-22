#!/usr/bin/env python3
"""
query_brain.py — Career Brain Local Query Interface
====================================================
Interactive CLI to query your Career Brain JSON engines without
opening files manually. Ideal for interview prep, cover letter
drafting, and KSC targeting.

Usage:
  python3 query_brain.py             # interactive mode
  python3 query_brain.py --help      # show commands

Requires: pip install rich
"""

import sys
import json
import re
from pathlib import Path
from difflib import get_close_matches

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    from rich.prompt import Prompt
    from rich.columns import Columns
    from rich.markdown import Markdown
    RICH = True
except ImportError:
    RICH = False

BASE   = Path(__file__).parent
OUTPUT = BASE / "output"

console = Console() if RICH else None

# ─── Loader ───────────────────────────────────────────────────────────────────

def load_json(filename: str) -> dict:
    path = OUTPUT / filename
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all():
    # Prefer enriched / curated versions if available
    history_file = "career_history_enriched.json" if (OUTPUT / "career_history_enriched.json").exists() else "career_history.json"
    narratives_file = "ksc_curated.json" if (OUTPUT / "ksc_curated.json").exists() else "ksc_and_narratives.json"

    history   = load_json(history_file)
    narratives = load_json(narratives_file)
    taxonomy  = load_json("skills_and_taxonomy.json")
    return history, narratives, taxonomy


# ─── Printing helpers ─────────────────────────────────────────────────────────

def print_header(title: str):
    if RICH:
        console.rule(f"[bold cyan]{title}[/bold cyan]")
    else:
        print(f"\n{'='*60}\n{title}\n{'='*60}")


def print_bullet(bullet: dict, index: int = None, show_meta: bool = True):
    text = bullet.get("raw_text", "")
    tags = bullet.get("domain_tags", [])
    review = bullet.get("needs_review", False)
    tier_icon = "🔴" if review else "✅"

    if RICH:
        label = f"[dim]{index}.[/dim] " if index else ""
        flag  = " [yellow][NEEDS METRIC][/yellow]" if review else ""
        console.print(f"  {label}[white]{text}[/white]{flag}")
        if show_meta and tags:
            console.print(f"     [dim]Tags: {', '.join(tags)}[/dim]")
    else:
        prefix = f"{index}. " if index else "  "
        flag   = " [NEEDS METRIC]" if review else ""
        print(f"{prefix}{text}{flag}")
        if show_meta and tags:
            print(f"   Tags: {', '.join(tags)}")


def print_narrative(n: dict, index: int = None, full: bool = False):
    ntype     = n.get("narrative_type", "?")
    comp_tags = n.get("competency_tags", [])
    text      = n.get("full_text", "")
    tier      = n.get("quality_tier", "?")
    wc        = n.get("word_count", 0)
    source    = n.get("source_lineage", "")

    if RICH:
        tier_colour = {"1": "green", "2": "yellow", "3": "red"}.get(str(tier), "white")
        label = f"[dim]{index}.[/dim] " if index else "  "
        console.print(f"\n{label}[bold {tier_colour}][{ntype.upper()} | T{tier} | {wc}w][/bold {tier_colour}]  [dim]{source[:50]}[/dim]")
        if comp_tags:
            console.print(f"     [dim]Competencies: {', '.join(comp_tags)}[/dim]")
        if full:
            console.print(Panel(text, border_style="dim"))
        else:
            preview = text[:200] + ("..." if len(text) > 200 else "")
            console.print(f"  [italic]{preview}[/italic]")
    else:
        label = f"{index}. " if index else "  "
        print(f"\n{label}[{ntype.upper()} | Tier {tier} | {wc}w]")
        if comp_tags:
            print(f"   Competencies: {', '.join(comp_tags)}")
        if full:
            print(text)
        else:
            print(f"  {text[:200]}...")


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_help():
    commands = [
        ("role <company>",         "Show all roles & bullets for an employer"),
        ("bullets <tag>",          "Filter bullets by domain tag"),
        ("star <competency>",      "Retrieve top STAR narratives for a competency"),
        ("pivot",                  "List all pivot/transition narratives"),
        ("hooks",                  "List all hook/intro narratives"),
        ("skills",                 "Show full skills inventory"),
        ("rosetta",                "Show all Rosetta Stone mappings"),
        ("review",                 "List all bullets flagged needs_review"),
        ("companies",              "List all employers in the database"),
        ("tags",                   "List all available domain tags"),
        ("competencies",           "List all competency tags with counts"),
        ("show <N>",               "Show full text of narrative #N from last result"),
        ("export <query> <file>",  "Export last result to .md file"),
        ("stats",                  "Show database statistics"),
        ("quit / exit",            "Exit the CLI"),
    ]
    if RICH:
        table = Table(title="Career Brain Query Commands", box=box.ROUNDED, border_style="cyan")
        table.add_column("Command", style="bold yellow", no_wrap=True)
        table.add_column("Description", style="white")
        for cmd, desc in commands:
            table.add_row(cmd, desc)
        console.print(table)
    else:
        print("\nAvailable commands:")
        for cmd, desc in commands:
            print(f"  {cmd:<30} {desc}")


def cmd_stats(history, narratives, taxonomy):
    roles          = history.get("roles", [])
    total_bullets  = sum(len(r.get("achievements", [])) for r in roles)
    review_bullets = sum(1 for r in roles for b in r.get("achievements", []) if b.get("needs_review"))
    all_narratives = narratives.get("narratives", [])
    tier_counts    = {}
    for n in all_narratives:
        t = str(n.get("quality_tier", "?"))
        tier_counts[t] = tier_counts.get(t, 0) + 1
    rosetta = taxonomy.get("rosetta_stone", {})
    skills  = taxonomy.get("skills_inventory", [])

    if RICH:
        console.print(Panel(
            f"[bold]Career History:[/bold]  {len(roles)} roles  |  {total_bullets} bullets  |  {review_bullets} needs metric\n"
            f"[bold]Narratives:[/bold]       {len(all_narratives)} total  |  "
            f"T1: [green]{tier_counts.get('1',0)}[/green]  T2: [yellow]{tier_counts.get('2',0)}[/yellow]  T3: [red]{tier_counts.get('3',0)}[/red]\n"
            f"[bold]Rosetta Stone:[/bold]    {len(rosetta)} mappings\n"
            f"[bold]Skills:[/bold]           {len(skills)} extracted",
            title="Database Statistics", border_style="cyan"
        ))
    else:
        print(f"\nRoles: {len(roles)}  |  Bullets: {total_bullets}  |  Needs review: {review_bullets}")
        print(f"Narratives: {len(all_narratives)}  T1:{tier_counts.get('1',0)} T2:{tier_counts.get('2',0)} T3:{tier_counts.get('3',0)}")
        print(f"Rosetta mappings: {len(rosetta)}  |  Skills: {len(skills)}")


def cmd_companies(history):
    roles = history.get("roles", [])
    by_company = {}
    for r in roles:
        co = r.get("company", "Unknown")
        by_company[co] = by_company.get(co, 0) + len(r.get("achievements", []))

    if RICH:
        table = Table(title="Employers in Database", box=box.SIMPLE, border_style="dim")
        table.add_column("Employer", style="bold white")
        table.add_column("Bullets", style="cyan", justify="right")
        for co, count in sorted(by_company.items(), key=lambda x: -x[1]):
            table.add_row(co, str(count))
        console.print(table)
    else:
        for co, count in sorted(by_company.items(), key=lambda x: -x[1]):
            print(f"  {co:<40} {count} bullets")


def cmd_role(history, query: str) -> list:
    query_lower = query.lower()
    roles = history.get("roles", [])
    matched = [r for r in roles if query_lower in r.get("company", "").lower()
               or query_lower in r.get("role", "").lower()]

    if not matched:
        # Fuzzy match on company names
        companies = [r.get("company", "") for r in roles]
        close = get_close_matches(query, companies, n=3, cutoff=0.4)
        if close:
            if RICH:
                console.print(f"[yellow]No exact match. Did you mean: {', '.join(close)}?[/yellow]")
            else:
                print(f"No exact match. Did you mean: {', '.join(close)}?")
        return []

    total = 0
    for role in matched:
        company = role.get("company", "")
        role_title = role.get("role", "")
        start = role.get("start_date", "")
        end   = role.get("end_date", "")
        bullets = role.get("achievements", [])

        print_header(f"{company} | {role_title} | {start} – {end}")
        for i, b in enumerate(bullets, 1):
            print_bullet(b, index=i)
            total += 1

    if RICH:
        console.print(f"\n[dim]{total} bullets across {len(matched)} role(s)[/dim]")
    return matched


def cmd_bullets_by_tag(history, tag: str) -> list:
    tag_lower = tag.lower()
    results = []
    for role in history.get("roles", []):
        company = role.get("company", "")
        for b in role.get("achievements", []):
            if any(tag_lower in t.lower() for t in b.get("domain_tags", [])):
                results.append((company, b))

    print_header(f"Bullets tagged: {tag} ({len(results)} results)")
    for i, (company, b) in enumerate(results, 1):
        if RICH:
            console.print(f"  [dim]{i}.[/dim] [bold cyan]{company}[/bold cyan]")
        else:
            print(f"  {i}. [{company}]")
        print_bullet(b, show_meta=False)

    return results


def cmd_star(narratives, competency: str, max_results: int = 10) -> list:
    comp_lower = competency.lower()
    all_narratives = narratives.get("narratives", [])

    matched = [
        n for n in all_narratives
        if any(comp_lower in tag.lower() for tag in n.get("competency_tags", []))
        and n.get("narrative_type") in ("STAR", "statement", "pivot", "hook")
    ]

    # Sort by quality tier then word count
    matched.sort(key=lambda n: (n.get("quality_tier", 9), -n.get("word_count", 0)))
    top = matched[:max_results]

    print_header(f"STAR Narratives: {competency} (top {len(top)} of {len(matched)} matched)")
    for i, n in enumerate(top, 1):
        print_narrative(n, index=i)

    return top


def cmd_pivot(narratives, max_results: int = 20) -> list:
    all_narratives = narratives.get("narratives", [])
    pivot = [n for n in all_narratives if n.get("narrative_type") == "pivot"]
    pivot.sort(key=lambda n: (n.get("quality_tier", 9), -n.get("word_count", 0)))
    top = pivot[:max_results]

    print_header(f"Pivot/Transition Narratives (top {len(top)} of {len(pivot)})")
    for i, n in enumerate(top, 1):
        print_narrative(n, index=i)

    return top


def cmd_hooks(narratives, max_results: int = 20) -> list:
    all_narratives = narratives.get("narratives", [])
    hooks = [n for n in all_narratives if n.get("narrative_type") == "hook"]
    hooks.sort(key=lambda n: (n.get("quality_tier", 9), -n.get("word_count", 0)))
    top = hooks[:max_results]

    print_header(f"Hook / Intro Narratives (top {len(top)} of {len(hooks)})")
    for i, n in enumerate(top, 1):
        print_narrative(n, index=i)

    return top


def cmd_review(history) -> list:
    results = []
    for role in history.get("roles", []):
        for b in role.get("achievements", []):
            if b.get("needs_review", False):
                results.append((role.get("company", ""), b))

    print_header(f"Bullets Needing Metric Injection ({len(results)} remaining)")
    for i, (company, b) in enumerate(results, 1):
        if RICH:
            console.print(f"  [dim]{i}.[/dim] [bold yellow]{company}[/bold yellow]")
        else:
            print(f"  {i}. [{company}]")
        print_bullet(b, show_meta=True)

    return results


def cmd_rosetta(taxonomy):
    rosetta = taxonomy.get("rosetta_stone", {})
    print_header(f"Rosetta Stone Mappings ({len(rosetta)})")

    for key, mapping in rosetta.items():
        corporate  = mapping.get("corporate_framing", "")[:100]
        community  = mapping.get("community_translation", "")
        keywords   = mapping.get("community_keywords", [])
        bridge     = mapping.get("contextual_bridge", "")[:200]

        if RICH:
            console.print(f"\n[bold cyan]{key}[/bold cyan]")
            console.print(f"  [dim]Corporate:[/dim]  {corporate}...")
            console.print(f"  [bold green]Community:[/bold green] {community}")
            console.print(f"  [dim]Keywords:[/dim]   {', '.join(keywords[:5])}")
            console.print(f"  [italic dim]{bridge}...[/italic dim]")
        else:
            print(f"\n{key}")
            print(f"  → {community}")
            print(f"  Keywords: {', '.join(keywords[:5])}")


def cmd_skills(taxonomy):
    skills = taxonomy.get("skills_inventory", [])
    print_header(f"Skills Inventory ({len(skills)})")

    if RICH:
        table = Table(box=box.SIMPLE, border_style="dim")
        table.add_column("Skill", style="bold white")
        table.add_column("Level", style="cyan")
        table.add_column("Sources", style="dim", justify="right")
        for s in skills:
            table.add_row(
                s.get("skill_name", ""),
                s.get("skill_level") or "—",
                str(len(s.get("source_lineage", [])))
            )
        console.print(table)
    else:
        for s in skills:
            print(f"  {s.get('skill_name'):<40} Sources: {len(s.get('source_lineage', []))}")


def cmd_tags(history):
    tag_counts = {}
    for role in history.get("roles", []):
        for b in role.get("achievements", []):
            for tag in b.get("domain_tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print_header("Available Domain Tags")
    if RICH:
        table = Table(box=box.SIMPLE, border_style="dim")
        table.add_column("Tag", style="bold cyan")
        table.add_column("Bullet Count", style="white", justify="right")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            table.add_row(tag, str(count))
        console.print(table)
    else:
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"  {tag:<35} {count}")


def cmd_competencies(narratives):
    comp_counts = {}
    for n in narratives.get("narratives", []):
        for tag in n.get("competency_tags", []):
            comp_counts[tag] = comp_counts.get(tag, 0) + 1

    print_header("Competency Tags (narrative counts)")
    if RICH:
        table = Table(box=box.SIMPLE, border_style="dim")
        table.add_column("Competency", style="bold cyan")
        table.add_column("Narratives", style="white", justify="right")
        for tag, count in sorted(comp_counts.items(), key=lambda x: -x[1]):
            table.add_row(tag, str(count))
        console.print(table)
    else:
        for tag, count in sorted(comp_counts.items(), key=lambda x: -x[1]):
            print(f"  {tag:<35} {count}")


def cmd_show(last_results: list, index: int):
    if not last_results:
        print("No previous results. Run a query first.")
        return
    if index < 1 or index > len(last_results):
        print(f"Index out of range. Results: 1–{len(last_results)}")
        return
    item = last_results[index - 1]
    if isinstance(item, dict) and "full_text" in item:
        print_narrative(item, full=True)
    elif isinstance(item, tuple) and len(item) == 2:
        # (company, bullet) tuple
        company, b = item
        if RICH:
            console.print(f"\n[bold cyan]{company}[/bold cyan]")
        print_bullet(b, show_meta=True)


def cmd_export(last_results: list, filename: str):
    if not last_results:
        print("No results to export.")
        return
    path = BASE / filename
    lines = [f"# Career Brain Export\n\nExported: {__import__('datetime').datetime.now().isoformat()}\n\n---\n"]
    for i, item in enumerate(last_results, 1):
        if isinstance(item, dict) and "full_text" in item:
            ntype = item.get("narrative_type", "")
            comp  = ", ".join(item.get("competency_tags", []))
            lines.append(f"## {i}. {ntype.upper()} | {comp}\n\n{item['full_text']}\n\n---\n")
        elif isinstance(item, tuple):
            company, b = item
            lines.append(f"## {i}. [{company}]\n\n{b.get('raw_text', '')}\n\n---\n")
        elif isinstance(item, dict) and "achievements" in item:
            lines.append(f"## {i}. {item.get('company')} — {item.get('role')}\n")
            for b in item["achievements"]:
                lines.append(f"- {b.get('raw_text','')}\n")
            lines.append("\n---\n")

    path.write_text("\n".join(lines), encoding="utf-8")
    if RICH:
        console.print(f"[green]Exported {len(last_results)} results to {path}[/green]")
    else:
        print(f"Exported to {path}")


# ─── REPL ─────────────────────────────────────────────────────────────────────

def run_repl():
    history, narratives, taxonomy = load_all()

    if RICH:
        console.print(Panel(
            "[bold cyan]Career Brain[/bold cyan] — Local Query Interface\n"
            "[dim]Type [bold]help[/bold] for commands, [bold]quit[/bold] to exit[/dim]",
            border_style="cyan"
        ))
    else:
        print("\nCareer Brain Query Interface")
        print("Type 'help' for commands, 'quit' to exit\n")

    cmd_stats(history, narratives, taxonomy)

    last_results = []

    while True:
        try:
            if RICH:
                raw = Prompt.ask("\n[bold cyan]brain>[/bold cyan]").strip()
            else:
                raw = input("\nbrain> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not raw:
            continue

        parts = raw.split(None, 1)
        cmd   = parts[0].lower()
        args  = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit", "q"):
            if RICH:
                console.print("[dim]Bye![/dim]")
            else:
                print("Bye!")
            break
        elif cmd == "help":
            cmd_help()
        elif cmd == "stats":
            cmd_stats(history, narratives, taxonomy)
        elif cmd == "companies":
            cmd_companies(history)
        elif cmd == "role":
            if not args:
                print("Usage: role <company name>")
            else:
                last_results = cmd_role(history, args)
        elif cmd == "bullets":
            if not args:
                print("Usage: bullets <tag>  (e.g. bullets harm_reduction)")
            else:
                last_results = cmd_bullets_by_tag(history, args)
        elif cmd == "star":
            if not args:
                print("Usage: star <competency>  (e.g. star leadership)")
            else:
                last_results = cmd_star(narratives, args)
        elif cmd == "pivot":
            last_results = cmd_pivot(narratives)
        elif cmd == "hooks":
            last_results = cmd_hooks(narratives)
        elif cmd == "review":
            last_results = cmd_review(history)
        elif cmd == "rosetta":
            cmd_rosetta(taxonomy)
        elif cmd == "skills":
            cmd_skills(taxonomy)
        elif cmd == "tags":
            cmd_tags(history)
        elif cmd == "competencies":
            cmd_competencies(narratives)
        elif cmd == "show":
            try:
                idx = int(args)
                cmd_show(last_results, idx)
            except ValueError:
                print("Usage: show <number>  (e.g. show 3)")
        elif cmd == "export":
            parts2 = args.split(None, 1)
            fname = parts2[0] if parts2 else "export.md"
            if not fname.endswith(".md"):
                fname += ".md"
            cmd_export(last_results, fname)
        else:
            if RICH:
                console.print(f"[red]Unknown command:[/red] {cmd}  (type [bold]help[/bold] for commands)")
            else:
                print(f"Unknown command: {cmd}  (type 'help' for commands)")


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        cmd_help()
    else:
        run_repl()
