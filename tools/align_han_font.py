#!/usr/bin/env python3
"""Align the ascender of a Noto CJK SC subset with the firmware's Roboto fonts."""
import argparse
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def align(source, output):
    with TTFont(source, recalcTimestamp=False) as han, TTFont(ROOT / 'fonts/Roboto-400.ttf') as latin:
        # ESPHome measures each extra glyph from its own ascender, then LVGL uses Roboto's shared baseline.
        # Match that reference point without moving the Han outlines or changing their advance widths.
        han['hhea'].ascent = round(latin['hhea'].ascent * han['head'].unitsPerEm / latin['head'].unitsPerEm)
        family, ps_name = 'Tessera Han', 'TesseraHan-Regular'
        replacements = {1: family, 3: ps_name, 4: family + ' Regular', 6: ps_name, 16: family}
        for record in han['name'].names:
            if record.nameID in replacements:
                record.string = replacements[record.nameID].encode(record.getEncoding())
        cff = han['CFF '].cff
        cff.fontNames[0] = ps_name
        cff.topDictIndex[0].FamilyName = family
        cff.topDictIndex[0].FullName = family + ' Regular'
        han.save(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Unmodified Noto Sans CJK SC subset')
    parser.add_argument('output', type=Path, help='Aligned OTF, e.g. fonts/TesseraHan-zh-Hans.otf')
    args = parser.parse_args()
    align(args.source, args.output)
