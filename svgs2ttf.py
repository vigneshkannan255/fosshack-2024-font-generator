#!/usr/bin/fontforge -script

import sys
import os.path
import json
import fontforge

IMPORT_OPTIONS = ('removeoverlap', 'correctdir')

try:
    unicode
except NameError:
    unicode = str

def loadConfig(filename='font.json'):
    with open(filename) as f:
        return json.load(f)
        

def setProperties(font, config):
    props = config['props']
    lang = props.pop('lang', 'English (US)')
    family = props.pop('family', None)
    style = props.pop('style', 'Regular')
    props['encoding'] = props.get('encoding', 'UnicodeFull')
    if family is not None:
        font.familyname = family
        font.fontname = family + '-' + style
        font.fullname = family + ' ' + style
    for k, v in config['props'].items():
        if hasattr(font, k):
            if isinstance(v, list):
                v = tuple(v)
            setattr(font, k, v)
        else:
            font.appendSFNTName(lang, k, v)
    for t in config.get('sfnt_names', []):
        font.appendSFNTName(str(t[0]), str(t[1]), unicode(t[2]))

def addGlyphs(font, config):
    for k, v in config['glyphs'].items():
        g = font.createMappedChar(int(k, 0))
        # Get outlines
        src = '%s.svg' % k
        

        if not isinstance(v, dict):
            v = {'src': v or src}
        print(config.get('input', '.'),os.path.sep,v.pop('src', src),"******")
        src = '%s%s%s' % (config.get('input', '.'), os.path.sep, v.pop('src', src))
        try:
            g.importOutlines(src, IMPORT_OPTIONS)
            g.removeOverlap()
        except Exception as e:
            sys.stderr.write(f"Error importing glyph from {src}: {e}\n")
            continue
    
        # Copy attributes
        for k2, v2 in v.items():
            if hasattr(g, k2):
                if isinstance(v2, list):
                    v2 = tuple(v2)
                setattr(g, k2, v2)

def start_process_ttf(config_file):
    config = loadConfig(config_file)
    os.chdir(os.path.dirname(config_file) or '.')
    font = fontforge.font()
    setProperties(font, config)
    addGlyphs(font, config)
    for outfile in config['output']:
        sys.stderr.write('Generating %s...\n' % outfile)
        font.generate(outfile)

