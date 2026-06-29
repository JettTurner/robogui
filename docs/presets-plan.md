# Presets feature — implementation plan

## Goals

- Add a preset selection screen as the first page of RoboGUI
- Allow users to quickly pick a common robocopy scenario and jump to the full UI pre-configured
- Show a live command preview on both pages

## File changes

| File | Action |
|---|---|
| `src/presets.py` | **Create** — preset data definitions + PresetsPage widget |
| `src/ui.py` | **Refactor** — extract AdvancedPage, add page switching via QStackedWidget |
| `src/core.py` | Unchanged |
| `src/robogui.py` | Unchanged |

## Presets (9)

| # | Name | Key flags | Use case |
|---|---|---|---|
| 1 | Quick Backup | `/E /COPY:DAT /MT:16` | Everyday folder copy |
| 2 | Mirror Sync | `/MIR /MT:16` | Exact 1:1 sync (deletes extras) |
| 3 | Full Backup + Security | `/E /COPY:DATSOU /MT:8` | Preserves ACLs, owner, audit |
| 4 | Large File Transfer | `/E /J /Z /MT:4` | Unbuffered I/O + restartable |
| 5 | Network Friendly | `/E /IPG:100 /R:10 /MT:2` | Throttled for slow links |
| 6 | Sync Missing Files | `/E /COPY:DAT /R:2 /W:1` | Copy only new files, never delete |
| 7 | Dry Run Preview | `/L /E /X /V /TS /FP` | Simulate without copying |
| 8 | Age Filtered Backup | `/E /MINAGE:1 /MAXAGE:365 /MT:16` | Files within date range |
| 9 | Move Files | `/MOV /E /COPY:DAT` | Copy + delete source |

## UI structure

```
QMainWindow: RoboGUI
└── QStackedWidget
    ├── [0] PresetsPage
    │   ├── Path inputs (src, dst)  ← live-synced with AdvancedPage
    │   ├── Grid of preset cards (2 cols × 5 rows)
    │   │   └── Each card: name, desc, flags tag, [Use] button
    │   ├── Command preview (auto-updating)
    │   └── [ Advanced Mode → ] button
    │
    └── [1] AdvancedPage (current full UI)
        ├── Header: [ ← Presets ] back button
        ├── Path inputs ← live-synced with PresetsPage
        ├── Mode & Performance
        ├── Copy Options
        ├── File Selection
        ├── File Throttling
        ├── Retry Options
        ├── Logging Options
        ├── Job Options
        ├── Raw Arguments
        ├── Command preview (auto-updating)
        ├── START / STOP / DRY RUN buttons
        └── Log output
```

## Preset selection flow

1. User clicks **[Use]** on a preset card
2. `PresetsPage` emits a signal with the preset's `cfg` dict
3. `RoboGUI` calls `AdvancedPage.load_config(cfg)` to populate every widget
4. `RoboGUI` switches the stacked widget to index 1 (AdvancedPage)
5. User reviews/adjusts settings, command preview updates live, clicks **START**

## Path sync

- `PresetsPage.src_input.textChanged` → updates `AdvancedPage.src_input.setText`
- `AdvancedPage.src_input.textChanged` → updates `PresetsPage.src_input.setText`
- Same for `dst_input`
- Prevents infinite loop by checking if value actually changed before setting

## `load_config(cfg)` method on AdvancedPage

Iterates over the cfg dict and sets every widget:
- `QLineEdit.setText(v)` for text values
- `QSpinBox.setValue(v)` for numeric values
- `QCheckBox.setChecked(v)` for booleans
- `QComboBox.setCurrentIndex(...)` for sparse
- `SegmentedButtons` → find button group and click the matching index
