# Lazy Acc Cannon with GUI
The Lazy Acc Cannon by JimberryDev is a cannon for Minecraft Java 1.21.11+ that allows you to travel in a few minutes to anywhere in your world within a range of ~500 thousand blocks in the nether, or ~4 million blocks in the overworld; with a max error of ~15 blocks (if you build it at y128 on the roof). This works by accelerating an enderpearl using tnt in a lazy loaded chunk, what is known as "lazy acceleration". The amount of tnt for each axis, as well as the direction of is stored in a Read-Only memory (ROM).

It comes with a small desktop tool to generate `.litematic` schematics so you can input locations into the ROM. Just open the .exe, input the cannon origin, the targets' names and coordinates, and click on "Make Schematic". It will ask you where you want to save the generated schematic and where.

If you click on the "Overworld coords" checkbox, it will asume the coordinates you input are on the overworld side, and will divide by 8 the xz coordinates to get the nether respective coordinates before calculating.

---

## Features

- Multiple targets with coordinates
- Automatic TNT calculation per target
- Generates `.litematic` files
- Highlights unreachable targets in the GUI
- Summary output (OK / NOT REACHABLE )
- Remembers last origin and starting ID in a JSON file
- Packaged executable

---

## Installation

### Option 1 — Download executable (recommended)

Download the latest release from:

👉 [Releases](https://github.com/JimberryDev/Lazy-acc-pearl-cannon-calculator/releases)

Then:
1. Extract (if zipped)
2. Run `LazyAccCannon.exe`

---

### Option 2 — Run from source

**Requirements**
- Python [VERSION]
- Packages:
  - `numpy`
  - `litemapy`
  - [other dependencies if any]

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
python gui.py
```

---

## 🖥️ Usage

### Inputs

- **Litematica origin**
  - Where the base cannon schematic is placed

- **Number of existing schematics**
  - Starting ID for new entries

- **Targets**
  - Name (optional)
  - X, Y, Z coordinates
  - Optional: **Overworld coords** (divides by 8 internally)

### Steps

1. Fill origin and starting ID
2. Add one or more targets
3. Click **Make schematic**
4. Choose output `.litematic` path

---

## 📤 Output

- A `.litematic` file containing decoder + data slices
- Only **reachable** targets are included

GUI feedback:
- Unreachable targets are highlighted
- Output shows per-target status and reason

---

## 💾 Saved State

The app stores a JSON file with:
- last origin
- last starting ID

File name:

```text
lazy_acc_cannon_gui_state.json
```

Location:
- Source run: next to Python files
- Packaged exe: next to the executable

---

## 🧠 How it works (high level)

1. Compute trajectory using Minecraft drag + gravity
2. Convert velocity → TNT counts
3. Encode TNT into binary layout
4. Build regions (decoder + data)
5. Merge into final schematic

---

## 📁 Project Structure

```text
[project root]
├─ gui.py
├─ slice_schems.py
├─ cannon_calc.py
├─ data_classes.py
├─ src/
│  ├─ Data slice.litematic
│  ├─ Decoder slice.litematic
│  └─ Repeater.litematic
├─ app.ico
└─ [other files]
```

---

## 🛠️ Build (PyInstaller)

Create venv and install:

```bash
py -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
pip install pyinstaller
```

Create spec:

```bash
pyi-makespec --onefile --windowed --name LazyAccCannon gui.py --add-data "src;src" --add-data "app.ico;." --icon app.ico
```

Build:

```bash
pyinstaller LazyAccCannon.spec
```

Output:

```text
dist/LazyAccCannon.exe
```

---

## 🖼️ Icons

- `.exe` icon is set via `--icon app.ico`
- Window icon is set in code using `root.iconbitmap(...)`
- Ensure `app.ico` is bundled with `--add-data`

---

## ⚠️ Limitations

- Max schematics: `64`
- Max TNT per axis: `3199`
- Assumes [CANNON DESIGN DETAILS]
- Assumes [COORDINATE SYSTEM DETAILS]

---

## 🧩 Known Issues

- Windows icon cache may delay icon updates
- [OTHER ISSUE]

---

## 🚧 TODO

- Friendlier error messages
- Save/load target presets
- [IDEA]
- [IDEA]

---

## 📦 Releases

End users should download from:

👉 [Releases](<REPLACE_WITH_RELEASES_LINK>)

---

## 👤 Author

- [YOUR NAME / HANDLE]

---

## 📜 License

[LICENSE HERE]
