# 🚀 Quick Start Guide - Cyberpunk Terminal

## Instalare și Pornire

### 1. Verificare Sistem

```bash
# Verifică Python 3
python3 --version  # Trebuie să fie 3.7+

# Verifică terminal size
echo "Terminal: $COLUMNS x $LINES"
# Recomandat: 80x24 sau mai mare
```

### 2. Pornire

```bash
# Metoda 1: Direct
cd /workspace
python3 cyberpunk_terminal.py

# Metoda 2: Cu script
./run.sh

# Metoda 3: Test imports first
python3 test_imports.py
python3 cyberpunk_terminal.py
```

## 📋 Keybindings Esențiale

### Navigare Cursor

| Key | Action |
|-----|--------|
| `←` / `→` | Mută cursorul stânga/dreapta |
| `Ctrl+←` / `Ctrl+→` | Mută pe cuvinte |
| `Home` sau `Ctrl+A` | Salt la început de linie |
| `End` sau `Ctrl+E` | Salt la sfârșit de linie |

### Editare Text

| Key | Action |
|-----|--------|
| `Backspace` | Șterge caracter înainte |
| `Delete` sau `Ctrl+D` | Șterge caracter după cursor |
| `Ctrl+W` | Șterge cuvânt înainte |
| `Ctrl+K` | Șterge până la sfârșit de linie |
| `Ctrl+U` | Șterge până la început de linie |
| `Ctrl+L` | Curăță linia curentă |

### Istoric și Autocomplete

| Key | Action |
|-----|--------|
| `↑` sau `Ctrl+P` | Comandă anterioară în istoric |
| `↓` sau `Ctrl+N` | Comandă următoare în istoric |
| `Tab` | Afișează autocomplete |
| `↑` / `↓` (în autocomplete) | Navighează sugestii |
| `Enter` | Acceptă sugestie / Execută comandă |

### Undo/Redo

| Key | Action |
|-----|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |

### Sistem

| Key | Action |
|-----|--------|
| `Ctrl+C` | Ieșire din aplicație |
| `F1` | Ajutor |

## 🎨 Comenzi Built-in

```bash
# Navigare directoare
cd [dir]        # Schimbă directorul
pwd             # Afișează directorul curent

# Environment
export VAR=val  # Setează variabilă de mediu
export          # Listează toate variabilele

# Aliasuri
alias name=cmd  # Setează alias
alias           # Listează toate aliasurile
unalias name    # Șterge alias

# Utilități
clear           # Curăță ecranul
history         # Afișează istoric comenzi
help            # Afișează ajutor
exit            # Ieșire (sau Ctrl+C)
```

## 🎯 Exemple Rapide

### 1. Navigare Simplă

```bash
$ pwd
/workspace

$ cd /tmp
$ pwd
/tmp

$ cd ~
$ pwd
/home/user
```

### 2. Utilizare Autocomplete

```bash
$ git [Tab]
# Apare panel cu: git, grep, etc.
# Apasă ↑/↓ pentru selecție
# Apasă Enter pentru accept
```

### 3. Istoric Comenzi

```bash
$ ls -la
# ... output ...

$ echo "test"
# ... output ...

$ [↑]  # Apare: echo "test"
$ [↑]  # Apare: ls -la
$ [Enter]  # Execută ls -la din nou
```

### 4. Editare Complexă

```bash
$ echo "This is a very long command that I want to edit"
# Apasă Ctrl+A (salt la început)
$ [Home] echo "This is a very long command that I want to edit"
# Apasă Ctrl+→ de 5 ori (sari 5 cuvinte)
$ echo "This is a very long command that I want to edit"
                                 ^cursor aici
# Apasă Ctrl+W (șterge cuvânt)
$ echo "This is a very long that I want to edit"
```

### 5. Aliasuri

```bash
$ alias ll='ls -la'
$ ll
# Execută: ls -la

$ alias gst='git status'
$ gst
# Execută: git status
```

