# TV Series Renamer Documentation

This Python script takes care of renaming TV series files with proper episode information.

## Usage

```bash
python3 tvrenamer3.py [-h] [--execute] [--format {standard,plex,simple,minimal,kodi}] [--recursive] [--language {it,en,es,fr,de}] [--interface {it,en}] [--tmdb-key TMDB_KEY] [--version] [--license] directory
```

### Required Arguments
- `directory` - The directory containing the TV series files

### Optional Arguments
- `--execute` - Actually perform the renaming (without this flag, it runs in preview mode)
- `--format` - Choose naming format: standard, plex, simple, minimal, kodi
- `--recursive` - Process subdirectories recursively
- `--language` - Episode title language: it, en, es, fr, de
- `--interface` - Interface language: it, en
- `--tmdb-key` - TMDB API key for episode information

## Example Usage

### Preview Mode (Safe - No Changes)
```bash
python3 tvrenamer3.py . --tmdb-key YOUR-API-KEY
```

### Execution Mode (Actually Renames Files)
```bash
python3 tvrenamer3.py . --tmdb-key YOUR-API-KEY --execute --interface en --language en
```

**If you like this project please offer a coffe!**  [TV Series](https://paypal.me/buzzqw?country.x=IT&locale.x=it_IT)

## Sample Output

### Preview Mode Example
```
📺 Universal TV Series Renamer v1.0
👨‍💻 Sviluppato da: Andres Zanzani
📄 Licenza: GPL-3.0
==================================================
📁 Directory: /xxx/yyyy/zzzz/Fallout
🎨 Formato: standard
🌍 Lingua: en
🔄 Ricorsivo: No
⚙️  Modalità: PREVIEW
==================================================
✅ TMDB API key configurata

📁 Trovati 8 file video
📊 Rilevate 1 serie diverse

================================================================================
📺 SERIE: Fallout (8 file)
================================================================================

🔍 Ricerca in corso per: 'Fallout'
🔄 Ricerca su TMDB...

🔍 Risultati di ricerca per: 'Fallout'
================================================================================
 1. TMDB | Fallout | 2024 | ⭐ 8.3/10
    └─ The story of haves and have-nots in a world in which there's almost nothing left to have. 200 years ...

 2. TMDB | Fallout: Nuka Break | 2011 | ⭐ 7.7/10
 3. TMDB | Fallout: The Wanderer | 2017 | ⭐ 8.0/10
    └─ This origin story follows the not-so-NCR Ranger, James Eldridge in the Wasteland, and his first enco...

0. ❌ Nessuna delle opzioni sopra
r. 🔄 Ricerca con nome diverso
q. 🚪 Esci dal programma
```

### Renaming Preview Table
| Original Name | New Name |
|---------------|----------|
| `Fallout.S01E01.La.fine.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv` | `Fallout - [01x01] - The End.mkv` |
| `Fallout.S01E02.L.obiettivo.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv` | `Fallout - [01x02] - The Target.mkv` |
| `Fallout.S01E03.La.testa.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv` | `Fallout - [01x03] - The Head.mkv` |
| `Fallout.S01E04.Il.Ghoul.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv` | `Fallout - [01x04] - The Ghouls.mkv` |
| `Fallout.S01E05.Il.passato.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv` | `Fallout - [01x05] - The Past.mkv` |
| `Fallout.S01E06.La.Trappola.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv` | `Fallout - [01x06] - The Trap.mkv` |
| `Fallout.S01E07.La.Radio.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv` | `Fallout - [01x07] - The Radio.mkv` |
| `Fallout.S01E08.Il.principio.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv` | `Fallout - [01x08] - The Beginning.mkv` |

### Execution Results
```
📊 RESULTS: ✅ 8 successes, ❌ 0 errors
✅ Rollback script generated: rollback_renamer.py
💡 **To restore original names, run**:
   python3 "rollback_renamer.py"
   or: ./rollback_renamer.py
```

## After Execution - Directory Listing
```
'Fallout - [01x01] - The End.mkv'
'Fallout - [01x02] - The Target.mkv'
'Fallout - [01x03] - The Head.mkv'
'Fallout - [01x04] - The Ghouls.mkv'
'Fallout - [01x05] - The Past.mkv'
'Fallout - [01x06] - The Trap.mkv'
'Fallout - [01x07] - The Radio.mkv'
'Fallout - [01x08] - The Beginning.mkv'
rollback_renamer.py
```

## Naming Formats

The script supports multiple naming formats:

1. **STANDARD**: `Serie - [01x01] - Episodio.mkv`
2. **PLEX**: `Serie - S01E01 - Episodio.mkv`
3. **SIMPLE**: `Serie 1x01 Episodio.mkv`
4. **MINIMAL**: `Serie S01E01.mkv`
5. **KODI**: `Serie S01E01 Episodio.mkv`

## Important Notes

- ⚠️ **Always run in preview mode first** to check the results before executing
- 🔄 **Rollback script is automatically generated** for safety
- 📡 **Requires TMDB API key** for episode information
- 🌍 **Supports multiple languages** for episode titles
- 🔍 **Interactive series selection** when multiple matches are found

## Safety Features

- Preview mode shows exactly what will be renamed
- Automatic rollback script generation
- Confirmation prompt before execution
- Error handling and reporting
- 
----



# Universal TV Series Renamer

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/andres-zanzani/universal-tv-renamer)


