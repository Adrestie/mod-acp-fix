# -*- coding: utf-8 -*-
r"""Makes the fixed files of ACP (the Addon Control Panel of the HD client packs) from its original
files, into data/game/Interface/AddOns/ACP.

ACP takes its texts from localization-<language>.lua. Asked for a text its language does not give, it
raises an error ("Locale key ... is not provided") and stops while it loads: its window stays empty. The
copy of the HD packs (3.3.4a, Data\patch-5.MPQ) misses texts in deDE, esES, esMX, frFR, koKR and zhTW.

The fix: ACP.lua shows the English text of a missing text instead of stopping, and each localization
file gets its missing texts ("Close" takes the game's own word, CLOSE).

    python tools/make_fix.py <folder holding ACP.toc, ACP.lua and the localization files>
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "data", "game", "Interface", "AddOns", "ACP")

# The statement of ACP.lua that stops on a missing text, and what replaces it: the text's English key.
LOCALE_ERROR = re.compile(rb'error\(\s*"Locale key "\s*\.\.\s*tostring\(\s*k\s*\)\s*\.\.\s*" is not provided\."\s*\)')
FALLBACK = b"return k"

# Lua code: a long comment, a long string.
LONG_COMMENT = re.compile(r"--\[(=*)\[")
LONG_STRING = re.compile(r"\[(=*)\[")
# A text asked for (L["..."]), a text given (["..."] = ...).
ASKED = re.compile(r'\bL\[\s*"([^"\\]*)"\s*\]')
GIVEN = re.compile(r'\[\s*"([^"\\]*)"\s*\]\s*=')
# The end of the table given to ACP:UpdateLocale.
TABLE_END = re.compile(rb"\}\s*\)")

# A missing "Close" takes the game's own word, in every language.
GLOBAL_TEXTS = {"Close": "CLOSE"}
# The other missing texts, per language.
TEXTS = {
    "deDE": {
        "ACP: Some protected addons aren't loaded. Reload now?":
            "ACP: Einige geschützte Addons sind nicht geladen. Jetzt neu laden?",
        "Active Embeds": "Aktive Einbettungen",
        "Add to current selection": "Zur aktuellen Auswahl hinzufügen",
        "Author": "Autor",
        "Click to enable protect mode. Protected addons will not be disabled":
            "Klicken, um den Schutzmodus einzuschalten. Geschützte Addons werden",
        "Default": "Standard",
        "Dependencies": "Abhängigkeiten",
        "Disabled on reloadUI": "Nach dem Neuladen deaktiviert",
        "Embeds": "Einbettungen",
        "LoD Child Enable is now %s": "Aktivierung der LoD-Unteraddons ist jetzt %s",
        "Loadable OnDemand": "Bei Bedarf ladbar",
        "Memory Usage": "Speicherverbrauch",
        "Recursive": "Rekursiv",
        "Recursive Enable is now %s": "Rekursive Aktivierung ist jetzt %s",
        "Remove from current selection": "Aus der aktuellen Auswahl entfernen",
        "Rename": "Umbenennen",
        "Save": "Speichern",
        "Set ": "Set ",
        "Status": "Status",
        "Use SHIFT to override the current enabling of dependancies behaviour.":
            "UMSCHALT umgeht das aktuelle Aktivieren der Abhängigkeiten.",
        "Version": "Version",
        "when performing a reloadui.": "beim Neuladen der Oberfläche nicht deaktiviert.",
    },
    "esES": {
        "Active Embeds": "Inclusiones activas",
        "Memory Usage": "Uso de memoria",
    },
    "esMX": {
        "Active Embeds": "Inclusiones activas",
        "Memory Usage": "Uso de memoria",
    },
    "frFR": {
        "Active Embeds": "Intégrés actifs",
        "Memory Usage": "Utilisation de la mémoire",
    },
}


def code(text):
    """The Lua code of text (a str) without its comments; strings are kept."""
    out, i, n = [], 0, len(text)
    while i < n:
        if text.startswith("--", i):
            m = LONG_COMMENT.match(text, i)
            if m:
                end = text.find("]%s]" % m.group(1), m.end())
                i = n if end < 0 else end + len(m.group(1)) + 2
            else:
                end = text.find("\n", i)
                i = n if end < 0 else end
            continue
        c = text[i]
        if c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
            continue
        m = LONG_STRING.match(text, i)
        if m:
            end = text.find("]%s]" % m.group(1), m.end())
            j = n if end < 0 else end + len(m.group(1)) + 2
            out.append(text[i:j])
            i = j
            continue
        out.append(c)
        i += 1
    return "".join(out)


def lua_code(content):
    return code(content.decode("latin-1"))


def lua_string(value):
    """value as a Lua string; every byte past ASCII as a decimal escape, so the file's encoding does not
    matter."""
    out = []
    for b in value.encode("utf-8"):
        if b in (0x22, 0x5C):
            out.append("\\" + chr(b))
        elif 0x20 <= b < 0x7F:
            out.append(chr(b))
        else:
            out.append("\\%03d" % b)
    return '"%s"' % "".join(out)


def localization_files(toc):
    """{language: file name} of the localization files the .toc loads."""
    found = {}
    for line in toc.decode("latin-1").splitlines():
        m = re.match(r"\s*(localization-([A-Za-z]{4})\.lua)\s*$", line)
        if m:
            found[m.group(2)] = m.group(1)
    return found


def completed(content, language, keys):
    """The localization file (bytes) with the texts of keys known here added at the end of its table."""
    lines = []
    for key in keys:
        if key in GLOBAL_TEXTS:
            value = GLOBAL_TEXTS[key]
        elif key in TEXTS.get(language, {}):
            value = lua_string(TEXTS[language][key])
        else:
            continue
        lines.append("\t\t[%s] = %s," % (lua_string(key), value))
    ends = list(TABLE_END.finditer(content))
    if not lines or not ends:
        return None
    newline = b"\r\n" if b"\r\n" in content else b"\n"
    added = newline.join(line.encode("ascii") for line in lines) + newline
    end = ends[-1].start()
    # The new lines go before the line of the closing brace, or before the brace when it closes a
    # line of fields.
    start = content.rfind(b"\n", 0, end) + 1
    own_line = not content[start:end].strip()
    head = content[:start] if own_line else content[:end].rstrip() + newline
    last = len(head.rstrip())
    if head[last - 1:last] not in (b",", b";", b"{"):
        head = head[:last] + b"," + head[last:]
    return head + added + content[start if own_line else end:]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    source = sys.argv[1]
    names = {n.lower(): os.path.join(source, n) for n in os.listdir(source)}

    def read(name):
        path = names.get(name.lower())
        if path is None:
            return None
        with open(path, "rb") as f:
            return f.read()

    main_file, toc = read("ACP.lua"), read("ACP.toc")
    if main_file is None or toc is None:
        sys.exit("ACP.lua and ACP.toc must be in %s" % source)
    if not LOCALE_ERROR.search(main_file):
        sys.exit("this ACP.lua does not stop on a missing text: nothing to fix")
    asked = set(ASKED.findall(lua_code(main_file)))

    files = {"ACP.lua": LOCALE_ERROR.sub(FALLBACK, main_file, count=1)}
    for language, name in sorted(localization_files(toc).items()):
        content = read(name)
        if content is None:
            print("%s: missing from %s" % (name, source))
            continue
        missing = sorted(asked - set(GIVEN.findall(lua_code(content))))
        new = completed(content, language, missing) if missing else None
        if new is not None:
            files[name] = new
        left = [k for k in missing if k not in GLOBAL_TEXTS and k not in TEXTS.get(language, {})]
        print("%s: %d text(s) missing, %d added%s" % (language, len(missing), len(missing) - len(left),
                                                      ", the others in English" if left else ""))

    os.makedirs(OUTPUT, exist_ok=True)
    for name in os.listdir(OUTPUT):
        os.remove(os.path.join(OUTPUT, name))
    for name, content in sorted(files.items()):
        with open(os.path.join(OUTPUT, name), "wb") as f:
            f.write(content)
        print("written: %s" % os.path.relpath(os.path.join(OUTPUT, name), ROOT))


if __name__ == "__main__":
    main()
