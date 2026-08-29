# 📺 Universal TV Series Renamer

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/buzzqw/Universal-TV-Series-Renamer)

🌍 **[English](#english-documentation) | [Italiano](#documentazione-italiana)**

---

## 💝 Support the Project

**If you find this project useful, please consider supporting development:**

[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/buzzqw?country.x=IT&locale.x=it_IT)

**[💰 Donate via PayPal](https://paypal.me/buzzqw?country.x=IT&locale.x=it_IT)**

Your support helps maintain and improve this free tool for the community! 🙏

---

# English Documentation

**Universal script to automatically rename TV series episodes** by querying **TMDB** and **TVMaze** to get episode title information.

## 🎯 Key Features

- 📺 **Universal**: Works with any TV series, not just specific ones
- 🌐 **Multi-source**: Integration with TMDB and TVMaze
- 🗣️ **Multilingual Interface**: English and Italian support
- 🎨 **5 Output Formats**: Standard, Plex, Simple, Minimal, Kodi
- 🔍 **Duplicate Management**: Smart handling of multiple versions with automatic [Version X] labeling
- 📊 **Missing Episodes**: Detects gaps in episode numbering with highlighted warnings
- ⚠️ **Preflight**: Detects collisions before changing files
- 🔄 **Rollback Script**: Automatically restores original names
- 🛡️ **Safe Mode**: Preview before execution

## 🚀 Quick Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation
```bash
# Clone the repository
git clone https://github.com/buzzqw/Universal-TV-Series-Renamer.git
cd Universal-TV-Series-Renamer

# Install dependencies
pip install -r requirements.txt

# Make executable (Linux/macOS)
chmod +x tvrenamer3.py
```

### TMDB API Key (Optional but Recommended)
For better episode title quality:
1. Register at [TheMovieDB](https://www.themoviedb.org/)
2. Go to [API Settings](https://www.themoviedb.org/settings/api)
3. Request a free API key
4. Use `--tmdb-key YOUR_KEY` option with the script

## 📖 Usage

### Basic Examples

```bash
# Safe preview (recommended for first time)
python3 tvrenamer3.py /path/to/series

# Actual execution
python3 tvrenamer3.py /path/to/series --execute

# With TMDB API key for better results
python3 tvrenamer3.py /path/to/series --tmdb-key YOUR_API_KEY --execute
```

### Advanced Options

```bash
# Episode titles in English
python3 tvrenamer3.py --language en /path/to/series --tmdb-key YOUR_KEY

# Complete English interface
python3 tvrenamer3.py --interface en --language en /path/to/series --tmdb-key YOUR_KEY

# Plex-compatible format
python3 tvrenamer3.py --format plex /path/to/series --tmdb-key YOUR_KEY --execute

# Recursive search in subfolders
python3 tvrenamer3.py --recursive /path/to/series --tmdb-key YOUR_KEY --execute
```

### All Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--language` | `it`, `en`, `es`, `fr`, `de` | `it` | Language for episode titles |
| `--interface` | `it`, `en` | `it` | User interface language |
| `--format` | `standard`, `plex`, `simple`, `minimal`, `kodi` | `standard` | Output filename format |
| `--tmdb-key` | `API_KEY` | - | TMDB API key (optional) |
| `--recursive` | - | `false` | Search recursively in subfolders |
| `--execute` | - | `false` | Execute renames (default: preview only) |
| `--version` | - | - | Show version and copyright |

## 🎨 Output Formats

### Standard (Default)
```
Cosmic Academy - S01E01 - First Contact.mkv
Cosmic Academy - S02E05 - Stellar Navigation.mkv
```

### Plex
```
Cosmic Academy - S01E01 - First Contact.mkv
Cosmic Academy - S02E05 - Stellar Navigation.mkv
```

### Simple
```
Cosmic Academy 1x01 First Contact.mkv
Cosmic Academy 2x05 Stellar Navigation.mkv
```

### Minimal
```
Cosmic Academy S01E01.mkv
Cosmic Academy S02E05.mkv
```

### Kodi
```
Cosmic Academy S01E01 First Contact.mkv
Cosmic Academy S02E05 Stellar Navigation.mkv
```

## 📋 Example Output

```
📺 Universal TV Series Renamer v1.2 (Clean)
👨‍💻 Developed by: Andres Zanzani
📄 License: GPL-3.0
==================================================
📁 Directory: /home/user/Series/Space.Rangers
🎨 Format: standard
🌍 Language: en
🔄 Recursive: No
⚙️  Mode: EXECUTION
==================================================
✅ TMDB configured
✅ TVMaze configured
🔗 Active providers: TMDB, TVMaze

📁 Found 8 video files

================================================================================
📺 SERIES: Space Rangers (8 files)
================================================================================
🔍 Searching for: 'Space Rangers'
🔄 Searching on TMDB...
✅ 1 results from TMDB
🔄 Searching on TVMaze...
✅ 1 results from TVMaze

🔍 Results for: 'Space Rangers':
================================================================================
 1. TMDB | Space Rangers | 2024 | ⭐ 8.4/10
    └─ Elite space pilots protect the galaxy from cosmic threats while...
 2. TVMaze | Space Rangers | 2024 | ⭐ 7.9/10
    └─ Intergalactic peacekeepers maintain order across distant worlds...

Select (1-3, 0, q): 1

⚠️  MISSING EPISODES DETECTED:
   📺 Season 1: Missing E03, E07
================================================================================
💡 Suggestion: Check if you have all episodes of the series
================================================================================

🔄 DUPLICATES DETECTED: S01E05 - 2 files
   1. Space.Rangers.S01E05.1080p.WEB-DL.x264.mkv (2950.8 MB)
   2. Space.Rangers.S01E05.720p.HDTV.x264.mkv (1380.2 MB)

📋 EXECUTION - 8 files
========================================================================================================================
STATUS   ORIGINAL FILE                                      NEW FILE                                        
------------------------------------------------------------------------------------------------------------------------
✅ DONE   Space.Rangers.S01E01.1080p.WEB-DL.mkv             Space Rangers - S01E01 - Pilot Mission.mkv
✅ DONE   Space.Rangers.S01E02.1080p.WEB-DL.mkv             Space Rangers - S01E02 - Deep Space.mkv
✅ DONE   Space.Rangers.S01E04.1080p.WEB-DL.mkv             Space Rangers - S01E04 - Asteroid Belt.mkv
✅ DONE   Space.Rangers.S01E05.1080p.WEB-DL.mkv             Space Rangers - S01E05 - Solar Storm [Version 1].mkv
✅ DONE   Space.Rangers.S01E05.720p.HDTV.mkv                Space Rangers - S01E05 - Solar Storm [Version 2].mkv
✅ DONE   Space.Rangers.S01E06.1080p.WEB-DL.mkv             Space Rangers - S01E06 - Alien Alliance.mkv
✅ DONE   Space.Rangers.S01E08.1080p.WEB-DL.mkv             Space Rangers - S01E08 - Final Mission.mkv
✅ DONE   Space.Rangers.S01E09.1080p.WEB-DL.mkv             Space Rangers - S01E09 - New Horizons.mkv
========================================================================================================================
📊 RESULTS: ✅ 8 successes, ❌ 0 errors

📄 Restore script created: restore_tv_names_20250614_150000.py
💡 To restore original names, run: python restore_tv_names_20250614_150000.py
```

## 🔧 Advanced Features

### 🔍 **Missing Episode Detection**
The script automatically detects gaps in episode numbering:
```
⚠️  MISSING EPISODES DETECTED:
   📺 Season 1: Missing E03, E07
   📺 Season 2: Missing E01, E05
================================================================================
💡 Suggestion: Check if you have all episodes of the series
================================================================================
```

### 🔄 **Duplicate File Management**
When multiple files exist for the same episode, the script:
- **Automatically** detects duplicates
- **Orders by file size** (larger = better quality)
- **Labels with [Version X]** system

Example:
```
🔄 DUPLICATES DETECTED: S01E05 - 2 files
   1. Space.Rangers.S01E05.1080p.WEB-DL.mkv (2950.8 MB)  → [Version 1]
   2. Space.Rangers.S01E05.720p.HDTV.mkv (1380.2 MB)     → [Version 2]
```

## 🛠️ Troubleshooting

### Error: "No series found"
1. Check series name spelling
2. Try with original English name
3. Use a shorter name
4. Register a TMDB API key for better results

### Error: "API key not configured"
- Register for free at [TheMovieDB](https://www.themoviedb.org/settings/api)
- Use `--tmdb-key YOUR_KEY` in the command

### Unrecognized files
- Verify filename contains `S01E01` or `1x01`
- Series name must be before episode numbering

## 📄 Supported File Formats

**Supported video extensions:**
- `.mkv`, `.avi`, `.mp4`, `.m4v`
- `.mov`, `.wmv`, `.flv`, `.webm`
- `.ts`, `.m2ts`

**Recognized filename patterns:**
- `Series.S01E01.*.ext` (standard format)
- `Series.1x01.*.ext` (alternative format)
- `Series.Season.1.Episode.01.*.ext` (extended format)

## 🔄 Restore Feature

After each successful execution, a Python restore script is automatically generated:
```bash
# To restore original names
python restore_tv_names_20250614_150000.py
```

The restore script:
- ✅ Is completely self-contained
- ✅ Works on Windows, Linux, and Mac
- ✅ Has multilingual interface
- ✅ Asks for confirmation before proceeding
- ✅ Self-deletes after successful restoration

---

# Documentazione Italiana

**Script universale per rinominare automaticamente episodi di serie TV** interrogando **TMDB** e **TVMaze** per ottenere i titoli degli episodi.

## 🎯 Caratteristiche Principali

- 📺 **Universale**: Funziona con qualsiasi serie TV, non solo specifiche
- 🌐 **Multi-fonte**: Integrazione con TMDB e TVMaze
- 🗣️ **Interfaccia multilingue**: Supporto Italiano e Inglese
- 🎨 **5 formati output**: Standard, Plex, Simple, Minimal, Kodi
- 🔍 **Gestione duplicati**: Gestione intelligente di più versioni con etichettatura automatica [Versione X]
- 📊 **Episodi mancanti**: Rileva vuoti nella numerazione con avvisi evidenziati
- 📋 **Tabella adattiva**: Si adatta alla larghezza del terminale
- 🔄 **Script di rollback**: Ripristina i nomi originali automaticamente
- 🛡️ **Modalità sicura**: Preview prima dell'esecuzione

## 🚀 Installazione Rapida

### Prerequisiti
- Python 3.7 o superiore
- pip (gestore pacchetti Python)

### Installazione
```bash
# Clona il repository
git clone https://github.com/buzzqw/Universal-TV-Series-Renamer.git
cd Universal-TV-Series-Renamer

# Installa le dipendenze
pip install -r requirements.txt

# Rendi eseguibile (Linux/macOS)
chmod +x tvrenamer3.py
```

### API Key TMDB (Opzionale ma Raccomandato)
Per ottenere titoli episodi di qualità migliore:
1. Registrati su [TheMovieDB](https://www.themoviedb.org/)
2. Vai su [API Settings](https://www.themoviedb.org/settings/api)
3. Richiedi una API key gratuita
4. Usa l'opzione `--tmdb-key YOUR_KEY` con lo script

## 📖 Utilizzo

### Esempi Base

```bash
# Preview sicura (raccomandato per la prima volta)
python3 tvrenamer3.py /path/to/series

# Esecuzione reale
python3 tvrenamer3.py /path/to/series --execute

# Con API key TMDB per risultati migliori
python3 tvrenamer3.py /path/to/series --tmdb-key YOUR_API_KEY --execute
```

### Opzioni Avanzate

```bash
# Titoli episodi in inglese
python3 tvrenamer3.py --language en /path/to/series --tmdb-key YOUR_KEY

# Interfaccia completamente in inglese
python3 tvrenamer3.py --interface en --language en /path/to/series --tmdb-key YOUR_KEY

# Formato compatibile con Plex
python3 tvrenamer3.py --format plex /path/to/series --tmdb-key YOUR_KEY --execute

# Ricerca ricorsiva nelle sottocartelle
python3 tvrenamer3.py --recursive /path/to/series --tmdb-key YOUR_KEY --execute
```

### Tutti i Parametri

| Parametro | Valori | Default | Descrizione |
|-----------|--------|---------|-------------|
| `--language` | `it`, `en`, `es`, `fr`, `de` | `it` | Lingua per i titoli degli episodi |
| `--interface` | `it`, `en` | `it` | Lingua dell'interfaccia utente |
| `--format` | `standard`, `plex`, `simple`, `minimal`, `kodi` | `standard` | Formato del nome file output |
| `--tmdb-key` | `API_KEY` | - | API key per TMDB (opzionale) |
| `--recursive` | - | `false` | Cerca ricorsivamente nelle sottocartelle |
| `--execute` | - | `false` | Esegue le rinomine (default: solo preview) |
| `--version` | - | - | Mostra versione e copyright |

## 🎨 Formati Output

### Standard (Default)
```
Guardiani Cosmici - S01E01 - Primo Contatto.mkv
Guardiani Cosmici - [02x05] - Navigazione Stellare.mkv
```

### Plex
```
Guardiani Cosmici - S01E01 - Primo Contatto.mkv
Guardiani Cosmici - S02E05 - Navigazione Stellare.mkv
```

### Simple
```
Guardiani Cosmici 1x01 Primo Contatto.mkv
Guardiani Cosmici 2x05 Navigazione Stellare.mkv
```

### Minimal
```
Guardiani Cosmici S01E01.mkv
Guardiani Cosmici S02E05.mkv
```

### Kodi
```
Guardiani Cosmici S01E01 Primo Contatto.mkv
Guardiani Cosmici S02E05 Navigazione Stellare.mkv
```

## 📋 Output Esempio

```
📺 Universal TV Series Renamer v1.2 (Clean)
👨‍💻 Sviluppato da: Andres Zanzani
📄 Licenza: GPL-3.0
==================================================
📁 Directory: /home/user/Series/Stelle.Perdute
🎨 Formato: standard
🌍 Lingua: it
🔄 Ricorsivo: No
⚙️  Modalità: ESECUZIONE
==================================================
✅ TMDB configurato
✅ TVMaze configurato
🔗 Provider attivi: TMDB, TVMaze

📁 Trovati 7 file video

================================================================================
📺 SERIE: Stelle Perdute (7 file)
================================================================================
🔍 Ricerca in corso per: 'Stelle Perdute'
🔄 Ricerca su TMDB...
✅ 1 risultati da TMDB
🔄 Ricerca su TVMaze...
✅ 1 risultati da TVMaze

🔍 Risultati di ricerca per: 'Stelle Perdute':
================================================================================
 1. TMDB | Stelle Perdute | 2024 | ⭐ 8.6/10
    └─ Un equipaggio di esploratori cerca pianeti abitabili in galassie remote...
 2. TVMaze | Stelle Perdute | 2024 | ⭐ 8.1/10
    └─ Avventure di scienziati spaziali che mappano sistemi solari inesplorati...

Seleziona (1-3, 0, q): 1

⚠️  EPISODI MANCANTI RILEVATI:
   📺 Stagione 1: Mancano E04
================================================================================
💡 Suggerimento: Verifica se hai tutti gli episodi della serie
================================================================================

🔄 DUPLICATI RILEVATI: S01E06 - 2 file
   1. Stelle.Perdute.S01E06.1080p.WEB-DL.mkv (3100.5 MB)
   2. Stelle.Perdute.S01E06.720p.HDTV.mkv (1520.7 MB)

📋 ESECUZIONE - 7 file
========================================================================================================================
STATO    FILE ORIGINALE                                     NUOVO FILE                                        
------------------------------------------------------------------------------------------------------------------------
✅ DONE   Stelle.Perdute.S01E01.1080p.WEB-DL.mkv            Stelle Perdute - S01E01 - Partenza.mkv
✅ DONE   Stelle.Perdute.S01E02.1080p.WEB-DL.mkv            Stelle Perdute - S01E02 - Nebulosa Oscura.mkv
✅ DONE   Stelle.Perdute.S01E03.1080p.WEB-DL.mkv            Stelle Perdute - S01E03 - Pianeta Ghiacciato.mkv
✅ DONE   Stelle.Perdute.S01E05.1080p.WEB-DL.mkv            Stelle Perdute - S01E05 - Incontro Alieno.mkv
✅ DONE   Stelle.Perdute.S01E06.1080p.WEB-DL.mkv            Stelle Perdute - S01E06 - Salvezza [Versione 1].mkv
✅ DONE   Stelle.Perdute.S01E06.720p.HDTV.mkv               Stelle Perdute - S01E06 - Salvezza [Versione 2].mkv
✅ DONE   Stelle.Perdute.S01E07.1080p.WEB-DL.mkv            Stelle Perdute - S01E07 - Ritorno.mkv
========================================================================================================================
📊 RISULTATI: ✅ 7 successi, ❌ 0 errori

📄 Script di ripristino creato: restore_tv_names_20250614_150000.py
💡 Per ripristinare i nomi originali, esegui: python restore_tv_names_20250614_150000.py
```

## 🔧 Funzionalità Avanzate

### 🔍 **Rilevamento Episodi Mancanti**
Lo script rileva automaticamente vuoti nella numerazione:
```
⚠️  EPISODI MANCANTI RILEVATI:
   📺 Stagione 1: Mancano E03, E07
   📺 Stagione 2: Mancano E01, E05
================================================================================
💡 Suggerimento: Verifica se hai tutti gli episodi della serie
================================================================================
```

### 🔄 **Gestione File Duplicati**
Quando esistono più file per lo stesso episodio, lo script:
- **Rileva automaticamente** i duplicati
- **Ordina per dimensione** (più grande = migliore qualità)
- **Etichetta con sistema [Versione X]**

Esempio:
```
🔄 DUPLICATI RILEVATI: S01E06 - 2 file
   1. Stelle.Perdute.S01E06.1080p.WEB-DL.mkv (3100.5 MB)  → [Versione 1]
   2. Stelle.Perdute.S01E06.720p.HDTV.mkv (1520.7 MB)     → [Versione 2]
```

## 🛠️ Risoluzione Problemi

### Errore: "Nessuna serie trovata"
1. Verifica l'ortografia del nome serie
2. Prova con il nome originale in inglese
3. Usa un nome più breve
4. Registra una API key TMDB per risultati migliori

### Errore: "API key non configurata"
- Registra gratuitamente su [TheMovieDB](https://www.themoviedb.org/settings/api)
- Usa `--tmdb-key YOUR_KEY` nel comando

### File non riconosciuti
- Verifica che il filename contenga `S01E01` o `1x01`
- Il nome della serie deve essere prima della numerazione episodio

## 📄 Formati File Supportati

**Estensioni video supportate:**
- `.mkv`, `.avi`, `.mp4`, `.m4v`
- `.mov`, `.wmv`, `.flv`, `.webm`
- `.ts`, `.m2ts`

**Pattern filename riconosciuti:**
- `Serie.S01E01.*.ext` (formato standard)
- `Serie.1x01.*.ext` (formato alternativo)
- `Serie.Season.1.Episode.01.*.ext` (formato esteso)

## 🔄 Funzionalità di Ripristino

Dopo ogni esecuzione reale viene generato automaticamente uno script Python e un manifest JSON di ripristino:
```bash
# Per ripristinare i nomi originali
python restore_tv_names_20250614_150000.py
```

Lo script di ripristino:
- ✅ È completamente autonomo
- ✅ Funziona su Windows, Linux e Mac
- ✅ Ha interfaccia multilingue
- ✅ Chiede conferma prima di procedere
- ✅ Conserva i percorsi relativi completi, anche in modalità ricorsiva
- ✅ Non si auto-elimina se il ripristino è parziale

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [TMDB](https://www.themoviedb.org/) for TV series data
- [TVMaze](https://www.tvmaze.com/) for additional episode information
- The open source community for the libraries used

## 📞 Support

For bugs, feature requests, or questions:
- 🐛 **Issues**: [GitHub Issues](https://github.com/buzzqw/Universal-TV-Series-Renamer/issues)

---

## 💝 Support the Project Again

**If this tool saved you time, please consider a small donation:**

[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/buzzqw?country.x=IT&locale.x=it_IT)

**[💰 Donate via PayPal](https://paypal.me/buzzqw?country.x=IT&locale.x=it_IT)**

Every contribution helps keep this project alive and improving! 🚀

---

**⭐ If you like this project, please give it a star on GitHub!**

Made with ❤️ by [Andres Zanzani](https://github.com/buzzqw)