**Script universale per rinominare automaticamente episodi di qualsiasi serie TV** interrogando **TMDB**, **TheTVDB** e **IMDb** per ottenere informazioni accurate sui titoli degli episodi.

## 🎯 Caratteristiche Principali

- 📺 **Universale**: Funziona con qualsiasi serie TV, non solo specifiche
- 🌐 **Multi-fonte**: Integrazione con TMDB, TheTVDB e IMDb
- 🗣️ **Interfaccia multilingue**: Italiano e Inglese
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
git clone https://github.com/andres-zanzani/universal-tv-renamer.git
cd universal-tv-renamer

# Installa le dipendenze
pip install requests

# Rendi eseguibile (Linux/macOS)
chmod +x tvrenamer.py
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
python3 tvrenamer.py /path/to/series

# Esecuzione reale
python3 tvrenamer.py /path/to/series --execute

# Con API key TMDB per risultati migliori
python3 tvrenamer.py /path/to/series --tmdb-key YOUR_API_KEY --execute
```

### Opzioni Avanzate

```bash
# Titoli episodi in inglese
python3 tvrenamer.py --language en /path/to/series --tmdb-key YOUR_KEY

# Interfaccia completamente in inglese
python3 tvrenamer.py --interface en --language en /path/to/series --tmdb-key YOUR_KEY

# Formato compatibile con Plex
python3 tvrenamer.py --format plex /path/to/series --tmdb-key YOUR_KEY --execute

# Ricerca ricorsiva nelle sottocartelle
python3 tvrenamer.py --recursive /path/to/series --tmdb-key YOUR_KEY --execute
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
| `--license` | - | - | Mostra informazioni sulla licenza |

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

## 🔧 Gestione Funzionalità Avanzate

### Duplicati
Quando lo script trova più file per lo stesso episodio:
```
⚠️  DUPLICATI RILEVATI: 1 episodi hanno più file

🔄 S02E03 - 2 file trovati:
   1. Serie.S02E03.720p.mkv (1.2 GB)
   2. Serie.S02E03.1080p.mkv (3.8 GB)
   0. ❌ Salta questo episodio
   a. ✅ Rinomina tutti i file (aggiungerà [Versione 2], [Versione 3], etc.)

Quale file tenere per S02E03? (1-2, 0, a):
```

**Opzioni:**
- **Numero (1-2)**: Mantiene solo il file scelto
- **0**: Salta completamente questo episodio
- **a**: Rinomina tutti i file aggiungendo `[Versione 2]`, `[Versione 3]`, etc.

### Episodi Mancanti
Lo script rileva automaticamente i "buchi" nella numerazione:
```
⚠️  EPISODI MANCANTI RILEVATI:
   📺 Stagione 1: Mancano E03, E07, E09
   📺 Stagione 2: Mancano E01, E05

💡 Suggerimento: Verifica se hai tutti gli episodi della serie
```

