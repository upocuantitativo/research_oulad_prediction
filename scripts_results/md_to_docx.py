# -*- coding: utf-8 -*-
"""Minimal Markdown -> .docx converter for the manuscript (headings, bold/italic,
tables, bullet lists, paragraphs). Usage: python md_to_docx.py <in.md> <out.docx>"""
import sys, re
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_runs(par, text):
    # handle **bold**, *italic*, `code`; strip markdown tokens
    tokens = re.split(r'(\*\*.+?\*\*|\*.+?\*|`.+?`)', text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('**') and tok.endswith('**'):
            r = par.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith('*') and tok.endswith('*'):
            r = par.add_run(tok[1:-1]); r.italic = True
        elif tok.startswith('`') and tok.endswith('`'):
            r = par.add_run(tok[1:-1]); r.font.name = 'Consolas'
        else:
            par.add_run(tok)

def main(src, dst):
    lines = open(src, encoding='utf-8').read().splitlines()
    doc = Document()
    style = doc.styles['Normal']; style.font.name = 'Calibri'; style.font.size = Pt(11)
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1; continue
        if ln.strip() == '---':
            i += 1; continue
        # table block
        if ln.lstrip().startswith('|'):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                block.append(lines[i].strip()); i += 1
            rows = [[c.strip() for c in r.strip('|').split('|')] for r in block]
            rows = [r for r in rows if not all(set(c) <= set('-: ') for c in r)]  # drop separator
            if rows:
                ncol = max(len(r) for r in rows)
                tbl = doc.add_table(rows=0, cols=ncol); tbl.style = 'Light Grid Accent 1'
                for ridx, r in enumerate(rows):
                    cells = tbl.add_row().cells
                    for cidx in range(ncol):
                        txt = r[cidx] if cidx < len(r) else ''
                        cells[cidx].text = ''
                        p = cells[cidx].paragraphs[0]
                        add_runs(p, txt)
                        if ridx == 0:
                            for rr in p.runs: rr.bold = True
            continue
        # headings
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            level = len(m.group(1)); txt = m.group(2).strip()
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', txt)
            if level == 1:
                h = doc.add_heading('', level=0); add_runs(h, txt)
            else:
                h = doc.add_heading('', level=min(level-1,4)); add_runs(h, txt)
            i += 1; continue
        # bullet
        if re.match(r'^\s*[-*]\s+', ln):
            txt = re.sub(r'^\s*[-*]\s+', '', ln)
            p = doc.add_paragraph(style='List Bullet'); add_runs(p, txt)
            i += 1; continue
        # blockquote
        if ln.lstrip().startswith('>'):
            txt = re.sub(r'^\s*>\s?', '', ln)
            p = doc.add_paragraph(); p.paragraph_format.left_indent = Pt(18); add_runs(p, txt)
            i += 1; continue
        # normal paragraph (gather until blank)
        para = [ln]; i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('|','#','-','*','>')) and lines[i].strip() != '---':
            para.append(lines[i].rstrip()); i += 1
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_runs(p, ' '.join(para))
    doc.save(dst)
    print('Saved', dst)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
