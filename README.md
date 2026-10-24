# mod-acp-fix

A fix for the Addon Control Panel (ACP 3.3.4a) that the HD client packs of WoW 3.3.5a carry in `Data\patch-5.MPQ`: in six of its languages (deDE, esES, esMX, frFR, koKR, zhTW) its window stays empty.

## Key features

- ACP shows the English text of a missing translation instead of stopping with an error.
- The six incomplete localization files get their missing texts.
- The Spanish texts get back their lost accented characters.
- Client only: `patch-5.MPQ` is left untouched, and removing the fix brings back the original ACP.

## Dependencies

| Dependency | For |
|---|---|
| A WoW 3.3.5a HD client pack carrying ACP 3.3.4a | the addon being fixed; do not install it with another version of ACP |

## How to install

1. Download `installer.exe` from the [WoW-mods-installer releases](https://github.com/Adrestie/WoW-mods-installer/releases).
2. Close the game.
3. Run `installer.exe`, give it this folder and the game folder, click **Check**, then **Install**.

## How to update

Same steps with the new version's folder, choosing **Update** instead of **Install**.

## How to uninstall

Same steps, choosing **Remove**.

## Credits

- ACP is the work of sylvanaar, Rophy and Saien, the authors its `ACP.toc` names. The files in `data/game` come from their addon, as the HD packs carry it, with the changes above.
