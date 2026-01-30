# rime-nom-viet

RIME input schema for Vietnamese Chữ Nôm (喃字).

Type Vietnamese using **Telex** to input Nôm characters.

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

### macOS (Squirrel 鼠鬚管)

**Step 1: Install Squirrel**
```bash
brew install --cask squirrel
```
Or download from: https://github.com/rime/squirrel/releases

**Step 2: Install plum + nom_viet**
```bash
cd ~/Library/Rime
curl -fsSL https://raw.githubusercontent.com/rime/plum/master/rime-install | bash
bash plum/rime-install nhatvu148/rime-nom-viet
```

Or **manually**:
1. Download `nom_viet.schema.yaml` and `nom_viet.dict.yaml` from this repo
2. Copy to `~/Library/Rime/`

**Step 3: Add to schema list**

Create/edit `~/Library/Rime/default.custom.yaml`:
```yaml
patch:
  schema_list:
    - schema: nom_viet
    - schema: luna_pinyin
```

**Step 4: Deploy**
- Click Squirrel icon in menu bar → Deploy (重新部署)
- Or run: `/Library/Input\ Methods/Squirrel.app/Contents/MacOS/Squirrel --reload`

**Step 5: Select schema**
- Press `Ctrl+`` or `F4` to switch to "Nôm Việt 喃越"

---

### Windows (Weasel 小狼毫)

**Step 1: Install Weasel**
- Download from: https://github.com/rime/weasel/releases
- Run installer, restart if needed

**Step 2: Install plum + nom_viet**

Open **Git Bash** (not PowerShell):
```bash
cd "$APPDATA/Rime"
git clone --depth 1 https://github.com/rime/plum.git
bash plum/rime-install nhatvu148/rime-nom-viet
```

Or **manually**:
1. Download `nom_viet.schema.yaml` and `nom_viet.dict.yaml` from this repo
2. Copy to `%APPDATA%\Rime\` (usually `C:\Users\<username>\AppData\Roaming\Rime\`)

**Step 3: Add to schema list**

Create/edit `%APPDATA%\Rime\default.custom.yaml`:
```yaml
patch:
  schema_list:
    - schema: nom_viet
    - schema: luna_pinyin
```

**Step 4: Deploy**
- Right-click Weasel icon in system tray → 重新部署 (Deploy)

**Step 5: Select schema**
- Press `Ctrl+`` or `F4` to switch to "Nôm Việt 喃越"

---

### Linux (ibus-rime / fcitx5-rime)

**Step 1: Install ibus-rime or fcitx5-rime**
```bash
# Ubuntu/Debian
sudo apt install ibus-rime
# or
sudo apt install fcitx5-rime

# Arch
sudo pacman -S ibus-rime
# or
sudo pacman -S fcitx5-rime
```

**Step 2: Install plum + nom_viet**
```bash
# For ibus-rime
cd ~/.config/ibus/rime

# For fcitx5-rime
cd ~/.local/share/fcitx5/rime

# Then install
curl -fsSL https://raw.githubusercontent.com/rime/plum/master/rime-install | bash
bash plum/rime-install nhatvu148/rime-nom-viet
```

**Step 3: Add to schema list**

Edit `default.custom.yaml` in the same directory:
```yaml
patch:
  schema_list:
    - schema: nom_viet
    - schema: luna_pinyin
```

**Step 4: Deploy**
- ibus: Right-click icon → Deploy
- fcitx5: Right-click icon → Restart

---

### Android (Trime 同文輸入法)

1. Install [Trime](https://github.com/osfans/trime/releases) from GitHub releases
2. Download `nom_viet.schema.yaml` and `nom_viet.dict.yaml`
3. Copy to `/sdcard/rime/` using file manager
4. Open Trime → Settings → Deploy
5. Select "Nôm Việt" in schema list

---

### iOS (iRime)

1. Install [iRime](https://apps.apple.com/app/id1142623977) from App Store
2. Download the schema files
3. Transfer via iCloud Drive or WebDAV (built into iRime)
4. Deploy in app settings
5. Select "Nôm Việt" schema

---

## Usage Examples

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
