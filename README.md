# mod-acp-fix

A fix for the Addon Control Panel (ACP) that the HD client packs of World of
Warcraft 3.3.5a carry in `Data\patch-5.MPQ` (ACP 3.3.4a, "HD client").

## The problem

ACP takes its texts from one localization file per language, and stops with an
error when its language lacks a text. Its German, Spanish, Mexican Spanish,
French, Korean and Traditional Chinese files lack some (`Close`, `Memory Usage`,
and 21 more in German). In those languages ACP stops while it loads:

```
Interface\AddOns\ACP\ACP.lua:125: Locale key Close is not provided.
```

and its window, opened from the AddOns button of the game menu, stays empty:
title `ADDON_LIST`, no list.

## The fix

- `ACP.lua` shows the English text of a missing text instead of stopping.
- The localization files get their missing texts. `Close` takes the game's own
  word (`CLOSE`), in every language.

The fixed files are written into the archive the game reads last, which shadows
those of `patch-5.MPQ` without touching it. Removing the module brings back the
original ACP.

Only the files that change are shipped: `ACP.lua` and six localization files,
those of ACP 3.3.4a. With another version of ACP, do not install this module.

## Install

With [WoW-mods-installer](https://github.com/Adrestie/WoW-mods-installer): give it
this folder and the game folder. Run it again to remove the fix. The game must
be closed.

## Making the files again

`tools/make_fix.py` makes `data/game` from the original files of ACP (ACP.toc,
ACP.lua and the localization files, taken out of `patch-5.MPQ`):

```
python tools/make_fix.py <folder of the original files>
```

## Credits

ACP is the work of sylvanaar, Rophy and Saien. The files in `data/game` are
theirs, with the changes above.
