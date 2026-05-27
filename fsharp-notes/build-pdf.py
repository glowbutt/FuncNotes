#!/usr/bin/env python3
"""Build FSharp-Notes.pdf — a single, print-ready PDF of all section notes.

Usage:   python3 build-pdf.py
Needs:   pandoc + a LaTeX engine (xelatex).  On macOS:
             brew install pandoc
             brew install --cask mactex-no-gui      # (or basictex)

It concatenates the section notes (in order), adds a title page + table of
contents (each section becomes a chapter on a fresh page), maps every special
glyph (arrows, ✓/✗, λ, …) to a LaTeX command for prose, and transliterates
those glyphs to ASCII inside code blocks (where LaTeX can't substitute them).
"""
import os, sys, tempfile, subprocess, datetime

NOTES = os.path.dirname(os.path.abspath(__file__))
BUILD = tempfile.mkdtemp(prefix="fsnotes-")
OUT = os.path.join(NOTES, "FSharp-Notes.pdf")

FILES = [
    "00-foundations/foundations.md",
    "01-data-types/fsharp_data_types.md",
    "02-functions-and-recursion/functions-and-recursion.md",
    "04-collections/collections.md",
    "05-advancedFP/advanced-fp.md",
]

# ASCII transliteration applied ONLY inside fenced code blocks (verbatim).
CODE_MAP = {
    "→": "->", "⤳": "~>", "↦": "|->", "⇒": "=>", "↑": "^", "↓": "v", "↔": "<->",
    "≡": "==", "≠": "<>", "≥": ">=", "≤": "<=", "∧": "/\\", "∨": "\\/", "¬": "~",
    "λ": "\\", "…": "...", "✅": "[x]", "❌": "[ ]", "⚠": "(!)",
    "—": "--", "–": "-", "§": "sec.", "️": "",
}

def transliterate_code(line):
    for k, v in CODE_MAP.items():
        line = line.replace(k, v)
    return line

def process(path):
    out, in_fence = [], False
    for line in open(path, encoding="utf-8").read().splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
        else:
            out.append(transliterate_code(line) if in_fence else line)
    return "\n".join(out)

yaml = (
    "---\n"
    'title: "Functional Programming 2026 — F# Study Notes"\n'
    'author: "Sebastian Holt Svendsen"\n'
    f'date: "{datetime.date.today().isoformat()}"\n'
    "---\n\n"
)
body = "\n\n".join(process(os.path.join(NOTES, f)) for f in FILES)
open(os.path.join(BUILD, "master.md"), "w", encoding="utf-8").write(yaml + body)

# Prose glyph -> LaTeX command (newunicodechar covers everything outside code).
PROSE_MAP = [
    ("→", r"\ensuremath{\rightarrow}"), ("⤳", r"\ensuremath{\rightsquigarrow}"),
    ("↦", r"\ensuremath{\mapsto}"), ("⇒", r"\ensuremath{\Rightarrow}"),
    ("↑", r"\ensuremath{\uparrow}"), ("↓", r"\ensuremath{\downarrow}"),
    ("↔", r"\ensuremath{\leftrightarrow}"), ("≡", r"\ensuremath{\equiv}"),
    ("≠", r"\ensuremath{\neq}"), ("≥", r"\ensuremath{\geq}"), ("≤", r"\ensuremath{\leq}"),
    ("∧", r"\ensuremath{\wedge}"), ("∨", r"\ensuremath{\vee}"), ("¬", r"\ensuremath{\neg}"),
    ("λ", r"\ensuremath{\lambda}"), ("✅", r"\ding{51}"), ("❌", r"\ding{55}"),
    ("⚠", r"\textbf{!}"), ("—", r"---"), ("–", r"--"), ("…", r"\ldots{}"),
    ("§", r"\S{}"), ("️", r""),
]
hdr = [
    r"\usepackage{amssymb}", r"\usepackage{pifont}", r"\usepackage{fvextra}",
    r"\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}",
    r"\usepackage{etoolbox}", r"\AtBeginEnvironment{longtable}{\small}",
    r"\setlength{\tabcolsep}{4pt}", r"\usepackage{newunicodechar}",
]
hdr += [r"\newunicodechar{%s}{%s}" % (ch, cmd) for ch, cmd in PROSE_MAP]
open(os.path.join(BUILD, "header.tex"), "w", encoding="utf-8").write("\n".join(hdr) + "\n")

cmd = [
    "pandoc", "master.md", "-H", "header.tex", "-o", OUT,
    "--pdf-engine=xelatex", "--toc", "--toc-depth=2",
    "--top-level-division=chapter", "-V", "documentclass=report",
    "-V", "geometry:margin=2.2cm", "-V", "colorlinks=true", "-V", "linkcolor=blue",
    "--highlight-style=tango",
]
print("building", OUT, "...")
r = subprocess.run(cmd, cwd=BUILD)
sys.exit(r.returncode)
