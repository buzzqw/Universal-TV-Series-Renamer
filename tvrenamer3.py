#!/usr/bin/env python3
"""
Universal TV Series Renamer - Versione Rifattorizzata
Script per rinominare episodi di serie TV

Copyright (C) 2024 Andres Zanzani
Licenza: GPL-3.0
"""

import os
import re
import sys
import time
import html
import argparse
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

@dataclass
class Config:
    """Configurazione dell'applicazione"""
    tmdb_api_key: Optional[str] = None
    timeout: int = 10
    max_retries: int = 3
    language: str = 'it'
    interface_language: str = 'it'
    format_style: str = 'standard'
    recursive: bool = False
    dry_run: bool = True

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'Config':
        return cls(
            tmdb_api_key=args.tmdb_key or os.getenv('TMDB_API_KEY'),
            language=args.language,
            interface_language=args.interface,
            format_style=args.format,
            recursive=args.recursive,
            dry_run=not args.execute
        )

# ============================================================================
# STRUTTURE DATI
# ============================================================================

@dataclass
class SeriesInfo:
    id: str
    name: str
    year: str
    overview: str
    source: str
    vote_average: Optional[float] = None

@dataclass
class EpisodeInfo:
    title: str
    season: int
    episode: int
    overview: str = ""
    air_date: str = ""
    vote_average: Optional[float] = None

@dataclass
class RenameOperation:
    old_path: Path
    new_name: str
    season: int
    episode: int

# ============================================================================
# UTILITÀ
# ============================================================================

class FileHelper:
    """Helper per operazioni sui file"""
    
    VIDEO_EXTENSIONS = {'.mkv', '.avi', '.mp4', '.m4v', '.mov', '.wmv', '.flv', '.webm', '.ts', '.m2ts'}
    
    @staticmethod
    def find_video_files(directory: Path, recursive: bool = False) -> List[Path]:
        """Trova file video"""
        files = []
        pattern = directory.rglob('*') if recursive else directory.iterdir()
        
        for file_path in pattern:
            if (file_path.is_file() and 
                file_path.suffix.lower() in FileHelper.VIDEO_EXTENSIONS and
                not file_path.name.startswith('.')):
                files.append(file_path)
        
        return sorted(files)
    
    @staticmethod
    def clean_filename(name: str) -> str:
        """Pulisce nome file"""
        name = html.unescape(name)
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')
        name = name.replace('&', 'and')
        return re.sub(r'\s+', ' ', name).strip()

class PatternHelper:
    """Helper per pattern matching"""
    
    SEASON_EPISODE_PATTERNS = [
        r'[Ss](\d+)[Ee](\d+)',
        r'(\d+)x(\d+)',
        r'[Ss]eason\s*(\d+).*[Ee]pisode\s*(\d+)'
    ]
    
    @staticmethod
    def extract_season_episode(filename: str) -> Tuple[Optional[int], Optional[int]]:
        """Estrae stagione e episodio"""
        for pattern in PatternHelper.SEASON_EPISODE_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return int(match.group(1)), int(match.group(2))
        return None, None
    
    @staticmethod
    def find_first_season_episode_pos(text: str) -> int:
        """Trova la posizione del primo pattern stagione/episodio"""
        patterns = [r'[Ss]\d+[Ee]\d+', r'\d+x\d+', r'[Ss]eason\s*\d+']
        earliest = len(text)
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                earliest = min(earliest, match.start())
        
        return earliest

