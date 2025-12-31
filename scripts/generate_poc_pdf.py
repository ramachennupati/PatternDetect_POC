#!/usr/bin/env python3
"""Generate a PDF from the POC_Guide.md file using reportlab."""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

INPUT = 'POC_Guide.md'
OUTPUT = 'POC_Guide.pdf'

def md_to_flowables(md_text):
    styles = getSampleStyleSheet()
    heading1 = ParagraphStyle('Heading1', parent=styles['Heading1'], fontSize=18, spaceAfter=6)
    heading2 = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=14, spaceAfter=4)
    body = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=10, leading=14)

    flowables = []
    for line in md_text.splitlines():
        line = line.rstrip()
        if not line:
            flowables.append(Spacer(1, 4))
            continue
        if line.startswith('# '):
            flowables.append(Paragraph(line[2:].strip(), heading1))
        elif line.startswith('## '):
            flowables.append(Paragraph(line[3:].strip(), heading2))
        elif line.startswith('### '):
            flowables.append(Paragraph(line[4:].strip(), heading2))
        else:
            # Escape & convert minor markdown elements
            text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            flowables.append(Paragraph(text, body))
    return flowables


def main():
    with open(INPUT, 'r', encoding='utf-8') as f:
        md = f.read()
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=20*mm, bottomMargin=20*mm)
    flowables = md_to_flowables(md)
    doc.build(flowables)
    print(f'Generated {OUTPUT}')

if __name__ == '__main__':
    main()