## 🎨 Customizare Rapidă

### Schimbă Tema

Editează `config.py`:

```python
# În __init__ al UserConfig:
theme: str = "cyberpunk"  # sau "christmas", "matrix", "ice", "fire"
```

### Ajustează Performanța

Editează `config.py`:

```python
render_quality: str = "ULTRA"  # LOW, MEDIUM, HIGH, ULTRA, INSANE
target_fps: int = 60           # Reduce pentru performance
```

### Activează/Dezactivează Efecte

Editează `config.py`:

```python
enable_parallax: bool = True
enable_tree: bool = True
enable_snow: bool = True
enable_sparkles: bool = True
```

## 🐛 Troubleshooting

### Problema: Terminal prea mic

```bash
# Verifică dimensiunea
echo "Size: $COLUMNS x $LINES"

# Mărește terminalul
# Recomandat: minim 80x24, ideal 120x40
```

### Problema: Culori greșite

```bash
# Verifică suport true color
echo $COLORTERM  # Trebuie să fie "truecolor" sau "24bit"

# Testează culori
printf "\x1b[38;2;255;100;0mTEST\x1b[0m\n"
```

### Problema: Unicode nu funcționează

```bash
# Verifică encoding
echo $LANG  # Trebuie să conțină "UTF-8"

# Setează encoding
export LANG=en_US.UTF-8
```

### Problema: Performance scăzut

```python
# Editează config.py:
render_quality: str = "MEDIUM"  # în loc de ULTRA
enable_parallax: bool = False   # dezactivează parallax
particle_count: int = 50        # reduce particule
```

## 📊 Verificare Stare

### Test Rapid

```bash
$ python3 test_imports.py
# Trebuie să afișeze:
# ✓ toate modulele
# ✓ toate testele funcționale
```

### Verificare Terminal

```bash
$ python3 -c "from terminal_core import get_terminal_size; print(get_terminal_size())"
(80, 24)  # sau dimensiunea ta
```

### Verificare Module

```bash
$ python3 -c "import cyberpunk_terminal; print('OK')"
OK
```

## 🎄 Tips & Tricks

### 1. Maximizează Fereastra

Pentru experiență optimă:
- Terminalul la fullscreen
- Font size moderat (12-14pt)
- Rezoluție minimă 80x24

### 2. Utilizează Istoricul

- `↑` pentru comenzi recente
- Rapid acces la comenzi lungi
- Nu mai scrii de 10 ori același lucru

### 3. Autocomplete Inteligent

- Scrie primele litere
- Apasă `Tab`
- Fuzzy matching găsește tot

### 4. Editare Eficientă

- `Ctrl+W` pentru ștergere cuvinte
- `Ctrl+U` pentru reset linie
- `Ctrl+K` pentru ștergere la sfârșit

### 5. Personalizează

- Schimbă tema în `config.py`
- Ajustează gradient-urile
- Modifică stilurile de border

## 🚀 Next Steps

1. ✅ Rulează `test_imports.py` pentru verificare
2. ✅ Pornește `cyberpunk_terminal.py`
3. ✅ Testează toate keybind-urile
4. ✅ Încearcă comenzile built-in
5. ✅ Customizează la preferințe

## 📚 Documentație Completă

- **README.md** - Ghid detaliat
- **ARCHITECTURE.md** - Arhitectură tehnică
- **CHANGELOG.md** - Istoricul modificărilor
- **IMPLEMENTATION_SUMMARY.md** - Rezumat implementare

## 🎉 Enjoy!

Ai acum un terminal cyberpunk complet funcțional cu:
- 🎨 Grafică avansată 3D
- ⌨️ Keybindings complete
- 🎄 Brad de Crăciun animat
- ❄️ Efecte de zăpadă
- ✨ Particule sparkle
- 🌟 Parallax background
- 📜 Istoric persistent
- 🔧 Complet customizabil

**Distrează-te!** 🚀