class SeriesNameExtractor:
    """Estrae nomi serie da file e directory"""
    
    SERIES_CORRECTIONS = {
        'Better Call Soul': 'Better Call Saul',
        'Breaking Bad': 'Breaking Bad',
        'Game of Thrones': 'Game of Thrones'
    }
    
    @staticmethod
    def extract_from_file(filename: str, directory_name: str = "") -> str:
        """Estrae nome serie da filename o directory"""
        stem = Path(filename).stem
        
        # Trova posizione pattern stagione/episodio
        season_pos = PatternHelper.find_first_season_episode_pos(stem)
        
        # Estrai nome serie dal filename
        if season_pos < len(stem):
            series_name = stem[:season_pos].strip()
            # Pulisci separatori finali
            series_name = re.sub(r'[\s\-\._]+$', '', series_name)
        else:
            series_name = ""
        
        # Se vuoto o troppo corto, usa directory
        if len(series_name) < 2 and directory_name:
            series_name = SeriesNameExtractor._clean_directory_name(directory_name)
        
        # Applica correzioni note
        for old, new in SeriesNameExtractor.SERIES_CORRECTIONS.items():
            if old.lower() in series_name.lower():
                return new
        
        return series_name or "Unknown Series"
    
    @staticmethod
    def _clean_directory_name(directory_name: str) -> str:
        """Pulisce nome directory"""
        # Rimuovi suffissi comuni
        cleaned = re.sub(r'\.(finito|completo|complete|finished)$', '', directory_name, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*-\s*(complete|completo|finito).*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*\(\d{4}\).*$', '', cleaned)  # Anno
        cleaned = re.sub(r'\s*\[.*?\].*$', '', cleaned)    # [tag]
        cleaned = re.sub(r'\s*S\d+.*$', '', cleaned, flags=re.IGNORECASE)  # Season info
        
        # Pulisci spazi e separatori
        cleaned = re.sub(r'[._]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

class FilenameGenerator:
    """Genera nomi file puliti"""
    
    @staticmethod
    def generate(series_name: str, season: int, episode: int, 
                episode_title: str, extension: str, format_style: str = 'standard') -> str:
        """Genera nome file nel formato richiesto"""
        series_clean = FileHelper.clean_filename(series_name)
        episode_clean = FileHelper.clean_filename(episode_title)
        
        formats = {
            "standard": f"{series_clean} - S{season:02d}E{episode:02d} - {episode_clean}{extension}",
            "plex": f"{series_clean} - S{season:02d}E{episode:02d} - {episode_clean}{extension}",
            "simple": f"{series_clean} {season}x{episode:02d} {episode_clean}{extension}",
            "minimal": f"{series_clean} S{season:02d}E{episode:02d}{extension}",
            "kodi": f"{series_clean} S{season:02d}E{episode:02d} {episode_clean}{extension}"
        }
        
        return formats.get(format_style, formats["standard"])

# ============================================================================
# HTTP E CACHE
# ============================================================================

class SimpleCache:
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str):
        if key not in self._cache:
            return None
        if time.time() - self._timestamps[key] > self.ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        return self._cache[key]
    
    def set(self, key: str, value):
        self._cache[key] = value
        self._timestamps[key] = time.time()

class HTTPClient:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            'User-Agent': 'UniversalTVRenamer/1.2',
            'Accept': 'application/json'
        })
        
        self._last_calls = {}
        self._min_interval = 0.2
    
    def get(self, url: str, **kwargs) -> requests.Response:
        domain = url.split('/')[2]
        
        if domain in self._last_calls:
            elapsed = time.time() - self._last_calls[domain]
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
        
        self._last_calls[domain] = time.time()
        
        kwargs.setdefault('timeout', self.config.timeout)
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response

# ============================================================================
# PROVIDER API
# ============================================================================

class BaseProvider:
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
        self.cache = SimpleCache()
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        raise NotImplementedError
    
    def get_episode_info(self, series_id: str, season: int, episode: int) -> Optional[EpisodeInfo]:
        raise NotImplementedError