### Script di Rollback
Dopo ogni esecuzione riuscita, viene generato automaticamente `rollback_renamer.py`:
```bash
# Per ripristinare i nomi originali
python3 rollback_renamer.py
```

## 📋 Output Esempio

```
📺 Universal TV Series Renamer v1.0
👨‍💻 Sviluppato da: Andres Zanzani
📄 Licenza: GPL-3.0
==================================================
📁 Directory: /home/user/Series/Fallout
🎨 Formato: standard
🌍 Lingua episodi: en
🗣️ Lingua interfaccia: it
🔄 Ricorsivo: No
⚙️  Modalità: PREVIEW
==================================================
✅ TMDB API key configurata
✅ Autenticazione TheTVDB v4 riuscita

🔍 Ricerca in corso per: 'Fallout'
🔄 Ricerca su TMDB...

🔍 Risultati di ricerca per: 'Fallout'
================================================================================
 1. TMDB | Fallout | 2024 | ⭐ 8.4/10
    └─ The story of haves and have-nots in a world in which there's almost...

Seleziona (1-1, 0, r, q): 1

================================================================================
📋 PREVIEW - 10 file
================================================================================
NOME ORIGINALE                                    | NUOVO NOME                                          
--------------------------------------------------+----------------------------------------------------
Fallout.S01E01.The.End.2160p.AMZN.WEB-DL.mkv     | Fallout - [01x01] - The End.mkv
Fallout.S01E02.The.Target.2160p.AMZN.WEB-DL.mkv  | Fallout - [01x02] - The Target.mkv
--------------------------------------------------+----------------------------------------------------
📊 RISULTATI: ✅ 10 successi, ❌ 0 errori

💡 Per eseguire realmente le rinomine, aggiungi --execute
```

## 🎯 Formati File Supportati

**Estensioni video supportate:**
- `.mkv`, `.avi`, `.mp4`, `.m4v`
- `.mov`, `.wmv`, `.flv`, `.webm`
- `.ts`, `.m2ts`

**Pattern filename riconosciuti:**
- `Serie.S01E01.*.ext` (formato standard)
- `Serie.1x01.*.ext` (formato alternativo)
- `Serie.Season.1.Episode.01.*.ext` (formato esteso)
- `[Gruppo] Serie - 01 - Titolo [CRC].ext` (formato anime)

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

## 🤝 Contributi

I contributi sono benvenuti! Per contribuire:

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push del branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

### Aree di Miglioramento
- [ ] Supporto per più lingue nell'interfaccia
- [ ] Integrazione con altri database (AniDB, etc.)
- [ ] GUI grafica opzionale
- [ ] Supporto per film
- [ ] Plugin per media center

## 📝 Changelog

### v1.0 (2024)
- ✅ Prima release pubblica
- ✅ Supporto TMDB, TheTVDB, IMDb
- ✅ Interfaccia multilingue (IT/EN)
- ✅ 5 formati output
- ✅ Gestione duplicati e episodi mancanti
- ✅ Script di rollback automatico
- ✅ Tabella adattiva al terminale

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **GNU General Public License v3.0**.

```
Copyright (C) 2024 Andres Zanzani

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
```

Per il testo completo della licenza: [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html)

## 🙏 Ringraziamenti

- [TheTVDB](https://thetvdb.com/) per i dati delle serie TV
- [TheMovieDB](https://www.themoviedb.org/) per i dati aggiuntivi e le traduzioni
- [IMDb](https://www.imdb.com/) come fonte di fallback
- La comunità open source per le librerie utilizzate

## 📞 Supporto

Per bug, richieste di funzionalità o domande:
- 🐛 **Issues**: [GitHub Issues](https://github.com/buzzqw/Universal-TV-Series-Renamer/issues)

---

**⭐ Se ti piace questo progetto, lascia una stella su GitHub!**

Made with ❤️ by [Andres Zanzani](https://github.com/buzzqw)

Dona qualche spicciolo con PayPal! https://paypal.me/buzzqw?country.x=IT&locale.x=it_IT
