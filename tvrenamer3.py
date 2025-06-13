#!/usr/bin/env python3
"""
Universal TV Series Renamer
Script universale per rinominare episodi di qualsiasi serie TV
Interroga TheTVDB, TMDB e IMDb per ottenere informazioni automaticamente

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
Version: 1.0
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
            'User-Agent': 'UniversalTVRenamer/1.0',
            'Accept': 'application/json'
        })
        self.language = 'it'  # Lingua di default
        
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
                    print("✅ Autenticazione TheTVDB v4 riuscita")
                    return True
            else:
                print(f"❌ Errore autenticazione TheTVDB: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Errore autenticazione TheTVDB: {e}")
        
        # Fallback: disabilita TheTVDB
        print("🔄 TheTVDB non disponibile, continuo con altre fonti")
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

    def search_series_tmdb(self, series_name):
        """Cerca la serie su TMDB"""
        if not self.tmdb_api_key:
            print("⚠️  TMDB API key non configurata - saltando TMDB")
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
                    print("   💡 Registra una API key gratuita su https://www.themoviedb.org/settings/api")
                
        except Exception as e:
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
            print(f"❌ Nessuna serie trovata per: '{series_name}'")
            print("\n💡 Suggerimenti:")
            print("   - Verifica l'ortografia del nome")
            print("   - Prova con il nome originale in inglese")
            print("   - Usa un nome più breve")
            return None
        
        print(f"\n🔍 Risultati di ricerca per: '{series_name}'")
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
        
        print("0. ❌ Nessuna delle opzioni sopra")
        print("r. 🔄 Ricerca con nome diverso")
        print("q. 🚪 Esci dal programma")
        
        while True:
            try:
                choice = input("Seleziona (1-{}, 0, r, q): ".format(len(results))).strip().lower()
                
                if choice == '0':
                    return None
                elif choice == 'r':
                    new_name = input("Inserisci nuovo nome per la ricerca: ").strip()
                    if new_name:
                        return self.search_and_select_series(new_name)
                    continue
                elif choice == 'q':
                    print("👋 Uscita richiesta dall'utente")
                    sys.exit(0)
                else:
                    choice_num = int(choice) - 1
                    if 0 <= choice_num < len(results):
                        return results[choice_num]
                    else:
                        print("❌ Selezione non valida!")
                        
            except (ValueError, KeyboardInterrupt):
                if choice == 'q':
                    sys.exit(0)
                print("❌ Selezione non valida!")
            except KeyboardInterrupt:
                print("\n👋 Uscita richiesta dall'utente")
                sys.exit(0)

    def select_language(self):
        """Seleziona la lingua per titoli episodi"""
        languages = {
            "1": ("it", "Italiano"),
            "2": ("en", "English"),
            "3": ("es", "Español"),
            "4": ("fr", "Français"),
            "5": ("de", "Deutsch")
        }
        
        print("\n🌍 Scegli la lingua per i titoli degli episodi:")
        for key, (code, name) in languages.items():
            print(f"{key}. {name} ({code})")
        
        while True:
            choice = input("Scegli lingua (1-5, o premi Enter per italiano): ").strip()
            if choice == "":
                self.language = "it"
                print("✅ Lingua selezionata: Italiano")
                return
            elif choice in languages:
                code, name = languages[choice]
                self.language = code
                print(f"✅ Lingua selezionata: {name}")
                return
            print("❌ Scelta non valida!")
    def search_and_select_series(self, series_name):
        """Cerca e seleziona una serie da tutte le fonti"""
        print(f"\n🔍 Ricerca in corso per: '{series_name}'")
        
        all_results = []
        
        # Cerca su TMDB prima (di solito ha dati migliori)
        if self.tmdb_api_key:
            print("🔄 Ricerca su TMDB...")
            tmdb_results = self.search_series_tmdb(series_name)
            all_results.extend(tmdb_results)
        
        # Poi TheTVDB
        if self.tvdb_token:
            print("🔄 Ricerca su TheTVDB...")
            tvdb_results = self.search_series_tvdb(series_name)
            all_results.extend(tvdb_results)
        
        # Infine IMDb come fallback
        if len(all_results) < 3:  # Solo se non abbiamo abbastanza risultati
            print("🔄 Ricerca su IMDb...")
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

    def find_video_files(self, directory):
        """Trova file video nella directory"""
        video_extensions = {'.mkv', '.avi', '.mp4', '.m4v', '.mov', '.wmv', '.flv', '.webm', '.ts', '.m2ts'}
        video_files = []
        
        path = Path(directory)
        for file_path in path.rglob('*') if getattr(self, 'recursive', False) else path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                video_files.append(file_path)
        
        return sorted(video_files)

    def process_files(self, directory, format_style="standard", dry_run=True):
        """Processa tutti i file nella directory"""
        video_files = self.find_video_files(directory)
        
        if not video_files:
            print("❌ Nessun file video trovato!")
            return
        
        print(f"\n📁 Trovati {len(video_files)} file video")
        
        # Raggruppa file per serie (basato sul nome estratto)
        series_groups = {}
        for file_path in video_files:
            series_name = self.extract_series_info(file_path.name)
            if series_name not in series_groups:
                series_groups[series_name] = []
            series_groups[series_name].append(file_path)
        
        print(f"📊 Rilevate {len(series_groups)} serie diverse")
        
        # Processa ogni serie
        for series_name, files in series_groups.items():
            print(f"\n{'='*80}")
            print(f"📺 SERIE: {series_name} ({len(files)} file)")
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
            self.process_series_files(files, selected_series, format_style, dry_run)

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
            print(f"\n⚠️  DUPLICATI RILEVATI: {len(duplicates)} episodi hanno più file")
            for season, episode, file_list in duplicates:
                print(f"\n🔄 S{season:02d}E{episode:02d} - {len(file_list)} file trovati:")
                for i, file_path in enumerate(file_list, 1):
                    size = file_path.stat().st_size / (1024**3)  # Size in GB
                    print(f"   {i}. {file_path.name} ({size:.1f} GB)")
                
                print("   0. ❌ Salta questo episodio")
                print("   a. ✅ Rinomina tutti i file (aggiungerà [Versione 2], [Versione 3], etc.)")
                
                while True:
                    try:
                        choice = input(f"Quale file tenere per S{season:02d}E{episode:02d}? (1-{len(file_list)}, 0, a): ").strip().lower()
                        
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
                                print("❌ Scelta non valida!")
                    except (ValueError, KeyboardInterrupt):
                        print("❌ Scelta non valida!")
        
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
                print(f"\n⚠️  EPISODI MANCANTI RILEVATI:")
                for season, missing in gaps_found:
                    missing_str = ', '.join([f"E{ep:02d}" for ep in missing])
                    print(f"   📺 Stagione {season}: Mancano {missing_str}")
                
                print("\n💡 Suggerimento: Verifica se hai tutti gli episodi della serie")
        
        return files
    def process_series_files(self, files, selected_series, format_style, dry_run):
        """Processa i file di una specifica serie"""
        series_id = selected_series.get('id')
        series_name = selected_series.get('name')
        source = selected_series.get('source')
        
        # Controllo duplicati e episodi mancanti
        files = self.check_duplicates_and_gaps(files, selected_series)
        
        if not files:
            print("❌ Nessun file da processare dopo i controlli")
            return
        
        renames = []
        duplicate_counter = {}
        
        for file_path in files:
            season, episode = self.extract_episode_info(file_path.name)
            
            if season is None or episode is None:
                print(f"⚠️  SKIP: {file_path.name} (formato non riconosciuto)")
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
                file_path.suffix, format_style
            )
            
            # Controlla se questo nome base è già stato usato
            key = (season, episode)
            if key in duplicate_counter:
                duplicate_counter[key] += 1
                # Aggiungi suffisso prima dell'estensione per versioni alternative
                name_part, ext = base_name.rsplit('.', 1) if '.' in base_name else (base_name, '')
                
                # Il secondo file è [Versione 2], il terzo [Versione 3], etc.
                version_number = duplicate_counter[key]
                new_name = f"{name_part} [Versione {version_number}].{ext}" if ext else f"{name_part} [Versione {version_number}]"
            else:
                duplicate_counter[key] = 1
                new_name = base_name
            
            renames.append((file_path, new_name))
        
        # Esegui rinomine senza l'elenco dettagliato
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
Script automatico per ripristinare i nomi file originali

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
    
    # Mostra anteprima delle prime 5 rinomine
    print("📋 Anteprima delle rinomine (prime 5):")
    print("-" * 80)
    for i, (new_path, old_name) in enumerate(files_found[:5]):
        print(f"{i+1:2d}. {new_path.name}")
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
            print(f"✅ {new_path.name} → {old_name}")
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
            
            print(f"✅ Script di rollback generato: {script_path}")
            print("💡 Per ripristinare i nomi originali, esegui:")
            if os.name == 'nt':  # Windows
                print(f"   python \"{script_path}\"")
            else:  # Linux/Mac
                print(f"   python3 \"{script_path}\"")
                print(f"   oppure: ./{script_path.name}")
            
        except Exception as e:
            print(f"❌ Errore nella generazione dello script di rollback: {e}")
    
    def execute_renames(self, renames, dry_run=True):
        """Esegue le rinomine con formato tabella adattivo"""
        if not renames:
            return
        
        if not dry_run:
            print(f"\n⚠️  ATTENZIONE: Rinominare {len(renames)} file?")
            if input("Confermi? [s/N]: ").strip().lower() not in ['s', 'si', 'sì']:
                print("❌ Annullato")
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
        print(f"📋 {'PREVIEW' if dry_run else 'RINOMINE'} - {len(renames)} file")
        print(f"{'='*terminal_width}")
        
        # Header tabella
        print(f"{'NOME ORIGINALE':<{old_width}} | {'NUOVO NOME':<{new_width}}")
        print(f"{'-'*old_width}-+-{'-'*new_width}")
        
        success = 0
        errors = 0
        
        for old_path, new_name in renames:
            new_path = old_path.parent / new_name
            
            # Tronca i nomi se necessario
            old_display = self.truncate_filename(old_path.name, old_width)
            new_display = self.truncate_filename(new_name, new_width)
            
            try:
                if dry_run:
                    print(f"{old_display:<{old_width}} | {new_display:<{new_width}}")
                    success += 1
                else:
                    if new_path.exists():
                        error_msg = self.truncate_filename("❌ File esiste già", new_width)
                        print(f"{old_display:<{old_width}} | {error_msg:<{new_width}}")
                        errors += 1
                        continue
                    
                    old_path.rename(new_path)
                    print(f"{old_display:<{old_width}} | {new_display:<{new_width}}")
                    success += 1
                    
            except Exception as e:
                error_msg = self.truncate_filename(f"❌ ERRORE: {str(e)}", new_width)
                print(f"{old_display:<{old_width}} | {error_msg:<{new_width}}")
                errors += 1
        
        print(f"{'-'*old_width}-+-{'-'*new_width}")
        print(f"📊 RISULTATI: ✅ {success} successi, ❌ {errors} errori")
        
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
        description="Universal TV Series Renamer v1.0 - by Andres Zanzani",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Universal TV Series Renamer
Copyright (C) 2024 Andres Zanzani
Licenza: GPL-3.0

Esempi di utilizzo:

  # Preview sicura
  python3 tv_renamer.py /path/to/series

  # Esecuzione reale
  python3 tv_renamer.py /path/to/series --execute

  # Ricerca ricorsiva in sottocartelle
  python3 tv_renamer.py /path/to/series --recursive --execute

  # Formato specifico con TMDB
  python3 tv_renamer.py /path/to/series --tmdb-key YOUR_KEY --format plex --execute

Questo software è distribuito sotto licenza GPL-3.0.
Per maggiori informazioni: https://www.gnu.org/licenses/gpl-3.0.html
        """
    )
    
    parser.add_argument('directory', help='Directory con i file video')
    parser.add_argument('--execute', action='store_true', help='Esegui le rinomine (default: solo preview)')
    parser.add_argument('--format', choices=['standard', 'plex', 'simple', 'minimal', 'kodi'], 
                       default='standard', help='Formato nome file')
    parser.add_argument('--recursive', action='store_true', help='Cerca ricorsivamente nelle sottocartelle')
    parser.add_argument('--language', choices=['it', 'en', 'es', 'fr', 'de'], 
                       default='it', help='Lingua per i titoli degli episodi')
    parser.add_argument('--tmdb-key', help='API key per TMDB (opzionale)')
    parser.add_argument('--version', action='version', 
                       version='Universal TV Series Renamer v1.0 - Copyright (C) 2024 Andres Zanzani - GPL-3.0')
    parser.add_argument('--license', action='store_true', 
                       help='Mostra informazioni sulla licenza')
    
    args = parser.parse_args()
    
    # Mostra licenza se richiesto
    if args.license:
        print("""
Universal TV Series Renamer v1.0
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

Per il testo completo della licenza GPL-3.0, visita:
https://www.gnu.org/licenses/gpl-3.0.html
        """)
        sys.exit(0)
    
    if not os.path.isdir(args.directory):
        print(f"❌ ERRORE: '{args.directory}' non è una directory valida!")
        sys.exit(1)
    
    print("📺 Universal TV Series Renamer v1.0")
    print("👨‍💻 Sviluppato da: Andres Zanzani")
    print("📄 Licenza: GPL-3.0")
    print("=" * 50)
    print(f"📁 Directory: {os.path.abspath(args.directory)}")
    print(f"🎨 Formato: {args.format}")
    print(f"🌍 Lingua: {args.language}")
    print(f"🔄 Ricorsivo: {'Sì' if args.recursive else 'No'}")
    print(f"⚙️  Modalità: {'ESECUZIONE' if args.execute else 'PREVIEW'}")
    print("=" * 50)
    
    renamer = TVSeriesRenamer()
    renamer.recursive = args.recursive
    renamer.language = args.language
    
    # Configura TMDB se fornita
    if args.tmdb_key:
        renamer.tmdb_api_key = args.tmdb_key
        print("✅ TMDB API key configurata")
    elif not renamer.tmdb_api_key:
        print("⚠️  TMDB non configurato - registra una chiave gratuita su https://www.themoviedb.org/settings/api")
    
    # Selezione lingua interattiva se non specificata
    if not args.execute:  # Solo in modalità preview
        renamer.select_language()
    
    # Autentica con TheTVDB
    renamer.authenticate_tvdb()
    
    # Processa i file
    renamer.process_files(args.directory, args.format, dry_run=not args.execute)
    
    if not args.execute:
        print(f"\n💡 Per eseguire realmente le rinomine, aggiungi --execute")

if __name__ == "__main__":
    main()