class TMDBProvider(BaseProvider):
    def __init__(self, api_key: str, http_client: HTTPClient, language: str = 'it'):
        super().__init__(http_client)
        self.api_key = api_key
        self.language = language
        self.base_url = "https://api.themoviedb.org/3"
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        cache_key = f"tmdb_search_{query}_{self.language}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/search/tv"
            params = {
                'api_key': self.api_key,
                'query': query,
                'language': f'{self.language}-{self.language.upper()}'
            }
            
            response = self.http_client.get(url, params=params)
            data = response.json()
            
            results = []
            for item in data.get('results', [])[:5]:
                series = SeriesInfo(
                    id=str(item.get('id')),
                    name=item.get('name', 'Nome non disponibile'),
                    year=item.get('first_air_date', '')[:4] if item.get('first_air_date') else '',
                    overview=item.get('overview', ''),
                    source='TMDB',
                    vote_average=item.get('vote_average', 0)
                )
                results.append(series)
            
            self.cache.set(cache_key, results)
            return results
        except Exception:
            return []
    
    def get_episode_info(self, series_id: str, season: int, episode: int) -> Optional[EpisodeInfo]:
        cache_key = f"tmdb_episode_{series_id}_{season}_{episode}_{self.language}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/tv/{series_id}/season/{season}/episode/{episode}"
            params = {
                'api_key': self.api_key,
                'language': f'{self.language}-{self.language.upper()}'
            }
            
            response = self.http_client.get(url, params=params)
            data = response.json()
            
            episode_info = EpisodeInfo(
                title=data.get('name', f'Episode {episode}'),
                season=season,
                episode=episode,
                overview=data.get('overview', ''),
                air_date=data.get('air_date', ''),
                vote_average=data.get('vote_average', 0)
            )
            
            self.cache.set(cache_key, episode_info)
            return episode_info
        except Exception:
            return None

class TVMazeProvider(BaseProvider):
    def __init__(self, http_client: HTTPClient):
        super().__init__(http_client)
        self.base_url = "https://api.tvmaze.com"
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        cache_key = f"tvmaze_search_{query}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/search/shows"
            params = {'q': query}
            
            response = self.http_client.get(url, params=params)
            data = response.json()
            
            results = []
            for item in data[:5]:
                show = item.get('show', {})
                
                summary = re.sub(r'<[^>]+>', '', show.get('summary', '') or '').strip()
                year = show.get('premiered', '')[:4] if show.get('premiered') else ''
                
                rating = None
                if show.get('rating') and show.get('rating').get('average'):
                    rating = show.get('rating').get('average')
                
                series = SeriesInfo(
                    id=str(show.get('id')),
                    name=show.get('name', 'Nome non disponibile'),
                    year=year,
                    overview=summary,
                    source='TVMaze',
                    vote_average=rating
                )
                results.append(series)
            
            self.cache.set(cache_key, results)
            return results
        except Exception:
            return []
    
    def get_episode_info(self, series_id: str, season: int, episode: int) -> Optional[EpisodeInfo]:
        cache_key = f"tvmaze_episode_{series_id}_{season}_{episode}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/shows/{series_id}/episodebynumber"
            params = {'season': season, 'number': episode}
            
            response = self.http_client.get(url, params=params)
            data = response.json()
            
            summary = re.sub(r'<[^>]+>', '', data.get('summary', '') or '').strip()
            
            rating = None
            if data.get('rating') and data.get('rating').get('average'):
                rating = data.get('rating').get('average')
            
            episode_info = EpisodeInfo(
                title=data.get('name', f'Episode {episode}'),
                season=season,
                episode=episode,
                overview=summary,
                air_date=data.get('airdate', ''),
                vote_average=rating
            )
            
            self.cache.set(cache_key, episode_info)
            return episode_info
        except Exception:
            return None

class ProviderManager:
    def __init__(self, config: Config, http_client: HTTPClient):
        self.providers = []
        
        # Inizializza provider disponibili
        if config.tmdb_api_key:
            try:
                self.providers.append(TMDBProvider(config.tmdb_api_key, http_client, config.language))
                print("✅ TMDB configurato")
            except Exception:
                pass
        
        try:
            self.providers.append(TVMazeProvider(http_client))
            print("✅ TVMaze configurato")
        except Exception:
            pass
        
        if not self.providers:
            print("❌ ERRORE: Nessun provider disponibile!")
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        all_results = []
        
        for provider in self.providers:
            try:
                results = provider.search_series(query)
                if results:
                    all_results.extend(results)
            except Exception:
                continue
        
        # Deduplica
        seen = set()
        unique = []
        for result in all_results:
            key = (result.name.lower().replace(' ', ''), result.source, result.year)
            if key not in seen:
                seen.add(key)
                unique.append(result)
        
        return unique[:10]
    
    def get_episode_info(self, series_info: SeriesInfo, season: int, episode: int) -> Optional[EpisodeInfo]:
        for provider in self.providers:
            if provider.__class__.__name__.replace('Provider', '') == series_info.source:
                try:
                    return provider.get_episode_info(series_info.id, season, episode)
                except Exception:
                    continue
        return None

