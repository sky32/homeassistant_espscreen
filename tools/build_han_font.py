#!/usr/bin/env python3
"""Build a compact, baseline-aligned Simplified Chinese subset for the screen fonts."""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HAN_LINE = re.compile(r'(?m)^  SCRIPT_GLYPHS_HAN: "([^"]*)"$')
COMMON_HAN = 2500
EXTRA_HAN = '卧厅主卫浴'

def repertoire(core):
    if not HAN_LINE.search(core):
        raise SystemExit('packages/core.yaml has no SCRIPT_GLYPHS_HAN substitution')
    data = json.loads((ROOT / 'screen_manager/translations/zh-Hans.json').read_text(encoding='utf-8'))
    old = set(data['_meta']['glyphs'])

    def texts(node):
        if isinstance(node, dict):
            return [text for value in node.values() for text in texts(value)]
        if isinstance(node, list):
            return [text for value in node for text in texts(value)]
        return [node] if isinstance(node, str) else []

    translated = ''.join(text for section in (data.get('screen', {}), data.get('addon', {}).get('screen', {}))
                         for text in texts(section))
    translated_han = {char for char in translated if '\u4e00' <= char <= '\u9fff'}
    frequency_file = ROOT / 'tools/han_frequency.txt'
    common = [line.strip() for line in frequency_file.read_text(encoding='utf-8').splitlines()
              if line.strip() and not line.startswith('#')]
    if len(common) < COMMON_HAN or len(set(common[:COMMON_HAN])) != COMMON_HAN:
        raise SystemExit(f'{frequency_file} must list {COMMON_HAN} unique ranked Han characters')
    if any(len(char) != 1 or not '\u4e00' <= char <= '\u9fff' for char in common[:COMMON_HAN]):
        raise SystemExit(f'{frequency_file} contains a non-Han character in its first {COMMON_HAN} entries')
    retained = {char for char in old if not '\u4e00' <= char <= '\u9fff'}
    return ''.join(sorted(retained | translated_han | set(common[:COMMON_HAN]) | set(EXTRA_HAN)) )


def build(source, output):
    core_path = ROOT / 'packages/core.yaml'
    core = core_path.read_text(encoding='utf-8')
    glyphs = repertoire(core)
    with tempfile.TemporaryDirectory(prefix='han-font-') as temporary:
        temporary = Path(temporary)
        unicodes = temporary / 'unicodes.txt'
        subset = temporary / 'subset.otf'
        unicodes.write_text(''.join(f'U+{ord(char):04X}\n' for char in glyphs), encoding='ascii')
        pyftsubset = Path(__import__('sys').executable).with_name('pyftsubset')
        subprocess.run([str(pyftsubset), str(source), f'--unicodes-file={unicodes}', f'--output-file={subset}',
                        '--name-IDs=*', '--name-legacy', '--name-languages=*', '--notdef-glyph',
                        '--notdef-outline', '--recommended-glyphs'], check=True)
        from align_han_font import align
        align(subset, output)

    core = HAN_LINE.sub('  SCRIPT_GLYPHS_HAN: ' + json.dumps(glyphs, ensure_ascii=False), core, count=1)
    core_path.write_text(core, encoding='utf-8')
    translation_path = ROOT / 'screen_manager/translations/zh-Hans.json'
    translations = json.loads(translation_path.read_text(encoding='utf-8'))
    translations['_meta']['glyphs'] = glyphs
    translation_path.write_text(json.dumps(translations, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    han_count = sum('\u4e00' <= char <= '\u9fff' for char in glyphs)
    print(f'{han_count} Han characters, {len(glyphs)} total glyphs: {output.stat().st_size} bytes')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Full NotoSansCJKsc-Regular.otf source font')
    parser.add_argument('--output', type=Path, default=ROOT / 'fonts/TesseraHan-zh-Hans.otf')
    args = parser.parse_args()
    build(args.source, args.output)
