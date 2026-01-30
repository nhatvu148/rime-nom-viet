# rime-nom-viet

RIME 輸入法 Chữ Nôm (Vietnamese Nôm) input schema.

Type Vietnamese using **Telex** to input Chữ Nôm (喃字) characters.

## Features

- **52,000+ entries** - One of the most comprehensive Nôm dictionaries
- **38,000 compound words** - Multi-syllable phrases like "việt nam" → 越南
- **Telex input** - Type `nguowfi` to get 𠊛 (người)
- **Vietnamese preview** - Shows "người" instead of "nguowfi" while typing
- **Frequency ranking** - Common characters appear first

## Telex Input Guide

| Type | Get | Example |
|------|-----|---------|
| `aa` | â | `aan` → ân |
| `aw` | ă | `awn` → ăn |
| `ee` | ê | `ees` → ế |
| `oo` | ô | `oof` → ồ |
| `ow` | ơ | `owf` → ờ |
| `uw` | ư | `uws` → ứ |
| `dd` | đ | `ddi` → đi |

**Tones:**
| Key | Tone | Example |
|-----|------|---------|
| `s` | sắc (á) | `as` → á |
| `f` | huyền (à) | `af` → à |
| `r` | hỏi (ả) | `ar` → ả |
| `x` | ngã (ã) | `ax` → ã |
| `j` | nặng (ạ) | `aj` → ạ |

## Installation

### macOS (Squirrel)

```bash
# Using plum
bash rime-install nhatvu148/rime-nom-viet

# Or manually
cp nom_viet.*.yaml ~/Library/Rime/
```
Then right-click Squirrel icon → Deploy.

### Windows (Weasel)

```bash
# Using plum
bash rime-install nhatvu148/rime-nom-viet

# Or manually copy to:
# %APPDATA%\Rime\
```
Then right-click Weasel icon → Deploy.

### Linux (ibus-rime / fcitx5-rime)

```bash
# Using plum
bash rime-install nhatvu148/rime-nom-viet

# Or manually copy to:
# ~/.config/ibus/rime/
# or ~/.local/share/fcitx5/rime/
```

### Android (Trime 同文輸入法)

1. Install [Trime](https://github.com/osfans/trime) from GitHub releases
2. Copy `nom_viet.*.yaml` to `/sdcard/rime/`
3. Open Trime → Deploy

### iOS (iRime)

1. Install [iRime](https://apps.apple.com/app/id1142623977) from App Store
2. Transfer files via iCloud or WebDAV
3. Deploy in app settings

## Usage

1. Switch to Squirrel/Weasel/etc input method
2. Press `Ctrl+`` or `F4` to select "Nôm Việt 喃越"
3. Type Vietnamese in Telex: `vieetj nam` → 越南

## Examples

| Input | Vietnamese | Output |
|-------|------------|--------|
| `nguowfi` | người | 𠊛 |
| `vieetj nam` | việt nam | 越南 |
| `awn cowm` | ăn cơm | 咹𩚵 |
| `tooi` | tôi | 碎 |
| `ddij` | đi | 𨅸 |

## Data Source

Dictionary data from [Nôm Na Việt](https://hannom.nvnv.app) - a comprehensive Vietnamese Hán-Nôm dictionary platform.

## License

[MIT](LICENSE)

## Related Projects

- [rime-hannom](https://github.com/tranduythanh/rime-hannom) - Another RIME Hán-Nôm schema
- [rime-vietnamese](https://github.com/gkovacs/rime-vietnamese) - Vietnamese Quốc ngữ + Nôm
- [chunom.org](https://chunom.org) - Chữ Nôm resources
