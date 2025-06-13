#!/usr/bin/env python3
"""
Universal TV Series Renamer
Script universale per rinominare episodi di qualsiasi serie TV
Interroga TheTVDB, TMDB e IMDb per ottenere informazioni automaticamente
Supporta anche la rinomina automatica dei sottotitoli

Copyright (C) 2024 Andres Zanzani

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Author: Andres Zanzani
License: GPL-3.0
Version: 1.1
"""

import os
import re
import json
import sys
import requests
import time
import html
import shutil
from pathlib import Path
from urllib.parse import quote

class TVSeriesRenamer:
    def __init__(self):
        # API Keys - IMPORTANTE: Registra le tue chiavi gratuite!
        self.tvdb_api_key = "fb51f9b848ffac9750bada89ecba0225"  # Key pubblica di tvnamer
        # Per TMDB: registrati su https://www.themoviedb.org/settings/api
        self.tmdb_api_key = None  # Inserisci la tua chiave TMDB qui
        self.tvdb_token = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UniversalTVRenamer/1.1',
            'Accept': 'application/json'
        })
        self.language = 'it'  # Lingua di default per episodi
        self.interface_language = 'it'  # Lingua interfaccia
        
        # Dizionari per i testi dell'interfaccia
        self.texts = {
            'it': {
                'header': "📺 Universal TV Series Renamer v1.1",
                'developer': "👨‍💻 Sviluppato da: Andres Zanzani",
                'license': "📄 Licenza: GPL-3.0",
                'directory': "📁 Directory:",
                'format': "🎨 Formato:",
                'episode_language': "🌍 Lingua episodi:",
                'interface_language': "🗣️ Lingua interfaccia:",
                'recursive': "🔄 Ricorsivo:",
                'mode': "⚙️  Modalità:",
                'preview': "PREVIEW",
                'execution': "ESECUZIONE",
                'yes': "Sì",
                'no': "No",
                'tmdb_configured': "✅ TMDB API key configurata",
                'tmdb_register': "⚠️  TMDB non configurato - registra una chiave gratuita su https://www.themoviedb.org/settings/api",
                'tvdb_auth_success': "✅ Autenticazione TheTVDB v4 riuscita",
                'tvdb_auth_error': "❌ Errore autenticazione TheTVDB:",
                'tvdb_not_available': "🔄 TheTVDB non disponibile, continuo con altre fonti",
                'searching_for': "🔍 Ricerca in corso per:",
                'searching_tmdb': "🔄 Ricerca su TMDB...",
                'searching_tvdb': "🔄 Ricerca su TheTVDB...",
                'searching_imdb': "🔄 Ricerca su IMDb...",
                'search_results': "🔍 Risultati di ricerca per:",
                'none_above': "❌ Nessuna delle opzioni sopra",
                'different_search': "🔄 Ricerca con nome diverso",
                'exit_program': "🚪 Esci dal programma",
                'select_option': "Seleziona ({}, 0, r, q):",
                'enter_new_name': "Inserisci nuovo nome per la ricerca",
                'user_exit': "👋 Uscita richiesta dall'utente",
                'invalid_selection': "❌ Selezione non valida!",
                'duplicates_found': "⚠️  DUPLICATI RILEVATI: {} episodi hanno più file",
                'episode_files_found': "🔄 S{:02d}E{:02d} - {} file trovati:",
                'skip_episode': "❌ Salta questo episodio",
                'rename_all_versions': "✅ Rinomina tutti i file (aggiungerà [Versione 2], [Versione 3], etc.)",
                'which_file_keep': "Quale file tenere per S{:02d}E{:02d}? (1-{}, 0, a):",
                'episodes_missing': "⚠️  EPISODI MANCANTI RILEVATI:",
                'season_missing': "📺 Stagione {}: Mancano {}",
                'verify_episodes': "💡 Suggerimento: Verifica se hai tutti gli episodi della serie",
                'no_files_process': "❌ Nessun file da processare dopo i controlli",
                'skip_unrecognized': "⚠️  SKIP: {} (formato non riconosciuto)",
                'title_not_found': "⚠️  Titolo non trovato per S{:02d}E{:02d}",
                'rollback_generated': "✅ Script di rollback generato: {}",
                'rollback_instructions': "💡 Per ripristinare i nomi originali, esegui:",
                'rollback_error': "❌ Errore nella generazione dello script di rollback: {}",
                'confirm_rename': "⚠️  ATTENZIONE: Rinominare {} file (video e sottotitoli)?",
                'confirm_prompt': "Confermi? [s/N]:",
                'cancelled': "❌ Annullato",
                'results_header': "📋 {} - {} file",
                'original_name': "NOME ORIGINALE",
                'new_name': "NUOVO NOME",
                'results_final': "📊 RISULTATI: ✅ {} successi, ❌ {} errori",
                'file_exists': "❌ File esiste già",
                'error': "❌ ERRORE:",
                'no_series_found': "❌ Nessuna serie trovata per: '{}'",
                'suggestions': "💡 Suggerimenti:",
                'check_spelling': "   - Verifica l'ortografia del nome",
                'try_english': "   - Prova con il nome originale in inglese",
                'use_shorter': "   - Usa un nome più breve",
                'video_files_found': "📹 File video trovati: {}",
                'subtitle_files_found': "📝 File sottotitoli trovati: {}",
                'subtitle_processed': "📝 Sottotitolo associato: {}",
                'subtitle_orphan': "⚠️  Sottotitolo orfano: {} (nessun video corrispondente)"
            },
            'en': {
                'header': "📺 Universal TV Series Renamer v1.1",
                'developer': "👨‍💻 Developed by: Andres Zanzani",
                'license': "📄 License: GPL-3.0",
                'directory': "📁 Directory:",
                'format': "🎨 Format:",
                'episode_language': "🌍 Episode language:",
                'interface_language': "🗣️ Interface language:",
                'recursive': "🔄 Recursive:",
                'mode': "⚙️  Mode:",
                'preview': "PREVIEW",
                'execution': "EXECUTION",
                'yes': "Yes",
                'no': "No",
                'tmdb_configured': "✅ TMDB API key configured",
                'tmdb_register': "⚠️  TMDB not configured - register a free key at https://www.themoviedb.org/settings/api",
                'tvdb_auth_success': "✅ TheTVDB v4 authentication successful",
                'tvdb_auth_error': "❌ TheTVDB authentication error:",
                'tvdb_not_available': "🔄 TheTVDB not available, continuing with other sources",
                'searching_for': "🔍 Searching for:",
                'searching_tmdb': "🔄 Searching TMDB...",
                'searching_tvdb': "🔄 Searching TheTVDB...",
                'searching_imdb': "🔄 Searching IMDb...",
                'search_results': "🔍 Search results for:",
                'none_above': "❌ None of the above options",
                'different_search': "🔄 Search with different name",
                'exit_program': "🚪 Exit program",
                'select_option': "Select ({}, 0, r, q):",
                'enter_new_name': "Enter new name for search",
                'user_exit': "👋 User requested exit",
                'invalid_selection': "❌ Invalid selection!",
                'duplicates_found': "⚠️  DUPLICATES DETECTED: {} episodes have multiple files",
                'episode_files_found': "🔄 S{:02d}E{:02d} - {} files found:",
                'skip_episode': "❌ Skip this episode",
                'rename_all_versions': "✅ Rename all files (will add [Version 2], [Version 3], etc.)",
                'which_file_keep': "Which file to keep for S{:02d}E{:02d}? (1-{}, 0, a):",
                'episodes_missing': "⚠️  MISSING EPISODES DETECTED:",
                'season_missing': "📺 Season {}: Missing {}",
                'verify_episodes': "💡 Suggestion: Check if you have all episodes of the series",
                'no_files_process': "❌ No files to process after checks",
                'skip_unrecognized': "⚠️  SKIP: {} (unrecognized format)",
                'title_not_found': "⚠️  Title not found for S{:02d}E{:02d}",
                'rollback_generated': "✅ Rollback script generated: {}",
                'rollback_instructions': "💡 To restore original names, run:",
                'rollback_error': "❌ Error generating rollback script: {}",
                'confirm_rename': "⚠️  WARNING: Rename {} files (video and subtitles)?",
                'confirm_prompt': "Confirm? [y/N]:",
                'cancelled': "❌ Cancelled",
                'results_header': "📋 {} - {} files",
                'original_name': "ORIGINAL NAME",
                'new_name': "NEW NAME",
                'results_final': "📊 RESULTS: ✅ {} successes, ❌ {} errors",
                'file_exists': "❌ File already exists",
                'error': "❌ ERROR:",
                'no_series_found': "❌ No series found for: '{}'",
                'suggestions': "💡 Suggestions:",
                'check_spelling': "   - Check the spelling of the name",
                'try_english': "   - Try with the original English name",
                'use_shorter': "   - Use a shorter name",
                'video_files_found': "📹 Video files found: {}",
                'subtitle_files_found': "📝 Subtitle files found: {}",
                'subtitle_processed': "📝 Subtitle associated: {}",
                'subtitle_orphan': "⚠️  Orphan subtitle: {} (no matching video)"
            }
        }

    def get_text(self, key, *args):
        """Ottiene il testo tradotto per la lingua dell'interfaccia"""
        text = self.texts.get(self.interface_language, self.texts['it']).get(key, key)
        if args:
            return text.format(*args)
        return text

    def authenticate_tvdb(self):
        """Autentica con TheTVDB API v4"""
        try:
            # API v4 con nuova autenticazione
            auth_url = "https://api4.thetvdb.com/v4/login"
            auth_data = {"apikey": self.tvdb_api_key}
            
            response = self.session.post(auth_url, json=auth_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.tvdb_token = data.get('data', {}).get('token')
                if self.tvdb_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.tvdb_token}'})
                    print(self.get_text('tvdb_auth_success'))
                    return True
            else:
                print(self.get_text('tvdb_auth_error'), response.status_code)
                
        except Exception as e:
            print(self.get_text('tvdb_auth_error'), e)
        
        # Fallback: disabilita TheTVDB
        print(self.get_text('tvdb_not_available'))
        return False

    def extract_series_info(self, filename):
        """Estrae il nome della serie dal filename"""
        # Rimuovi estensione
        name = Path(filename).stem
        
        # Pattern per rimuovere info episodio
        patterns_to_remove = [
            r'[Ss]\d+[Ee]\d+.*',  # S01E01...
            r'\d+x\d+.*',         # 1x01...
            r'[Ss]eason\s*\d+.*', # Season 1...
            r'[Ee]pisode\s*\d+.*', # Episode 1...
            r'\d{4}.*',           # Anno...
            r'(720p|1080p|480p|2160p|4K).*',  # Qualità video
            r'(HDTV|WEB-?DL|BluRay|BDRip|DVDRip).*',  # Fonte
            r'(x264|x265|H\.?264|H\.?265|XviD).*',  # Codec
            r'\[.*?\].*',         # [Release group]...
        ]
        
        series_name = name
        for pattern in patterns_to_remove:
            series_name = re.sub(pattern, '', series_name, flags=re.IGNORECASE)
        
        # Pulisci il nome
        series_name = re.sub(r'[._\-]+', ' ', series_name)
        series_name = re.sub(r'\s+', ' ', series_name).strip()
        
        return series_name

    def extract_episode_info(self, filename):
        """Estrae stagione e episodio dal filename"""
        patterns = [
            r'[Ss](\d+)[Ee](\d+)',
            r'(\d+)x(\d+)',
            r'[Ss]eason\s*(\d+).*[Ee]pisode\s*(\d+)',
            r'(\d+)\.(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return int(match.group(1)), int(match.group(2))
        
        return None, None

    def extract_subtitle_language(self, filename):
        """Estrae il codice lingua dal nome del sottotitolo"""
        filename_lower = filename.lower()
        
        # Pattern con gruppi di cattura
        patterns_with_groups = [
            r'\.([a-z]{2,3})\.srt$',  # .it.srt, .eng.srt
            r'\.([a-z]{2,3})\.sub$',  # .it.sub
            r'\.([a-z]{2,3})\.ass$',  # .it.ass
            r'\.([a-z]{2,3})\.ssa$',  # .it.ssa
            r'\.([a-z]{2,3})\.vtt$',  # .it.vtt
            r'\[([a-z]{2,3})\]',      # [it], [eng]
            r'_([a-z]{2,3})_',        # _it_, _eng_
        ]
        
        # Prova prima i pattern con gruppi
        for pattern in patterns_with_groups:
            match = re.search(pattern, filename_lower)
            if match:
                lang_code = match.group(1)
                # Normalizza alcuni codici comuni
                lang_mapping = {
                    'ita': 'it',
                    'eng': 'en',
                }
                return lang_mapping.get(lang_code, lang_code)
        
        # Pattern senza gruppi - controllo diretto
        if '.italian.' in filename_lower or '.italiani.' in filename_lower:
            return 'it'
        elif '.english.' in filename_lower:
            return 'en'
        elif '.iTALiAN.' in filename_lower:
            return 'it'
        elif '.ENGLISH.' in filename_lower:
            return 'en'
        
        return None

    def search_series_tmdb(self, series_name):
        """Cerca la serie su TMDB"""
        if not self.tmdb_api_key:
            return []
            
        try:
            search_url = "https://api.themoviedb.org/3/search/tv"
            params = {
                'api_key': self.tmdb_api_key,
                'query': series_name,
                'language': f'{self.language}-{self.language.upper()}'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('results', [])[:5]:  # Prime 5 corrispondenze
                    result = {
                        'id': item.get('id'),
                        'name': item.get('name', item.get('original_name', 'Nome non disponibile')),
                        'year': item.get('first_air_date', '')[:4] if item.get('first_air_date') else '',
                        'overview': item.get('overview', ''),
                        'source': 'TMDB',
                        'original_name': item.get('original_name', ''),
                        'vote_average': item.get('vote_average', 0)
                    }
                    results.append(result)
                
                return results
            else:
                print(f"❌ Errore ricerca TMDB: {response.status_code}")
                if response.status_code == 401:
                    if self.interface_language == 'en':
                        print("   💡 Register a free API key at https://www.themoviedb.org/settings/api")
                    else:
                        print("   💡 Registra una API key gratuita su https://www.themoviedb.org/settings/api")
                
        except Exception as e:
            if self.interface_language == 'en':
                print(f"❌ Error in TMDB search: {e}")
            else:
                print(f"❌ Errore nella ricerca TMDB: {e}")
        
        return []

    def search_series_tvdb(self, series_name):
        """Cerca la serie su TheTVDB"""
        if not self.tvdb_token:
            return []
            
        try:
            search_url = f"https://api4.thetvdb.com/v4/search"
            params = {
                'query': series_name,
                'type': 'series',
                'limit': 10
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('data', []):
                    result = {
                        'id': item.get('tvdb_id', item.get('id')),
                        'name': item.get('name', item.get('translations', {}).get('ita', item.get('translations', {}).get('eng', 'Nome non disponibile'))),
                        'year': item.get('year', ''),
                        'overview': item.get('overview', ''),
                        'source': 'TheTVDB',
                        'country': item.get('country', ''),
                        'status': item.get('status', {}).get('name', '') if isinstance(item.get('status'), dict) else item.get('status', '')
                    }
                    results.append(result)
                
                return results
            else:
                print(f"❌ Errore ricerca TheTVDB: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Errore nella ricerca TheTVDB: {e}")
        
        return []

    def search_series_imdb_web(self, series_name):
        """Ricerca serie tramite web scraping IMDb (fallback)"""
        try:
            search_url = f"https://www.imdb.com/find"
            params = {'q': series_name, 's': 'tt', 'ttype': 'tv'}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse semplificato dei risultati HTML
                content = response.text
                results = []
                
                # Cerca pattern per titoli di serie TV
                title_pattern = r'<a[^>]*href="/title/(tt\d+)[^>]*>([^<]+)</a>'
                matches = re.findall(title_pattern, content)
                
                for imdb_id, title in matches[:5]:  # Prime 5 corrispondenze
                    # Decodifica caratteri HTML
                    title = html.unescape(title)
                    results.append({
                        'id': imdb_id,
                        'name': title.strip(),
                        'source': 'IMDb',
                        'year': '',  # IMDb web scraping limitato
                        'overview': ''
                    })
                
                return results
                
        except Exception as e:
            print(f"⚠️  Errore ricerca IMDb: {e}")
        
        return []

    def get_episode_info_tmdb(self, series_id, season, episode):
        """Ottieni informazioni episodio da TMDB"""
        if not self.tmdb_api_key:
            return None
            
        try:
            episode_url = f"https://api.themoviedb.org/3/tv/{series_id}/season/{season}/episode/{episode}"
            
            # Prima prova nella lingua selezionata
            params = {
                'api_key': self.tmdb_api_key,
                'language': f'{self.language}-{self.language.upper()}'
            }
            
            response = self.session.get(episode_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('name', f'Episode {episode}'),
                    'overview': data.get('overview', ''),
                    'airDate': data.get('air_date', ''),
                    'season': season,
                    'episode': episode,
                    'vote_average': data.get('vote_average', 0),
                    'language': f'{self.language}-{self.language.upper()}'
                }
            
            # Se non trova nella lingua selezionata, prova in inglese
            if response.status_code == 404:
                params['language'] = 'en-US'
                response = self.session.get(episode_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'title': data.get('name', f'Episode {episode}'),
                        'overview': data.get('overview', ''),
                        'airDate': data.get('air_date', ''),
                        'season': season,
                        'episode': episode,
                        'vote_average': data.get('vote_average', 0),
                        'language': 'en-US'
                    }
                        
        except Exception as e:
            print(f"❌ Errore recupero episodio TMDB: {e}")
        
        return None

    def get_episode_info_tvdb(self, series_id, season, episode):
        """Ottieni informazioni episodio da TheTVDB"""
        if not self.tvdb_token:
            return None
            
        try:
            # Prima ottieni la serie
            series_url = f"https://api4.thetvdb.com/v4/series/{series_id}/episodes/default"
            params = {'season': season, 'page': 0}
            
            response = self.session.get(series_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                episodes = data.get('data', {}).get('episodes', [])
                
                for ep in episodes:
                    if ep.get('seasonNumber') == season and ep.get('number') == episode:
                        return {
                            'title': ep.get('name', f'Episode {episode}'),
                            'overview': ep.get('overview', ''),
                            'airDate': ep.get('aired', ''),
                            'season': season,
                            'episode': episode
                        }
                        
        except Exception as e:
            print(f"❌ Errore recupero episodio TheTVDB: {e}")
        
        return None

    def interactive_series_selection(self, results, series_name):
        """Interfaccia interattiva per selezione serie"""
        if not results:
            print(self.get_text('no_series_found', series_name))
            print(f"\n{self.get_text('suggestions')}")
            print(self.get_text('check_spelling'))
            print(self.get_text('try_english'))
            print(self.get_text('use_shorter'))
            return None
        
        print(f"\n{self.get_text('search_results')} '{series_name}'")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            name = result.get('name', 'Nome non disponibile')
            year = result.get('year', '')
            source = result.get('source', 'Unknown')
            overview = result.get('overview', '')
            
            # Decodifica caratteri HTML
            name = html.unescape(name)
            overview = html.unescape(overview) if overview else ''
            
            # Riga compatta: Fonte, Nome, Anno, Voto
            line1 = f"{i:2d}. {source}"
            if name:
                line1 += f" | {name}"
            if year:
                line1 += f" | {year}"
            if source == 'TMDB' and result.get('vote_average'):
                line1 += f" | ⭐ {result['vote_average']:.1f}/10"
            elif source == 'TheTVDB' and result.get('status'):
                line1 += f" | {result['status']}"
            
            print(line1)
            
            # Trama solo se presente e non troppo lunga
            if overview:
                overview_short = overview[:100] + "..." if len(overview) > 100 else overview
                print(f"    └─ {overview_short}")
            
            # Spazio tra risultati solo se c'è trama
            if overview:
                print()
        
        print(f"0. {self.get_text('none_above')}")
        print(f"r. {self.get_text('different_search')}")
        print(f"q. {self.get_text('exit_program')}")
        
        while True:
            try:
                choice = input(self.get_text('select_option', f"1-{len(results)}")).strip().lower()
                
                if choice == '0':
                    return None
                elif choice == 'r':
                    new_name = input(f"{self.get_text('enter_new_name')}: ").strip()
                    if new_name:
                        return self.search_and_select_series(new_name)
                    continue
                elif choice == 'q':
                    print(self.get_text('user_exit'))
                    sys.exit(0)
                else:
                    choice_num = int(choice) - 1
                    if 0 <= choice_num < len(results):
                        return results[choice_num]
                    else:
                        print(self.get_text('invalid_selection'))
                        
            except (ValueError, KeyboardInterrupt):
                if choice == 'q':
                    sys.exit(0)
                print(self.get_text('invalid_selection'))
            except KeyboardInterrupt:
                print(f"\n{self.get_text('user_exit')}")
                sys.exit(0)

    def search_and_select_series(self, series_name):
        """Cerca e seleziona una serie da tutte le fonti"""
        print(f"\n{self.get_text('searching_for')} '{series_name}'")
        
        all_results = []
        
        # Cerca su TMDB prima (di solito ha dati migliori)
        if self.tmdb_api_key:
            print(self.get_text('searching_tmdb'))
            tmdb_results = self.search_series_tmdb(series_name)
            all_results.extend(tmdb_results)
        
        # Poi TheTVDB
        if self.tvdb_token:
            print(self.get_text('searching_tvdb'))
            tvdb_results = self.search_series_tvdb(series_name)
            all_results.extend(tvdb_results)
        
        # Infine IMDb come fallback
        if len(all_results) < 3:  # Solo se non abbiamo abbastanza risultati
            print(self.get_text('searching_imdb'))
            imdb_results = self.search_series_imdb_web(series_name)
            all_results.extend(imdb_results)
        
        # Rimuovi duplicati basati sul nome
        seen_names = set()
        unique_results = []
        for result in all_results:
            name_key = result['name'].lower().replace(' ', '').replace("'", "")
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_results.append(result)
        
        return self.interactive_series_selection(unique_results, series_name)

    def generate_filename(self, series_name, season, episode, episode_title, original_ext, format_style="standard"):
        """Genera il nuovo nome file"""
        series_name = self.clean_filename(series_name)
        episode_title = self.clean_filename(episode_title)
        
        formats = {
            "standard": f"{series_name} - [{season:02d}x{episode:02d}] - {episode_title}{original_ext}",
            "plex": f"{series_name} - S{season:02d}E{episode:02d} - {episode_title}{original_ext}",
            "simple": f"{series_name} {season}x{episode:02d} {episode_title}{original_ext}",
            "minimal": f"{series_name} S{season:02d}E{episode:02d}{original_ext}",
            "kodi": f"{series_name} S{season:02d}E{episode:02d} {episode_title}{original_ext}"
        }
        
        return formats.get(format_style, formats["standard"])

    def generate_subtitle_filename(self, video_filename, subtitle_ext, language_code=None, version_suffix=""):
        """Genera il nome del file sottotitolo basato sul video"""
        # Rimuovi l'estensione dal nome del video
        video_base = Path(video_filename).stem
        
        # Aggiungi suffisso versione se presente
        if version_suffix:
            video_base = f"{video_base}{version_suffix}"
        
        # Aggiungi codice lingua se presente
        if language_code:
            return f"{video_base}.{language_code}{subtitle_ext}"
        else:
            return f"{video_base}{subtitle_ext}"

    def clean_filename(self, name):
        """Pulisce il nome file da caratteri non validi"""
        # Decodifica caratteri HTML
        name = html.unescape(name)
        
        # Caratteri non permessi
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')
        
        # Sostituisci caratteri problematici
        name = name.replace('&', 'and')
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name

    def find_media_files(self, directory):
        """Trova file video e sottotitoli nella directory"""
        video_extensions = {'.mkv', '.avi', '.mp4', '.m4v', '.mov', '.wmv', '.flv', '.webm', '.ts', '.m2ts'}
        subtitle_extensions = {'.srt', '.sub', '.ass', '.ssa', '.vtt', '.idx', '.sup'}
        
        video_files = []
        subtitle_files = []
        
        path = Path(directory)
        file_iterator = path.rglob('*') if getattr(self, 'recursive', False) else path.iterdir()
        
        for file_path in file_iterator:
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in video_extensions:
                    video_files.append(file_path)
                elif ext in subtitle_extensions:
                    subtitle_files.append(file_path)
        
        return sorted(video_files), sorted(subtitle_files)

    def match_subtitles_to_videos(self, video_files, subtitle_files):
        """Associa i sottotitoli ai file video corrispondenti"""
        video_subtitle_map = {}
        orphan_subtitles = []
        
        for video_file in video_files:
            video_subtitle_map[video_file] = []
        
        for subtitle_file in subtitle_files:
            # Estrai informazioni dal sottotitolo
            sub_season, sub_episode = self.extract_episode_info(subtitle_file.name)
            sub_language = self.extract_subtitle_language(subtitle_file.name)
            
            if sub_season is None or sub_episode is None:
                orphan_subtitles.append(subtitle_file)
                continue
            
            # Trova il video corrispondente
            matching_video = None
            for video_file in video_files:
                vid_season, vid_episode = self.extract_episode_info(video_file.name)
                if vid_season == sub_season and vid_episode == sub_episode:
                    matching_video = video_file
                    break
            
            if matching_video:
                video_subtitle_map[matching_video].append({
                    'file': subtitle_file,
                    'language': sub_language,
                    'season': sub_season,
                    'episode': sub_episode
                })
                print(self.get_text('subtitle_processed', subtitle_file.name))
            else:
                orphan_subtitles.append(subtitle_file)
        
        # Mostra sottotitoli orfani
        for orphan in orphan_subtitles:
            print(self.get_text('subtitle_orphan', orphan.name))
        
        return video_subtitle_map

    def process_files(self, directory, format_style="standard", dry_run=True):
        """Processa tutti i file nella directory"""
        video_files, subtitle_files = self.find_media_files(directory)
        
        if not video_files and not subtitle_files:
            print("❌ Nessun file video o sottotitolo trovato!")
            return
        
        print(f"\n{self.get_text('video_files_found', len(video_files))}")
        print(f"{self.get_text('subtitle_files_found', len(subtitle_files))}")
        
        # Associa sottotitoli ai video
        video_subtitle_map = self.match_subtitles_to_videos(video_files, subtitle_files)
        
        # Raggruppa file per serie (basato sul nome estratto)
        series_groups = {}
        for video_file in video_files:
            series_name = self.extract_series_info(video_file.name)
            if series_name not in series_groups:
                series_groups[series_name] = {
                    'videos': [],
                    'subtitles': []
                }
            series_groups[series_name]['videos'].append(video_file)
            # Aggiungi i sottotitoli associati
            series_groups[series_name]['subtitles'].extend(video_subtitle_map.get(video_file, []))
        
        print(f"📊 Rilevate {len(series_groups)} serie diverse")
        
        # Processa ogni serie
        for series_name, files in series_groups.items():
            print(f"\n{'='*80}")
            video_count = len(files['videos'])
            subtitle_count = len(files['subtitles'])
            print(f"📺 SERIE: {series_name} ({video_count} video, {subtitle_count} sottotitoli)")
            print(f"{'='*80}")
            
            # Cerca e seleziona la serie
            selected_series = self.search_and_select_series(series_name)
            if not selected_series:
                print(f"⏭️  Saltando serie: {series_name}")
                continue
            
            # Seleziona formato
            if not dry_run:
                format_style = self.select_format_style()
            
            # Processa i file di questa serie
            self.process_series_files(files['videos'], video_subtitle_map, selected_series, format_style, dry_run)

    def select_format_style(self):
        """Seleziona lo stile di formattazione"""
        formats = {
            "1": ("standard", "Serie - [01x01] - Episodio.mkv"),
            "2": ("plex", "Serie - S01E01 - Episodio.mkv"),
            "3": ("simple", "Serie 1x01 Episodio.mkv"),
            "4": ("minimal", "Serie S01E01.mkv"),
            "5": ("kodi", "Serie S01E01 Episodio.mkv")
        }
        
        print("\n🎨 Scegli il formato del nome file:")
        for key, (style, example) in formats.items():
            print(f"{key}. {style.upper()}: {example}")
        
        while True:
            choice = input("Scegli formato (1-5): ").strip()
            if choice in formats:
                style, _ = formats[choice]
                print(f"✅ Formato selezionato: {style}")
                return style
            print("❌ Scelta non valida!")

    def check_duplicates_and_gaps(self, files, selected_series):
        """Controlla duplicati e episodi mancanti"""
        episodes_found = {}
        duplicates = []
        
        # Analizza tutti i file
        for file_path in files:
            season, episode = self.extract_episode_info(file_path.name)
            if season is not None and episode is not None:
                key = (season, episode)
                if key not in episodes_found:
                    episodes_found[key] = []
                episodes_found[key].append(file_path)
        
        # Trova duplicati
        for (season, episode), file_list in episodes_found.items():
            if len(file_list) > 1:
                duplicates.append((season, episode, file_list))
        
        # Gestisci duplicati
        if duplicates:
            print(f"\n{self.get_text('duplicates_found', len(duplicates))}")
            for season, episode, file_list in duplicates:
                print(f"\n{self.get_text('episode_files_found', season, episode, len(file_list))}")
                for i, file_path in enumerate(file_list, 1):
                    size = file_path.stat().st_size / (1024**3)  # Size in GB
                    print(f"   {i}. {file_path.name} ({size:.1f} GB)")
                
                print(f"   0. {self.get_text('skip_episode')}")
                print(f"   a. {self.get_text('rename_all_versions')}")
                
                while True:
                    try:
                        choice = input(self.get_text('which_file_keep', season, episode, len(file_list))).strip().lower()
                        
                        if choice == '0':
                            # Rimuovi tutti i file di questo episodio dalla lista
                            for f in file_list:
                                if f in files:
                                    files.remove(f)
                            break
                        elif choice == 'a':
                            # Mantieni tutti i file, verranno rinominati con suffisso
                            break
                        else:
                            choice_num = int(choice) - 1
                            if 0 <= choice_num < len(file_list):
                                # Mantieni solo il file scelto
                                chosen_file = file_list[choice_num]
                                for f in file_list:
                                    if f != chosen_file and f in files:
                                        files.remove(f)
                                break
                            else:
                                print(self.get_text('invalid_selection'))
                    except (ValueError, KeyboardInterrupt):
                        print(self.get_text('invalid_selection'))
        
        # Controlla episodi mancanti
        if episodes_found:
            seasons_found = {}
            for (season, episode), _ in episodes_found.items():
                if season not in seasons_found:
                    seasons_found[season] = []
                seasons_found[season].append(episode)
            
            gaps_found = []
            for season, episodes in seasons_found.items():
                episodes.sort()
                if len(episodes) > 1:  # Solo se ci sono almeno 2 episodi
                    min_ep, max_ep = min(episodes), max(episodes)
                    expected_episodes = set(range(min_ep, max_ep + 1))
                    missing_episodes = expected_episodes - set(episodes)
                    
                    if missing_episodes:
                        gaps_found.append((season, sorted(missing_episodes)))
            
            if gaps_found:
                print(f"\n{self.get_text('episodes_missing')}")
                for season, missing in gaps_found:
                    missing_str = ', '.join([f"E{ep:02d}" for ep in missing])
                    print(f"   {self.get_text('season_missing', season, missing_str)}")
                
                print(f"\n{self.get_text('verify_episodes')}")
        
        return files

    def process_series_files(self, video_files, video_subtitle_map, selected_series, format_style, dry_run):
        """Processa i file di una specifica serie (video e sottotitoli)"""
        series_id = selected_series.get('id')
        series_name = selected_series.get('name')
        source = selected_series.get('source')
        
        # Controllo duplicati e episodi mancanti
        video_files = self.check_duplicates_and_gaps(video_files, selected_series)
        
        if not video_files:
            print(self.get_text('no_files_process'))
            return
        
        renames = []
        duplicate_counter = {}
        
        for video_file in video_files:
            season, episode = self.extract_episode_info(video_file.name)
            
            if season is None or episode is None:
                print(self.get_text('skip_unrecognized', video_file.name))
                continue
            
            # Ottieni info episodio dalla fonte selezionata
            episode_info = None
            
            if source == 'TMDB':
                episode_info = self.get_episode_info_tmdb(series_id, season, episode)
            elif source == 'TheTVDB':
                episode_info = self.get_episode_info_tvdb(series_id, season, episode)
            
            # Se non trova info, prova l'altra fonte
            if not episode_info and source == 'TMDB':
                episode_info = self.get_episode_info_tvdb(series_id, season, episode)
            elif not episode_info and source == 'TheTVDB':
                episode_info = self.get_episode_info_tmdb(series_id, season, episode)
            
            if episode_info:
                episode_title = episode_info['title']
            else:
                episode_title = f"Episode {episode}"
            
            # Gestione duplicati - aggiungi suffisso se necessario
            base_name = self.generate_filename(
                series_name, season, episode, episode_title, 
                video_file.suffix, format_style
            )
            
            # Controlla se questo nome base è già stato usato
            key = (season, episode)
            version_suffix = ""
            if key in duplicate_counter:
                duplicate_counter[key] += 1
                # Il secondo file è [Versione 2], il terzo [Versione 3], etc.
                version_number = duplicate_counter[key]
                version_suffix = f" [Versione {version_number}]"
                
                # Aggiungi suffisso prima dell'estensione
                name_part, ext = base_name.rsplit('.', 1) if '.' in base_name else (base_name, '')
                new_video_name = f"{name_part}{version_suffix}.{ext}" if ext else f"{name_part}{version_suffix}"
            else:
                duplicate_counter[key] = 1
                new_video_name = base_name
            
            # Aggiungi il video alle rinomine
            renames.append((video_file, new_video_name))
            
            # Processa i sottotitoli associati a questo video
            subtitles_for_video = video_subtitle_map.get(video_file, [])
            for subtitle_info in subtitles_for_video:
                subtitle_file = subtitle_info['file']
                subtitle_language = subtitle_info['language']
                
                # Genera il nome del sottotitolo basato sul nuovo nome del video
                new_subtitle_name = self.generate_subtitle_filename(
                    new_video_name, 
                    subtitle_file.suffix, 
                    subtitle_language, 
                    version_suffix
                )
                
                renames.append((subtitle_file, new_subtitle_name))
        
        # Esegui rinomine
        if renames:
            self.execute_renames(renames, dry_run)

    def get_terminal_width(self):
        """Ottiene la larghezza del terminale"""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 120  # Fallback se non riesce a rilevare

    def generate_rollback_script(self, renames, directory):
        """Genera uno script Python per ripristinare i nomi originali"""
        script_content = '''#!/usr/bin/env python3
"""
Rollback Script - Universal TV Series Renamer
Script automatico per ripristinare i nomi file originali (video e sottotitoli)

Copyright (C) 2024 Andres Zanzani
Licenza: GPL-3.0

ATTENZIONE: Questo script ripristinerà i nomi file originali.
Eseguire solo se si desidera annullare le rinomine effettuate.
"""

import os
import sys
from pathlib import Path

def main():
    print("🔄 Universal TV Renamer - Script di Rollback")
    print("👨‍💻 Sviluppato da: Andres Zanzani")
    print("📄 Licenza: GPL-3.0")
    print("=" * 50)
    
    # Lista delle rinomine da ripristinare (nuovo_nome -> nome_originale)
    renames = {
'''
        
        # Aggiungi tutte le rinomine al dizionario
        for old_path, new_name in renames:
            old_name = old_path.name.replace("'", "\\'")  # Escape apostrofi
            new_name_escaped = new_name.replace("'", "\\'")
            script_content += f"        '{new_name_escaped}': '{old_name}',\n"
        
        script_content += '''    }
    
    current_dir = Path(__file__).parent
    
    print(f"📁 Directory di lavoro: {current_dir}")
    print(f"📊 File da ripristinare: {len(renames)}")
    print()
    
    # Controlla se i file esistono
    files_found = []
    files_missing = []
    
    for new_name, old_name in renames.items():
        new_path = current_dir / new_name
        if new_path.exists():
            files_found.append((new_path, old_name))
        else:
            files_missing.append(new_name)
    
    if files_missing:
        print(f"⚠️  ATTENZIONE: {len(files_missing)} file non trovati:")
        for missing in files_missing[:5]:  # Mostra solo i primi 5
            print(f"   ❌ {missing}")
        if len(files_missing) > 5:
            print(f"   ... e altri {len(files_missing) - 5} file")
        print()
    
    if not files_found:
        print("❌ ERRORE: Nessun file da ripristinare trovato!")
        print("💡 Suggerimento: Assicurati di eseguire lo script nella directory corretta")
        input("Premi Enter per uscire...")
        sys.exit(1)
    
    print(f"✅ Trovati {len(files_found)} file da ripristinare")
    print()
    
    # Separa video e sottotitoli per il conteggio
    video_exts = {'.mkv', '.avi', '.mp4', '.m4v', '.mov', '.wmv', '.flv', '.webm', '.ts', '.m2ts'}
    subtitle_exts = {'.srt', '.sub', '.ass', '.ssa', '.vtt', '.idx', '.sup'}
    
    videos = []
    subtitles = []
    
    for new_path, old_name in files_found:
        if new_path.suffix.lower() in video_exts:
            videos.append((new_path, old_name))
        elif new_path.suffix.lower() in subtitle_exts:
            subtitles.append((new_path, old_name))
    
    print(f"📹 Video: {len(videos)}")
    print(f"📝 Sottotitoli: {len(subtitles)}")
    print()
    
    # Mostra anteprima delle prime 5 rinomine
    print("📋 Anteprima delle rinomine (prime 5):")
    print("-" * 80)
    for i, (new_path, old_name) in enumerate(files_found[:5]):
        file_type = "📹" if new_path.suffix.lower() in video_exts else "📝"
        print(f"{i+1:2d}. {file_type} {new_path.name}")
        print(f"    ↳ {old_name}")
    
    if len(files_found) > 5:
        print(f"    ... e altri {len(files_found) - 5} file")
    print("-" * 80)
    
    # Conferma dall'utente
    while True:
        response = input(f"\\n⚠️  Ripristinare {len(files_found)} file? [s/N]: ").strip().lower()
        if response in ['s', 'si', 'sì', 'y', 'yes']:
            break
        elif response in ['n', 'no', ''] or response == '':
            print("❌ Operazione annullata dall'utente")
            input("Premi Enter per uscire...")
            sys.exit(0)
        else:
            print("❌ Risposta non valida. Inserisci 's' per Sì o 'n' per No")
    
    # Esegui il rollback
    print("\\n🔄 Ripristino in corso...")
    success_count = 0
    error_count = 0
    
    for new_path, old_name in files_found:
        old_path = current_dir / old_name
        
        try:
            # Controlla se il file di destinazione esiste già
            if old_path.exists():
                print(f"⚠️  SKIP: {old_name} (esiste già)")
                error_count += 1
                continue
            
            # Esegui la rinomina
            new_path.rename(old_path)
            file_type = "📹" if new_path.suffix.lower() in video_exts else "📝"
            print(f"✅ {file_type} {new_path.name} → {old_name}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ ERRORE: {new_path.name} - {e}")
            error_count += 1
    
    print("\\n" + "=" * 50)
    print(f"📊 RISULTATI FINALI:")
    print(f"   ✅ Ripristinati con successo: {success_count}")
    print(f"   ❌ Errori: {error_count}")
    
    if success_count > 0:
        print("\\n🎉 Rollback completato!")
    else:
        print("\\n❌ Nessun file è stato ripristinato")
    
    print("\\n💡 Questo script può essere eliminato se non serve più il rollback")
    input("\\nPremi Enter per uscire...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\n👋 Operazione interrotta dall'utente")
        sys.exit(0)
    except Exception as e:
        print(f"\\n\\n❌ ERRORE CRITICO: {e}")
        input("Premi Enter per uscire...")
        sys.exit(1)
'''
        
        # Scrivi lo script nella directory di destinazione
        script_path = Path(directory) / "rollback_renamer.py"
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Rendi eseguibile su Linux/Mac
            if os.name != 'nt':  # Non Windows
                import stat
                script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            print(self.get_text('rollback_generated', script_path))
            print(self.get_text('rollback_instructions'))
            if os.name == 'nt':  # Windows
                print(f"   python \"{script_path}\"")
            else:  # Linux/Mac
                print(f"   python3 \"{script_path}\"")
                print(f"   oppure: ./{script_path.name}")
            
        except Exception as e:
            print(self.get_text('rollback_error', e))

    def execute_renames(self, renames, dry_run=True):
        """Esegue le rinomine con formato tabella adattivo"""
        if not renames:
            return
        
        if not dry_run:
            confirm_text = self.get_text('confirm_rename', len(renames))
            prompt_text = self.get_text('confirm_prompt')
            
            print(f"\n{confirm_text}")
            response = input(prompt_text).strip().lower()
            
            valid_yes = ['s', 'si', 'sì', 'y', 'yes'] if self.interface_language == 'it' else ['y', 'yes', 's', 'si', 'sì']
            
            if response not in valid_yes:
                print(self.get_text('cancelled'))
                return
        
        terminal_width = self.get_terminal_width()
        separator_width = 3  # " | "
        
        # Calcola la larghezza ottimale delle colonne
        max_old_len = max(len(str(old_path.name)) for old_path, _ in renames)
        max_new_len = max(len(new_name) for _, new_name in renames)
        
        # Distribuisci lo spazio disponibile proporzionalmente
        available_width = terminal_width - separator_width - 2  # -2 per margini
        
        # Se entrambi i nomi stanno nel terminale, usa le lunghezze naturali
        if max_old_len + max_new_len + separator_width <= terminal_width:
            old_width = max_old_len
            new_width = max_new_len
        else:
            # Altrimenti distribuisci proporzionalmente
            total_content = max_old_len + max_new_len
            old_ratio = max_old_len / total_content
            new_ratio = max_new_len / total_content
            
            old_width = max(30, int(available_width * old_ratio))  # Minimo 30 caratteri
            new_width = available_width - old_width
        
        print(f"\n{'='*terminal_width}")
        header_text = self.get_text('results_header', 
                                   self.get_text('execution') if not dry_run else self.get_text('preview'), 
                                   len(renames))
        print(header_text)
        print(f"{'='*terminal_width}")
        
        # Header tabella
        old_header = self.get_text('original_name')
        new_header = self.get_text('new_name')
        print(f"{old_header:<{old_width}} | {new_header:<{new_width}}")
        print(f"{'-'*old_width}-+-{'-'*new_width}")
        
        # Separatori per tipo di file
        video_extensions = {'.mkv', '.avi', '.mp4', '.m4v', '.mov', '.wmv', '.flv', '.webm', '.ts', '.m2ts'}
        subtitle_extensions = {'.srt', '.sub', '.ass', '.ssa', '.vtt', '.idx', '.sup'}
        
        success = 0
        errors = 0
        
        for old_path, new_name in renames:
            new_path = old_path.parent / new_name
            
            # Determina il tipo di file e aggiungi icona
            file_ext = old_path.suffix.lower()
            if file_ext in video_extensions:
                icon = "📹"
            elif file_ext in subtitle_extensions:
                icon = "📝"
            else:
                icon = "📄"
            
            # Tronca i nomi se necessario
            old_display = f"{icon} {self.truncate_filename(old_path.name, old_width - 2)}"
            new_display = f"{icon} {self.truncate_filename(new_name, new_width - 2)}"
            
            try:
                if dry_run:
                    print(f"{old_display:<{old_width}} | {new_display:<{new_width}}")
                    success += 1
                else:
                    if new_path.exists():
                        error_msg = f"{icon} {self.truncate_filename(self.get_text('file_exists'), new_width - 2)}"
                        print(f"{old_display:<{old_width}} | {error_msg:<{new_width}}")
                        errors += 1
                        continue
                    
                    old_path.rename(new_path)
                    print(f"{old_display:<{old_width}} | {new_display:<{new_width}}")
                    success += 1
                    
            except Exception as e:
                error_text = f"{self.get_text('error')} {str(e)}"
                error_msg = f"{icon} {self.truncate_filename(error_text, new_width - 2)}"
                print(f"{old_display:<{old_width}} | {error_msg:<{new_width}}")
                errors += 1
        
        print(f"{'-'*old_width}-+-{'-'*new_width}")
        print(self.get_text('results_final', success, errors))
        
        # Genera script di rollback solo se ci sono stati successi e non è dry run
        if not dry_run and success > 0:
            directory = renames[0][0].parent  # Prendi la directory dal primo file
            self.generate_rollback_script(renames, directory)

    def truncate_filename(self, filename, max_width):
        """Tronca intelligentemente il nome del file"""
        if len(filename) <= max_width:
            return filename
        
        if max_width <= 3:
            return "..."
        
        # Prova a mantenere l'estensione se possibile
        if '.' in filename:
            name, ext = filename.rsplit('.', 1)
            ext = '.' + ext
            
            # Se l'estensione è ragionevole e c'è spazio
            if len(ext) <= 6 and len(ext) < max_width - 5:
                available_for_name = max_width - len(ext) - 3  # -3 per "..."
                if available_for_name > 0:
                    return name[:available_for_name] + "..." + ext
        
        # Fallback: tronca semplicemente
        return filename[:max_width-3] + "..."


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Universal TV Series Renamer v1.1 - by Andres Zanzani",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Universal TV Series Renamer v1.1
Copyright (C) 2024 Andres Zanzani
Licenza: GPL-3.0

NOVITÀ v1.1:
✅ Supporto completo per sottotitoli (.srt, .sub, .ass, .ssa, .vtt)
✅ Riconoscimento automatico delle lingue nei sottotitoli
✅ Associazione intelligente sottotitoli-video
✅ Gestione sottotitoli orfani
✅ Script di rollback include i sottotitoli

Esempi di utilizzo:

  # Preview sicura (mostra video e sottotitoli)
  python3 tv_renamer.py /path/to/series

  # Esecuzione reale (rinomina video e sottotitoli)
  python3 tv_renamer.py /path/to/series --execute

  # Ricerca ricorsiva in sottocartelle
  python3 tv_renamer.py /path/to/series --recursive --execute

  # Formato specifico con TMDB
  python3 tv_renamer.py /path/to/series --tmdb-key YOUR_KEY --format plex --execute

Esempi di sottotitoli supportati:
  - Meglio.Di.Noi.1x07.srt → Serie - [01x07] - Titolo Episodio.srt
  - Meglio.Di.Noi.1x07.it.srt → Serie - [01x07] - Titolo Episodio.it.srt
  - Meglio.Di.Noi.1x07.iTALiAN.srt → Serie - [01x07] - Titolo Episodio.it.srt

Questo software è distribuito sotto licenza GPL-3.0.
Per maggiori informazioni: https://www.gnu.org/licenses/gpl-3.0.html
        """
    )
    
    parser.add_argument('directory', 
                       help='Directory contenente i file video e sottotitoli')
    parser.add_argument('--execute', action='store_true',
                       help='Esegui realmente le rinomine (default: solo preview)')
    parser.add_argument('--format', choices=['standard', 'plex', 'simple', 'minimal', 'kodi'],
                       default='standard',
                       help='Formato del nome file (default: standard)')
    parser.add_argument('--recursive', action='store_true',
                       help='Cerca ricorsivamente nelle sottocartelle')
    parser.add_argument('--language', choices=['it', 'en', 'es', 'fr', 'de'], 
                       default='it', help='Lingua per i titoli degli episodi')
    parser.add_argument('--interface', choices=['it', 'en'], 
                       default='it', help='Lingua dell\'interfaccia del programma')
    parser.add_argument('--tmdb-key', help='API key per TMDB (opzionale)')
    parser.add_argument('--version', action='version', 
                       version='Universal TV Series Renamer v1.1 - Copyright (C) 2024 Andres Zanzani - GPL-3.0')
    parser.add_argument('--license', action='store_true', 
                       help='Mostra informazioni sulla licenza')
    
    args = parser.parse_args()
    
    # Mostra licenza se richiesto
    if args.license:
        print("""
Universal TV Series Renamer v1.1
Copyright (C) 2024 Andres Zanzani

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

NOVITÀ v1.1:
- Supporto completo per sottotitoli in tutti i formati principali
- Riconoscimento automatico delle lingue nei sottotitoli
- Associazione intelligente sottotitoli-video per stagione/episodio
- Gestione sottotitoli orfani (senza video corrispondente)
- Script di rollback esteso per includere i sottotitoli

Per il testo completo della licenza GPL-3.0, visita:
https://www.gnu.org/licenses/gpl-3.0.html
        """)
        sys.exit(0)
    
    if not os.path.isdir(args.directory):
        print(f"❌ ERRORE: '{args.directory}' non è una directory valida!")
        sys.exit(1)
    
    renamer = TVSeriesRenamer()
    renamer.recursive = args.recursive
    renamer.language = args.language
    renamer.interface_language = args.interface
    
    print(renamer.get_text('header'))
    print(renamer.get_text('developer'))
    print(renamer.get_text('license'))
    print("=" * 50)
    print(f"{renamer.get_text('directory')} {os.path.abspath(args.directory)}")
    print(f"{renamer.get_text('format')} {args.format}")
    print(f"{renamer.get_text('episode_language')} {args.language}")
    print(f"{renamer.get_text('interface_language')} {args.interface}")
    print(f"{renamer.get_text('recursive')} {renamer.get_text('yes') if args.recursive else renamer.get_text('no')}")
    print(f"{renamer.get_text('mode')} {renamer.get_text('execution') if args.execute else renamer.get_text('preview')}")
    print("=" * 50)
    
    # Configura TMDB se fornita
    if args.tmdb_key:
        renamer.tmdb_api_key = args.tmdb_key
        print(renamer.get_text('tmdb_configured'))
    elif not renamer.tmdb_api_key:
        print(renamer.get_text('tmdb_register'))
    
    # Autentica con TheTVDB
    renamer.authenticate_tvdb()
    
    # Processa i file
    renamer.process_files(args.directory, args.format, dry_run=not args.execute)
    
    if not args.execute:
        if renamer.interface_language == 'en':
            print(f"\n💡 To actually execute the renames, add --execute")
            print(f"💡 This will rename both video files and their matching subtitles")
        else:
            print(f"\n💡 Per eseguire realmente le rinomine, aggiungi --execute")
            print(f"💡 Questo rinominerà sia i file video che i sottotitoli corrispondenti")

if __name__ == "__main__":
    main()