# ============================================================================
# TESTI INTERFACCIA
# ============================================================================

class TextManager:
    TEXTS = {
        'it': {
            'header': "📺 Universal TV Series Renamer v1.2 (Clean)",
            'developer': "👨‍💻 Sviluppato da: Andres Zanzani",
            'license': "📄 Licenza: GPL-3.0",
            'directory': "📁 Directory:",
            'format': "🎨 Formato:",
            'language': "🌍 Lingua:",
            'recursive': "🔄 Ricorsivo:",
            'mode': "⚙️  Modalità:",
            'preview': "PREVIEW",
            'execution': "ESECUZIONE",
            'yes': "Sì",
            'no': "No",
            'searching_for': "🔍 Ricerca in corso per:",
            'files_found': "📁 Trovati {} file video",
            'no_files': "❌ Nessun file video trovato!",
            'no_series_found': "❌ Nessuna serie trovata per: '{}'",
            'results': "📊 RISULTATI: ✅ {} successi, ❌ {} errori",
            'series_title': "📺 SERIE:",
            'search_results': "🔍 Risultati di ricerca per:",
            'none_above': "❌ Nessuna delle opzioni sopra",
            'exit': "🚪 Esci dal programma",
            'select_prompt': "Seleziona (1-{}, 0, q):",
            'skipping_series': "⏭️  Saltando serie:",
            'skip_unrecognized': "⚠️  SKIP: {} (formato non riconosciuto)",
            'restore_script_created': "📄 Script di ripristino creato: {}",
            'restore_instructions': "💡 Per ripristinare i nomi originali, esegui: python {}"
        },
        'en': {
            'header': "📺 Universal TV Series Renamer v1.2 (Clean)",
            'developer': "👨‍💻 Developed by: Andres Zanzani", 
            'license': "📄 License: GPL-3.0",
            'directory': "📁 Directory:",
            'format': "🎨 Format:",
            'language': "🌍 Language:",
            'recursive': "🔄 Recursive:",
            'mode': "⚙️  Mode:",
            'preview': "PREVIEW",
            'execution': "EXECUTION",
            'yes': "Yes",
            'no': "No",
            'searching_for': "🔍 Searching for:",
            'files_found': "📁 Found {} video files",
            'no_files': "❌ No video files found!",
            'no_series_found': "❌ No series found for: '{}'",
            'results': "📊 RESULTS: ✅ {} successes, ❌ {} errors",
            'series_title': "📺 SERIES:",
            'search_results': "🔍 Results for:",
            'none_above': "❌ None of the above options",
            'exit': "🚪 Exit",
            'select_prompt': "Select (1-{}, 0, q):",
            'skipping_series': "⏭️  Skipping series:",
            'skip_unrecognized': "⚠️  SKIP: {} (unrecognized format)",
            'restore_script_created': "📄 Restore script created: {}",
            'restore_instructions': "💡 To restore original names, run: python {}"
        }
    }
    
    def __init__(self, language: str = 'it'):
        self.language = language
    
    def get(self, key: str, *args) -> str:
        text = self.TEXTS.get(self.language, self.TEXTS['it']).get(key, key)
        if args:
            try:
                return text.format(*args)
            except (IndexError, KeyError, ValueError):
                return text
        return text

# ============================================================================
# SCRIPT DI RIPRISTINO
# ============================================================================

