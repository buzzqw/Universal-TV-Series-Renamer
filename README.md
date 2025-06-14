# 📺 Universal TV Series Renamer

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
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

**Universal script to automatically rename TV series episodes** by querying **TMDB**, **TVMaze**, and **IMDb** to get accurate episode title information.

## 🎯 Key Features

- 📺 **Universal**: Works with any TV series, not just specific ones
- 🌐 **Multi-source**: Integration with TMDB, TVMaze, and IMDb
- 🗣️ **Multilingual Interface**: English and Italian support
- 🎨 **5 Output Formats**: Standard, Plex, Simple, Minimal, Kodi
- 🔍 **Duplicate Management**: Smart choice between multiple versions
- 📊 **Missing Episodes**: Detects "gaps" in episode numbering
- 📋 **Adaptive Table**: Adjusts to terminal width
- 🔄 **Rollback Script**: Automatically restores original names
- 🛡️ **Safe Mode**: Preview before execution

## 🚀 Quick Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Installation
```bash
# Clone the repository
git clone https://github.com/buzzqw/Universal-TV-Series-Renamer.git
cd Universal-TV-Series-Renamer

# Install dependencies
pip install requests

# Make executable (Linux/macOS)
chmod +x tvrenamer4.py
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
python3 tvrenamer4.py /path/to/series

# Actual execution
python3 tvrenamer4.py /path/to/series --execute

# With TMDB API key for better results
python3 tvrenamer4.py /path/to/series --tmdb-key YOUR_API_KEY --execute
```

### Advanced Options

```bash
# Episode titles in English
python3 tvrenamer4.py --language en /path/to/series --tmdb-key YOUR_KEY

# Complete English interface
python3 tvrenamer4.py --interface en --language en /path/to/series --tmdb-key YOUR_KEY

# Plex-compatible format
python3 tvrenamer4.py --format plex /path/to/series --tmdb-key YOUR_KEY --execute

# Recursive search in subfolders
python3 tvrenamer4.py --recursive /path/to/series --tmdb-key YOUR_KEY --execute
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
TV Series - [01x01] - Episode Title.mkv
TV Series - [02x05] - Another Episode.mkv
```

### Plex
```
TV Series - S01E01 - Episode Title.mkv
TV Series - S02E05 - Another Episode.mkv
```

### Simple
```
TV Series 1x01 Episode Title.mkv
TV Series 2x05 Another Episode.mkv
```

### Minimal
```
TV Series S01E01.mkv
TV Series S02E05.mkv
```

### Kodi
```
TV Series S01E01 Episode Title.mkv
TV Series S02E05 Another Episode.mkv
```

## 📋 Example Output

