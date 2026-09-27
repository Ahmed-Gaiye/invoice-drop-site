#!/usr/bin/env python3
"""Rebuilds the site from the app's texts: python3 build.py
Sources: ../InvoiceApp/AppStore/{privacy-policy,support,terms-of-use}.md (plain Python, no dependencies)."""
import html, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'InvoiceApp', 'AppStore')

def inline(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', t)
    t = re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+)', r'<a href="mailto:\1">\1</a>', t)
    return t

def md(text):
    out, para, inlist = [], [], False
    def flush():
        nonlocal para
        if para:
            out.append('<p>' + '<br>'.join(inline(x) for x in para) + '</p>')
            para = []
    for line in text.splitlines():
        if line.startswith('# '):
            continue
        if line.startswith('## '):
            flush()
            if inlist: out.append('</ul>'); inlist = False
            out.append('<h2>' + inline(line[3:]) + '</h2>'); continue
        if line.startswith('- '):
            flush()
            if not inlist: out.append('<ul>'); inlist = True
            out.append('<li>' + inline(line[2:]) + '</li>'); continue
        if not line.strip():
            flush()
            if inlist: out.append('</ul>'); inlist = False
            continue
        para.append(line)
    flush()
    if inlist: out.append('</ul>')
    return '\n'.join(out)

NAV = [('Support', 'support/'), ('Privacy', 'privacy/'), ('Terms', 'terms/')]

def page(title, desc, root, current, body):
    nav = ''.join(f'<a href="{root}{href}"{" aria-current=\"page\"" if name == current else ""}>{name}</a>' for name, href in NAV)
    return f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="icon" href="{root}logo.png"><link rel="stylesheet" href="{root}style.css">
</head><body><div class="wrap">
<header><a href="{root}"><img src="{root}logo.png" alt=""><span>Invoice Drop</span></a><nav>{nav}</nav></header>
{body}
<footer>© 2026 Pulseni · <a href="{root}terms/">Terms of Use</a> · <a href="{root}privacy/">Privacy Policy</a> · <a href="mailto:support@pulseni.com">support@pulseni.com</a></footer>
</div></body></html>
'''

def write(path, text):
    full = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w').write(text)

HOME = '''<main class="card hero">
<img src="logo.png" alt="Invoice Drop app icon">
<h1>Invoice Drop</h1>
<p>Pick the days you worked, choose your client, and send a professional PDF invoice in seconds. Everything stays on your iPhone.</p>
<span class="btn">Coming soon to the App Store</span>
<div class="links"><a href="support/">Help &amp; support</a><a href="privacy/">Privacy policy</a><a href="terms/">Terms of use</a></div>
</main>'''
write('index.html', page('Invoice Drop', 'Simple invoices from the days you worked, as a real PDF, on your iPhone.', '', '', HOME))
for folder, source, title, name in [('privacy', 'privacy-policy.md', 'Privacy Policy', 'Privacy'),
                                    ('support', 'support.md', 'Support', 'Support'),
                                    ('terms', 'terms-of-use.md', 'Terms of Use', 'Terms')]:
    text = open(os.path.join(SRC, source)).read()
    write(f'{folder}/index.html', page(f'{title} – Invoice Drop', f'Invoice Drop {title.lower()}.', '../', name,
                                       f'<main class="card"><h1>{title}</h1>\n{md(text)}\n</main>'))
print('Site rebuilt.')
