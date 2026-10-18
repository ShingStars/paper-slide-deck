#!/usr/bin/env python3
"""Assemble AI-authored slide fragments into one standalone HTML file."""
import argparse
import html
import json
import re
from pathlib import Path
from check_deck import inspect, css_errors

ROOT = Path(__file__).resolve().parent.parent


def build(slides_file, output, title, author='', extra_css=None):
    if slides_file.resolve() == output.resolve():
        raise ValueError('Output must not overwrite the slide fragment.')
    slides = slides_file.read_text(encoding='utf-8-sig')
    fragment_report = inspect(slides, fragment=True)
    if not fragment_report['ok']:
        raise ValueError('\n'.join(fragment_report['errors']))
    css = (ROOT / 'assets/theme.css').read_text(encoding='utf-8')
    if extra_css:
        css += '\n' + extra_css.read_text(encoding='utf-8-sig')
    if '</style' in css.lower():
        raise ValueError('CSS cannot close its inline style element.')
    problems = css_errors(css)
    if problems:
        raise ValueError('\n'.join(problems))
    values = {
        'DECK_TITLE': html.escape(title, quote=True),
        'DECK_AUTHOR': html.escape(author, quote=True),
        'DECK_CSS': css,
        'DECK_SLIDES': slides,
        'DECK_JS': (ROOT / 'assets/runtime.js').read_text(encoding='utf-8'),
    }
    shell = (ROOT / 'assets/shell.html').read_text(encoding='utf-8')
    # One pass: content containing template-like strings stays literal content.
    result = re.sub(r'\{\{(DECK_[A-Z]+)\}\}', lambda match: values[match.group(1)], shell)
    report = inspect(result)
    if not report['ok']:
        raise ValueError('\n'.join(report['errors']))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, encoding='utf-8')
    return {'ok': True, 'output': str(output.resolve()), 'slides': report['slides'], 'bytes': output.stat().st_size}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--slides-file', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--author', default='')
    ap.add_argument('--extra-css', type=Path)
    args = ap.parse_args()
    try:
        report = build(args.slides_file, args.output, args.title, args.author, args.extra_css)
    except (OSError, ValueError, KeyError) as error:
        ap.exit(1, 'Build failed: ' + str(error) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