```
📺 Universal TV Series Renamer v1.2 (Clean)
👨‍💻 Developed by: Andres Zanzani
📄 License: GPL-3.0
==================================================
📁 Directory: /home/user/Series/Circuit.Breakers
🎨 Format: standard
🌍 Language: en
🔄 Recursive: No
⚙️  Mode: PREVIEW
==================================================
✅ TMDB configured
✅ TVMaze configured
✅ IMDb configured
🔗 Active providers: TMDB, TVMaze, IMDb

📁 Found 7 video files

================================================================================
📺 SERIES: Circuit Breakers (7 files)
================================================================================
🔍 Searching for: 'Circuit Breakers'
🔄 Searching on TMDB...
✅ 1 results from TMDB
🔄 Searching on TVMaze...
✅ 1 results from TVMaze
🔄 Searching on IMDb...
✅ 3 results from IMDb

🔍 Results for: 'Circuit Breakers':
================================================================================
 1. TMDB | Circuit Breakers | 2022 | ⭐ 6.4/10
    └─ This futuristic anthology series tackles children's issues through...
 2. TVMaze | Circuit Breakers | 2022 | ⭐ 3.3/10
    └─ Circuit Breakers is a half-hour thought-provoking futuristic anthology...
 3. IMDb (tt21942776) | Circuit Breakers | ⭐ 5.5/10
    └─ Follow the futuristic anthology as it tackles children's issues...

Select (1-3, 0, q): 1

📋 EXECUTION - 7 files
========================================================================================================================
STATUS   ORIGINAL FILE                                      NEW FILE                                        
------------------------------------------------------------------------------------------------------------------------
✅ DONE   Circuit Breakers - [01x01] - Episode 1.mkv         Circuit Breakers - [01x01] - Test Subject 13.mkv  
✅ DONE   Circuit Breakers - [01x02] - Episode 2.mkv         Circuit Breakers - [01x02] - Copycat.mkv          
✅ DONE   Circuit Breakers - [01x03] - Episode 3.mkv         Circuit Breakers - [01x03] - Picture Perfect.mkv  
✅ DONE   Circuit Breakers - [01x04] - Episode 4.mkv         Circuit Breakers - [01x04] - Entangled.mkv        
✅ DONE   Circuit Breakers - [01x05] - Episode 5.mkv         Circuit Breakers - [01x05] - Permanent Detention.mkv
✅ DONE   Circuit Breakers - [01x06] - Episode 6.mkv         Circuit Breakers - [01x06] - Parental Controls.mkv
✅ DONE   Circuit Breakers - [01x07] - Episode 7.mkv         Circuit Breakers - [01x07] - No Place Like Home.mkv
========================================================================================================================
📊 RESULTS: ✅ 7 successes, ❌ 0 errors

📄 Restore script created: restore_tv_names_20250614_150000.py
💡 To restore original names, run: python restore_tv_names_20250614_150000.py
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

**Script universale per rinominare automaticamente episodi di serie TV** interrogando **TMDB**, **TVMaze** e **IMDb** per ottenere informazioni accurate sui titoli degli episodi.

## 🎯 Caratteristiche Principali

- 📺 **Universale**: Funziona con qualsiasi serie TV, non solo specifiche
- 🌐 **Multi-fonte**: Integrazione con TMDB, TVMaze e IMDb
- 🗣️ **Interfaccia multilingue**: Supporto Italiano e Inglese
- 🎨 **5 formati output**: Standard, Plex, Simple, Minimal, Kodi
- 🔍 **Gestione duplicati**: Scelta intelligente tra versioni multiple
- 📊 **Episodi mancanti**: Rileva "buchi" nella numerazione
- 📋 **Tabella adattiva**: Si adatta alla larghezza del terminale
- 🔄 **Script di rollback**: Ripristina i nomi originali automaticamente
- 🛡️ **Modalità sicura**: Preview prima dell'esecuzione

## 🚀 Installazione Rapida

### Prerequisiti
- Python 3.6 o superiore
- pip (gestore pacchetti Python)

### Installazione
```bash
# Clona il repository
git clone https://github.com/buzzqw/Universal-TV-Series-Renamer.git
cd Universal-TV-Series-Renamer

# Installa le dipendenze
pip install requests

# Rendi eseguibile (Linux/macOS)
chmod +x tvrenamer4.py
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
python3 tvrenamer4.py /path/to/series

# Esecuzione reale
python3 tvrenamer4.py /path/to/series --execute

# Con API key TMDB per risultati migliori
python3 tvrenamer4.py /path/to/series --tmdb-key YOUR_API_KEY --execute
```

### Opzioni Avanzate

```bash
# Titoli episodi in inglese
python3 tvrenamer4.py --language en /path/to/series --tmdb-key YOUR_KEY

# Interfaccia completamente in inglese
python3 tvrenamer4.py --interface en --language en /path/to/series --tmdb-key YOUR_KEY

# Formato compatibile con Plex
python3 tvrenamer4.py --format plex /path/to/series --tmdb-key YOUR_KEY --execute

