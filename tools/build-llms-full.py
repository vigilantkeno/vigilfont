#!/usr/bin/env python3
"""Regenerate llms-full.txt from the site's HTML plus install.md.

Run from the repo root after editing page copy:  python3 tools/build-llms-full.py
"""
import re, html, glob, os, sys

def text_of(fragment):
    s = fragment
    s = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S|re.I)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'<h1[^>]*>(.*?)</h1>', lambda m: '\n\n# '+inline(m.group(1))+'\n', s, flags=re.S|re.I)
    s = re.sub(r'<h2[^>]*>(.*?)</h2>', lambda m: '\n\n## '+inline(m.group(1))+'\n', s, flags=re.S|re.I)
    s = re.sub(r'<h3[^>]*>(.*?)</h3>', lambda m: '\n\n### '+inline(m.group(1))+'\n', s, flags=re.S|re.I)
    s = re.sub(r'<li[^>]*>(.*?)</li>', lambda m: '\n- '+inline(m.group(1)), s, flags=re.S|re.I)
    s = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '\n\n> '+inline(m.group(1))+'\n', s, flags=re.S|re.I)
    s = re.sub(r'</(p|div|section|article|figure|ul|ol|footer|header)>', '\n\n', s, flags=re.I)
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

def inline(s):
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def title_of(s):
    m = re.search(r'<title>(.*?)</title>', s, re.S|re.I)
    return inline(m.group(1)) if m else ''

def body_of(path):
    s = open(path, encoding='utf-8').read()
    m = re.search(r'<main[^>]*>(.*?)</main>', s, re.S|re.I)
    return title_of(s), text_of(m.group(1) if m else s)

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
out = []
out.append("# Vigil — full text\n")
out.append("> Vigil is a free, open-source softened geometric grotesk by Keno Vigil, under the "
           "SIL Open Font License 1.1. Eight weights with matching italics, an Outline style, and a "
           "continuous 200-900 variable axis. Free for commercial use: no cost, no account, no email, "
           "no attribution required. This file is the full text of vigilfont.com for machine readers.\n")
out.append("Source: https://www.vigilfont.com/ · Install guide: https://www.vigilfont.com/install.md\n")

out.append("\n---\n\n# Install\n")
out.append(re.sub(r'^# Install Vigil\n+', '', open('install.md', encoding='utf-8').read()).strip())

t, b = body_of('index.html')
out.append("\n---\n\n# Homepage — " + t + "\n\nhttps://www.vigilfont.com/\n\n" + b)

posts = sorted(p for p in glob.glob('notes/*.html') if not p.endswith('index.html'))
out.append("\n---\n\n# Notes\n")
for p in posts:
    t, b = body_of(p)
    url = "https://www.vigilfont.com/" + p[:-5]
    out.append("\n## " + t + "\n\n" + url + "\n\n" + b)

txt = "\n".join(out).rstrip() + "\n"
txt = re.sub(r'\n{3,}', '\n\n', txt)
open('llms-full.txt', 'w', encoding='utf-8').write(txt)
print("llms-full.txt: %d bytes, %d posts" % (len(txt), len(posts)))