class RestoreScriptGenerator:
    def __init__(self, directory: Path, text_manager: TextManager):
        self.directory = directory
        self.text_manager = text_manager
        self.renames = []
    
    def add_rename(self, old_name: str, new_name: str):
        self.renames.append((old_name, new_name))
    
    def create_script(self) -> Optional[str]:
        if not self.renames:
            return None
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        script_name = f"restore_tv_names_{timestamp}.py"
        script_path = self.directory / script_name
        
        try:
            script_content = self._generate_content()
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            try:
                os.chmod(script_path, 0o755)
            except:
                pass
            
            return script_name
        except Exception as e:
            print(f"❌ Errore creazione script: {e}")
            return None
    
    def _generate_content(self) -> str:
        lang = self.text_manager.language
        
        if lang == 'en':
            texts = {
                'header': 'TV Renamer - Restore Script',
                'warning': 'WARNING: This script will restore original filenames!',
                'confirm': 'Do you want to proceed? (y/N): ',
                'cancelled': 'Operation cancelled.',
                'processing': 'Processing restores...',
                'completed': 'Restore completed!',
                'press_enter': 'Press ENTER to exit...'
            }
        else:
            texts = {
                'header': 'TV Renamer - Script di Ripristino',
                'warning': 'ATTENZIONE: Questo script ripristinerà i nomi file originali!',
                'confirm': 'Vuoi procedere? (s/N): ',
                'cancelled': 'Operazione annullata.',
                'processing': 'Elaborazione ripristini...',
                'completed': 'Ripristino completato!',
                'press_enter': 'Premi INVIO per uscire...'
            }
        
        renames_code = '\n'.join([f"        ({repr(new)}, {repr(old)})," for old, new in self.renames])
        
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{texts['header']}
Creato: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

import os
from pathlib import Path

def main():
    print("📺 {texts['header']}")
    print("=" * 50)
    print("{texts['warning']}")
    print()
    
    script_dir = Path(__file__).parent.absolute()
    
    renames = [
{renames_code}
    ]
    
    print(f"📋 Trovati {{len(renames)}} file da ripristinare")
    
    try:
        confirm = input("{texts['confirm']}").strip().lower()
        if confirm not in ['s', 'y', 'si', 'yes']:
            print("{texts['cancelled']}")
            return
    except KeyboardInterrupt:
        print("\\n{texts['cancelled']}")
        return
    
    print("\\n{texts['processing']}")
    
    success = 0
    for current_name, original_name in renames:
        try:
            current_path = script_dir / current_name
            original_path = script_dir / original_name
            
            if current_path.exists() and not original_path.exists():
                current_path.rename(original_path)
                print(f"✅ {{original_name}}")
                success += 1
            else:
                print(f"❌ {{original_name}} (skip)")
        except Exception as e:
            print(f"❌ {{original_name}} ({{e}})")
    
    print(f"\\n📊 Ripristinati {{success}} file")
    if success > 0:
        print("\\n✅ {texts['completed']}")
        try:
            Path(__file__).unlink()
        except:
            pass
    
    input("\\n{texts['press_enter']}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Errore: {{e}}")
        input("{texts['press_enter']}")
