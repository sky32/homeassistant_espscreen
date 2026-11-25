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
EXTRA_HAN = '卧厅'

def repertoire(core):
    match = HAN_LINE.search(core)
    if not match:
        raise SystemExit('packages/core.yaml has no SCRIPT_GLYPHS_HAN list')
    if match.group(1) == '${HAN_GLYPHS}':
        data = json.loads((ROOT / 'screen_manager/translations/zh-Hans.json').read_text(encoding='utf-8'))
        retained = set(data['_meta']['glyphs'])
    else:
        retained = set(match.group(1))
    common = []
    for lead in range(0xB0, 0xF8):
        for trail in range(0xA1, 0xFF):
            try:
                char = bytes((lead, trail)).decode('gb2312')
            except UnicodeDecodeError:
                continue
            if '\u4e00' <= char <= '\u9fff' and char not in common:
                common.append(char)
    if len(common) < COMMON_HAN:
        raise SystemExit(f'GB2312 provides only {len(common)} common Han characters')
    return ''.join(sorted(retained | set(common[:COMMON_HAN]) | set(EXTRA_HAN)) )


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
