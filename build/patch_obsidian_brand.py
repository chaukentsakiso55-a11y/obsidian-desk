from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
edition = sys.argv[2].strip().lower()
desktop = sys.argv[3].strip().lower()

editions = {
    "mini-lite": ("Mini Lite", "xfce4", "com.cyberpulse.obsidiandeck.minilite", "~300 MB desktop RAM"),
    "lite": ("Lite", "lxqt", "com.cyberpulse.obsidiandeck.lite", "~200 MB desktop RAM"),
    "standard": ("Standard", "mate", "com.cyberpulse.obsidiandeck.standard", "~400 MB desktop RAM"),
    "full": ("Full", "kde", "com.cyberpulse.obsidiandeck.full", "~600 MB desktop RAM"),
}
if edition not in editions:
    raise SystemExit("Unknown edition")
label, required_desktop, package_id, ram = editions[edition]
if desktop != required_desktop:
    raise SystemExit("Edition/desktop mismatch")

def load(path):
    return (root / path).read_text(encoding="utf-8")

def save(path, text):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def swap(path, old, new):
    text = load(path)
    if old not in text:
        raise SystemExit(f"Missing text in {path}: {old[:100]!r}")
    save(path, text.replace(old, new))

p = "app/pubspec.yaml"
text = load(p)
text = re.sub(r"^version:\s*.+$", "version: 1.0.0+100", text, flags=re.MULTILINE)
text = text.replace('description: "DroidDesk - Full Linux Desktop on Android"', 'description: "Obsidian Deck - Linux desktop on Android"')
if "assets/obsidian/obsidian-deck-icon.jpg" not in text:
    text = text.replace("    - assets/ember/ember_server.py\n", "    - assets/ember/ember_server.py\n    - assets/obsidian/obsidian-deck-icon.jpg\n")
text = text.replace('image_path: "assets/icons/logo.png"', 'image_path: "assets/obsidian/obsidian-deck-icon.jpg"')
save(p, text)

swap("app/android/app/build.gradle.kts", 'applicationId = "com.orailnoor.droiddesk"', f'applicationId = "{package_id}"')
swap("app/android/app/src/main/AndroidManifest.xml", 'android:label="DroidDesk"', f'android:label="Obsidian Deck {label}"')
swap("app/lib/main.dart", "title: 'DroidDesk',", f"title: 'Obsidian Deck {label}',")

p = "app/lib/state/app_state.dart"
text = load(p)
text = text.replace("String _selectedDE = 'xfce4';", f"String _selectedDE = '{desktop}';")
text = text.replace(
    "  void setSelectedDE(String de) {\n    _selectedDE = de;\n    notifyListeners();\n  }",
    f"  void setSelectedDE(String de) {{\n    _selectedDE = '{desktop}';\n    notifyListeners();\n  }}",
)
text = text.replace("DroidDesk Linux Terminal", "OBSIDIAN DECK Terminal")
save(p, text)

p = "app/lib/screens/setup/de_picker.dart"
text = load(p)
start = text.index("  static const _desktops = [")
end = text.index("\n  ];", start) + len("\n  ];")
icons = {"xfce4": "Icons.grid_view_rounded", "lxqt": "Icons.widgets_rounded", "mate": "Icons.view_comfy_rounded", "kde": "Icons.auto_awesome_mosaic_rounded"}
names = {"xfce4": "XFCE", "lxqt": "LXQt", "mate": "MATE", "kde": "KDE Plasma"}
block = f"""  static const _desktops = [
    _DEOption(
      id: '{desktop}',
      name: 'OBSIDIAN {label.upper()} · {names[desktop]}',
      description: 'Obsidian neon-blue desktop profile with the {names[desktop]} engine.',
      ram: '{ram}',
      icon: {icons[desktop]},
      color: Color(0xFF18B8FF),
      recommended: true,
    ),
  ];"""
text = text[:start] + block + text[end:]
text = text.replace("Text('Choose Desktop', style: DroidTheme.headingXl)", f"Text('Obsidian Deck · {label}', style: DroidTheme.headingXl)")
text = text.replace("Text('Install Essentials')", "Text('Initialize Obsidian')")
save(p, text)

p = "app/lib/theme/droid_theme.dart"
text = load(p)
for old, new in {
    "0xFF0A0E17": "0xFF030711",
    "0xFF111827": "0xFF07111F",
    "0xFF1A2332": "0xFF0B1D32",
    "0xFF1E293B": "0xFF12395A",
    "0xFF151D2B": "0xFF081522",
    "0xFF6366F1": "0xFF008CFF",
    "0xFF818CF8": "0xFF33C5FF",
    "0xFF22D3EE": "0xFF00E5FF",
    "0xFF10B981": "0xFF18B8FF",
    "0xFF8B5CF6": "0xFF005BFF",
    "0xFF0F1729": "0xFF061B2D",
}.items():
    text = text.replace(old, new)
save(p, text)

for p in ["app/lib/screens/welcome_screen.dart", "app/lib/screens/home_screen.dart", "app/lib/screens/setup/setup_progress.dart"]:
    text = load(p).replace("DroidDesk", "Obsidian Deck").replace("DROIDDESK", "OBSIDIAN DECK")
    save(p, text)

p = "app/lib/screens/apps/app_catalog_screen.dart"
text = load(p).replace("Linux App Store", "Obsidian App Center").replace("Hand-picked apps tested for DroidDesk.", "Linux apps verified for Obsidian Deck.")
save(p, text)

print(f"Applied Obsidian Deck {label} branding for {desktop}.")
