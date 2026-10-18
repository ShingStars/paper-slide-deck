#!/usr/bin/env python3
"""Check portable deck structure. This is not a general HTML sanitizer or visual QA."""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path

VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
FORBIDDEN = {'iframe', 'object', 'embed', 'base'}


def css_errors(css):
    errors = []
    if re.search(r'@import\b', css, re.I):
        errors.append('CSS @import is not allowed in an offline deck.')
    for match in re.finditer(r'url\(\s*([\s\S]*?)\s*\)', css, re.I):
        url = match.group(1).strip(' \t\r\n\"\'')
        if not url.lower().startswith('data:') and not url.startswith('#'):
            errors.append('CSS resource must be embedded: ' + url[:100])
    return errors


class DeckParser(HTMLParser):
    def __init__(self, fragment=False):
        super().__init__(convert_charrefs=True)
        self.fragment = fragment
        self.stack = []
        self.errors = []
        self.ids = set()
        self.targets = []
        self.slides = []
        self.script_count = 0
        self.css = []
        self.has_deck = False
        self.has_nav = False

    def error(self, message):
        self.errors.append(f'Line {self.getpos()[0]}: {message}')

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get('class') or '').split())
        element_id = attrs.get('id')
        if element_id:
            if element_id in self.ids:
                self.error('Duplicate id: ' + element_id)
            self.ids.add(element_id)
        if tag in FORBIDDEN or (self.fragment and tag in {'script', 'style', 'html', 'head', 'body', 'link', 'meta'}):
            self.error('Unsupported element: ' + tag)
        if tag == 'script':
            self.script_count += 1
        if tag == 'meta' and (attrs.get('http-equiv') or '').lower() == 'refresh':
            self.error('Meta refresh is not allowed.')
        for key, value in attrs.items():
            value = value or ''
            if key.startswith('on'):
                self.error('Inline event handlers are not allowed: ' + key)
            if key in {'src', 'poster', 'background', 'data'}:
                if not value.lower().startswith('data:'):
                    self.error('Resource must be embedded: ' + value[:100])
            if key == 'srcset':
                self.error('Use a single embedded src instead of srcset.')
            if key in {'href', 'xlink:href'}:
                if value.startswith('#'):
                    self.targets.append(value[1:])
                elif tag != 'a' or not re.match(r'^(https?://|mailto:|tel:)', value, re.I):
                    self.error('Unsupported link: ' + value[:100])
            if key == 'style':
                self.errors.extend(css_errors(value))
        if element_id == 'deck' and tag == 'main':
            self.has_deck = True
        if 'slide-nav' in classes:
            self.has_nav = True
        if self.fragment and not self.stack and not (tag == 'section' and 'slide' in classes):
            self.error('Fragment roots must be <section class="slide">.')
        is_slide = tag == 'section' and 'slide' in classes
        if is_slide:
            if self.fragment and self.stack:
                self.error('A slide must be a fragment root, not nested.')
            if not self.fragment and (not self.stack or self.stack[-1][2] != 'deck'):
                self.error('Slides must be direct children of main#deck.')
            if not element_id:
                self.error('Every slide needs a stable unique id.')
            self.slides.append({'id': element_id, 'title': attrs.get('data-title', ''), 'heading': False})
        if tag in {'h1', 'h2', 'h3'} and any('slide' in entry[1] for entry in self.stack):
            if self.slides:
                self.slides[-1]['heading'] = True
        if tag not in VOID:
            self.stack.append((tag, classes, element_id))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.error('Unexpected closing tag: ' + tag)
        elif self.stack[-1][0] != tag:
            self.error('Mismatched closing tag: ' + tag + '; expected ' + self.stack[-1][0])
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1][0] == 'style':
            self.css.append(data)
        if self.fragment and not self.stack and data.strip():
            self.error('Visible text must be inside a slide.')


def inspect(text, fragment=False):
    parser = DeckParser(fragment)
    parser.feed(text)
    parser.close()
    errors = list(parser.errors)
    if parser.stack:
        errors.append('Unclosed tags: ' + ', '.join(e[0] for e in parser.stack))
    if not parser.slides:
        errors.append('No slides found.')
    for slide in parser.slides:
        if not slide['heading']:
            errors.append('Slide has no heading: ' + str(slide['id']))
    for target in parser.targets:
        if target and target not in parser.ids:
            errors.append('Missing internal link target: ' + target)
    for css in parser.css:
        errors.extend(css_errors(css))
    if not fragment:
        if not parser.has_deck or not parser.has_nav:
            errors.append('Missing deck or navigation shell.')
        if parser.script_count != 1:
            errors.append('Expected exactly one inline runtime script.')
        if not re.search(r'<meta\s+[^>]*charset=', text, re.I):
            errors.append('Missing charset declaration.')
    return {'ok': not errors, 'slides': len(parser.slides), 'errors': errors}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('html', type=Path)
    ap.add_argument('--fragment', action='store_true')
    args = ap.parse_args()
    try:
        result = inspect(args.html.read_text(encoding='utf-8-sig'), args.fragment)
    except (OSError, UnicodeError) as error:
        result = {'ok': False, 'errors': [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