# Ricerca ricorsiva nelle sottocartelle
python3 tvrenamer4.py --recursive /path/to/series --tmdb-key YOUR_KEY --execute
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
Serie TV - [01x01] - Titolo Episodio.mkv
Serie TV - [02x05] - Altro Episodio.mkv
```

### Plex
```
Serie TV - S01E01 - Titolo Episodio.mkv
Serie TV - S02E05 - Altro Episodio.mkv
```

### Simple
```
Serie TV 1x01 Titolo Episodio.mkv
Serie TV 2x05 Altro Episodio.mkv
```

### Minimal
```
Serie TV S01E01.mkv
Serie TV S02E05.mkv
```

### Kodi
```
Serie TV S01E01 Titolo Episodio.mkv
Serie TV S02E05 Altro Episodio.mkv
```

## 📋 Output Esempio

```
📺 Universal TV Series Renamer v1.2 (Clean)
👨‍💻 Sviluppato da: Andres Zanzani
📄 Licenza: GPL-3.0
==================================================
📁 Directory: /home/user/Series/Circuit.Breakers
🎨 Formato: standard
🌍 Lingua: it
🔄 Ricorsivo: No
⚙️  Modalità: PREVIEW
==================================================
✅ TMDB configurato
✅ TVMaze configurato
✅ IMDb configurato
🔗 Provider attivi: TMDB, TVMaze, IMDb

📁 Trovati 7 file video

================================================================================
📺 SERIE: Circuit Breakers (7 file)
================================================================================
🔍 Ricerca in corso per: 'Circuit Breakers'
🔄 Ricerca su TMDB...
✅ 1 risultati da TMDB
🔄 Ricerca su TVMaze...
✅ 1 risultati da TVMaze
🔄 Ricerca su IMDb...
✅ 3 risultati da IMDb

🔍 Risultati di ricerca per: 'Circuit Breakers':
================================================================================
 1. TMDB | Circuit Breakers | 2022 | ⭐ 6.4/10
    └─ In questa serie antologica di fantascienza, alcuni studenti del futuro...
 2. TVMaze | Circuit Breakers | 2022 | ⭐ 3.3/10
    └─ Circuit Breakers is a half-hour thought-provoking futuristic anthology...
 3. IMDb (tt21942776) | Circuit Breakers | ⭐ 5.5/10
    └─ Follow the futuristic anthology as it tackles children's issues...

Seleziona (1-3, 0, q): 1

📋 ESECUZIONE - 7 file
========================================================================================================================
STATO    FILE ORIGINALE                                     NUOVO FILE                                        
------------------------------------------------------------------------------------------------------------------------
✅ DONE   Circuit Breakers - [01x01] - Episode 1.mkv         Circuit Breakers - [01x01] - Soggetto numero 13.mkv
✅ DONE   Circuit Breakers - [01x02] - Episode 2.mkv         Circuit Breakers - [01x02] - Il duplicato.mkv      
✅ DONE   Circuit Breakers - [01x03] - Episode 3.mkv         Circuit Breakers - [01x03] - Il ricordo perfetto.mkv
✅ DONE   Circuit Breakers - [01x04] - Episode 4.mkv         Circuit Breakers - [01x04] - Lo scambio.mkv        
✅ DONE   Circuit Breakers - [01x05] - Episode 5.mkv         Circuit Breakers - [01x05] - Punizione infinita.mkv
✅ DONE   Circuit Breakers - [01x06] - Episode 6.mkv         Circuit Breakers - [01x06] - Controllo genitori.mkv
✅ DONE   Circuit Breakers - [01x07] - Episode 7.mkv         Circuit Breakers - [01x07] - Nessun luogo è come casa.mkv
========================================================================================================================
📊 RISULTATI: ✅ 7 successi, ❌ 0 errori

📄 Script di ripristino creato: restore_tv_names_20250614_150000.py
💡 Per ripristinare i nomi originali, esegui: python restore_tv_names_20250614_150000.py
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

Dopo ogni esecuzione riuscita, viene generato automaticamente uno script Python di ripristino:
```bash
# Per ripristinare i nomi originali
python restore_tv_names_20250614_150000.py
```

Lo script di ripristino:
- ✅ È completamente autonomo
- ✅ Funziona su Windows, Linux e Mac
- ✅ Ha interfaccia multilingue
- ✅ Chiede conferma prima di procedere
- ✅ Si auto-elimina dopo il ripristino riuscito

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [TMDB](https://www.themoviedb.org/) for TV series data
- [TVMaze](https://www.tvmaze.com/) for additional episode information
- [IMDb](https://www.imdb.com/) as fallback source
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