'''

# ============================================================================
# INTERFACCIA UTENTE
# ============================================================================

class UserInterface:
    def __init__(self, text_manager: TextManager):
        self.text_manager = text_manager
    
    def show_header(self, config: Config, directory: Path):
        print(self.text_manager.get('header'))
        print(self.text_manager.get('developer'))
        print(self.text_manager.get('license'))
        print("=" * 50)
        print(f"{self.text_manager.get('directory')} {directory.absolute()}")
        print(f"{self.text_manager.get('format')} {config.format_style}")
        print(f"{self.text_manager.get('language')} {config.language}")
        print(f"{self.text_manager.get('recursive')} {self.text_manager.get('yes') if config.recursive else self.text_manager.get('no')}")
        print(f"{self.text_manager.get('mode')} {self.text_manager.get('execution') if not config.dry_run else self.text_manager.get('preview')}")
        print("=" * 50)
    
    def select_series(self, results: List[SeriesInfo], series_name: str) -> Optional[SeriesInfo]:
        if not results:
            print(self.text_manager.get('no_series_found', series_name))
            return None
        
        print(f"\\n{self.text_manager.get('search_results')} '{series_name}':")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            name = html.unescape(result.name)
            line = f"{i:2d}. {result.source} | {name}"
            
            if result.year:
                line += f" | {result.year}"
            if result.vote_average:
                line += f" | ⭐ {result.vote_average:.1f}/10"
            
            print(line)
            
            if result.overview:
                overview = result.overview[:100] + "..." if len(result.overview) > 100 else result.overview
                print(f"    └─ {overview}")
        
        print(f"0. {self.text_manager.get('none_above')}")
        print(f"q. {self.text_manager.get('exit')}")
        
        while True:
            try:
                choice = input(f"{self.text_manager.get('select_prompt', len(results))} ").strip().lower()
                
                if choice == 'q':
                    sys.exit(0)
                elif choice == '0':
                    return None
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

# ============================================================================
# RENAMER PRINCIPALE
# ============================================================================

class TVSeriesRenamer:
    def __init__(self, config: Config):
        self.config = config
        self.text_manager = TextManager(config.interface_language)
        self.ui = UserInterface(self.text_manager)
        self.http_client = HTTPClient(config)
        self.provider_manager = ProviderManager(config, self.http_client)
    
    def process_directory(self, directory: Path):
        """Processa directory principale"""
        self.ui.show_header(self.config, directory)
        
        # Trova file video
        video_files = FileHelper.find_video_files(directory, self.config.recursive)
        
        if not video_files:
            print(self.text_manager.get('no_files'))
            return
        
        print(f"\\n{self.text_manager.get('files_found', len(video_files))}")
        
        # Ottieni nome directory corretto
        if str(directory) in ['.', './']:
            directory_name = Path.cwd().name
        else:
            directory_name = directory.name
        
        print(f"📁 Directory per estrazione serie: '{directory_name}'")
        
        # Raggruppa file per serie
        series_groups = self._group_files_by_series(video_files, directory_name)
        
        # Processa ogni serie
        for series_name, files in series_groups.items():
            print(f"\n{'='*80}")
            print(f"{self.text_manager.get('series_title')} {series_name} ({len(files)} file)")
            print(f"{'='*80}")
            
            self._process_series(series_name, files, directory)
    
    def _group_files_by_series(self, files: List[Path], directory_name: str) -> Dict[str, List[Path]]:
        """Raggruppa file per serie"""
        series_groups = {}
        
        for video_file in files:
            series_name = SeriesNameExtractor.extract_from_file(video_file.name, directory_name)
            if series_name not in series_groups:
                series_groups[series_name] = []
            series_groups[series_name].append(video_file)
        
        return series_groups
    
    def _process_series(self, series_name: str, files: List[Path], directory: Path):
        """Processa una serie specifica"""
        print(f"{self.text_manager.get('searching_for')} '{series_name}'")
        
        # Cerca serie online
        results = self.provider_manager.search_series(series_name)
        selected_series = self.ui.select_series(results, series_name)
        
        if not selected_series:
            print(f"{self.text_manager.get('skipping_series')} {series_name}")
            return
        
        # Prepara operazioni di rinomina
        operations = self._prepare_rename_operations(selected_series, files)
        
        if not operations:
            print("⚠️  Nessuna rinomina da eseguire per questa serie.")
            return
        
        # Esegui rinomine
        self._execute_renames(operations, directory)
    
    def _prepare_rename_operations(self, series: SeriesInfo, files: List[Path]) -> List[RenameOperation]:
        """Prepara operazioni di rinomina"""
        operations = []
        episode_files = {}
        
        # Raggruppa file per episodio
        for video_file in files:
            season, episode = PatternHelper.extract_season_episode(video_file.name)
            
            if season is None or episode is None:
                print(self.text_manager.get('skip_unrecognized', video_file.name))
                continue
            
            ep_key = (season, episode)
            if ep_key not in episode_files:
                episode_files[ep_key] = []
            episode_files[ep_key].append(video_file)
        
        # Crea operazioni per ogni episodio
        for (season, episode), file_list in episode_files.items():
            episode_info = self.provider_manager.get_episode_info(series, season, episode)
            episode_title = episode_info.title if episode_info else f"Episode {episode}"
            
            for i, video_file in enumerate(file_list):
                new_name = FilenameGenerator.generate(
                    series.name, season, episode, episode_title, 
                    video_file.suffix, self.config.format_style
                )
                
                # Se ci sono duplicati, aggiungi versione
                if len(file_list) > 1:
                    version_text = f"[Versione {i+1}]" if self.text_manager.language == 'it' else f"[Version {i+1}]"
                    name_part, ext = os.path.splitext(new_name)
                    new_name = f"{name_part} {version_text}{ext}"
                
                # Skip se il file è già nel formato corretto
                if video_file.name == new_name:
                    if self.config.dry_run:
                        print(f"⏭️  SKIP: {video_file.name} (già corretto)")
                    continue
                
                operations.append(RenameOperation(
                    old_path=video_file,
                    new_name=new_name,
                    season=season,
                    episode=episode
                ))
        
        return operations
    
    def _execute_renames(self, operations: List[RenameOperation], directory: Path):
        """Esegue le operazioni di rinomina"""
        restore_manager = RestoreScriptGenerator(directory, self.text_manager)
        
        mode = self.text_manager.get('execution') if not self.config.dry_run else self.text_manager.get('preview')
        print(f"\\n📋 {mode} - {len(operations)} operazioni")
        print("=" * 120)
        
        if self.text_manager.language == 'en':
            print(f"{'STATUS':<8} {'ORIGINAL FILE':<50} {'NEW FILE':<50}")
        else:
            print(f"{'STATO':<8} {'FILE ORIGINALE':<50} {'NUOVO FILE':<50}")
        print("-" * 120)
        
        success_count = 0
        error_count = 0
        
        for operation in operations:
            new_path = operation.old_path.parent / operation.new_name
            
            # Tronca nomi per visualizzazione
            old_display = operation.old_path.name
            if len(old_display) > 47:
                old_display = old_display[:44] + "..."
            
            new_display = operation.new_name
            if len(new_display) > 47:
                new_display = new_display[:44] + "..."
            
            if self.config.dry_run:
                print(f"{'📹 OK':<8} {old_display:<50} {new_display:<50}")
                success_count += 1
            else:
                try:
                    if new_path.exists():
                        status = "❌ EXISTS" if self.text_manager.language == 'en' else "❌ ESISTE"
                        print(f"{status:<8} {old_display:<50} {new_display:<50}")
                        error_count += 1
                        continue
                    
                    restore_manager.add_rename(operation.old_path.name, operation.new_name)
                    operation.old_path.rename(new_path)
                    print(f"{'✅ DONE':<8} {old_display:<50} {new_display:<50}")
                    success_count += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    if len(error_msg) > 20:
                        error_msg = error_msg[:17] + "..."
                    print(f"{'❌ ERROR':<8} {old_display:<50} {error_msg:<50}")
                    error_count += 1
        
        print("=" * 120)
        print(self.text_manager.get('results', success_count, error_count))
        
        # Crea script di ripristino
        if not self.config.dry_run and restore_manager.renames:
            try:
                script_name = restore_manager.create_script()
                if script_name:
                    print(f"\\n{self.text_manager.get('restore_script_created', script_name)}")
                    print(f"{self.text_manager.get('restore_instructions', script_name)}")
            except Exception as e:
                print(f"\\n❌ Errore nella creazione dello script di ripristino: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(
        description="Universal TV Series Renamer v1.2 (Clean) - by Andres Zanzani"
    )
    
    parser.add_argument('directory', help='Directory contenente i file video')
    parser.add_argument('--execute', action='store_true', help='Esegui rinomine (default: solo preview)')
    parser.add_argument('--format', choices=['standard', 'plex', 'simple', 'minimal', 'kodi'],
                       default='standard', help='Formato nome file')
    parser.add_argument('--recursive', action='store_true', help='Cerca ricorsivamente')
    parser.add_argument('--language', choices=['it', 'en', 'es', 'fr', 'de'], 
                       default='it', help='Lingua episodi')
    parser.add_argument('--interface', choices=['it', 'en'], 
                       default='it', help='Lingua interfaccia')
    parser.add_argument('--tmdb-key', help='API key TMDB')
    parser.add_argument('--version', action='version', version='Universal TV Series Renamer v1.2 (Clean)')
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"❌ ERRORE: '{args.directory}' non è una directory valida!")
        sys.exit(1)
    
    try:
        config = Config.from_args(args)
        renamer = TVSeriesRenamer(config)
        renamer.process_directory(directory)
        
    except KeyboardInterrupt:
        print("\\n👋 Operazione interrotta dall'utente")
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERRORE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
