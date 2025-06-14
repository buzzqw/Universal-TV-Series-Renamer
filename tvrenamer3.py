#!/usr/bin/env python3
"""
Universal TV Series Renamer - Versione Pulita
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
from urllib.parse import quote

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
    tvdb_api_key: str = "fb51f9b848ffac9750bada89ecba0225"
    timeout: int = 10
    max_retries: int = 3
    language: str = 'it'
    interface_language: str = 'it'
    format_style: str = 'standard'
    recursive: bool = False
    dry_run: bool = True

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'Config':
        """Crea configurazione da argomenti CLI"""
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
    """Informazioni di una serie"""
    id: str
    name: str
    year: str
    overview: str
    source: str
    vote_average: Optional[float] = None
    original_name: Optional[str] = None

@dataclass
class EpisodeInfo:
    """Informazioni di un episodio"""
    title: str
    season: int
    episode: int
    overview: str = ""
    air_date: str = ""
    vote_average: Optional[float] = None

# ============================================================================
# HTTP CLIENT SEMPLICE
# ============================================================================

class SafeHTTPClient:
    """Client HTTP con retry"""
    
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
        
        self._last_call_times = {}
        self._min_interval = 0.2

    def get(self, url: str, **kwargs) -> requests.Response:
        """GET con rate limiting"""
        import urllib.parse
        domain = urllib.parse.urlparse(url).netloc
        
        if domain in self._last_call_times:
            elapsed = time.time() - self._last_call_times[domain]
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
        
        self._last_call_times[domain] = time.time()
        
        kwargs.setdefault('timeout', self.config.timeout)
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response

# ============================================================================
# CACHE SEMPLICE
# ============================================================================

class SimpleCache:
    """Cache in memoria con TTL"""
    
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

# ============================================================================
# TESTI INTERFACCIA
# ============================================================================

class TextManager:
    """Gestione testi multilingue"""
    
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
            'suggestions': "💡 Suggerimenti:",
            'check_spelling': "   - Verifica l'ortografia del nome",
            'try_english': "   - Prova con il nome originale in inglese", 
            'use_shorter': "   - Usa un nome più breve",
            'providers_active': "🔗 Provider attivi:",
            'no_providers': "⚠️  Nessun provider configurato",
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
            'suggestions': "💡 Suggestions:",
            'check_spelling': "   - Check the spelling of the name",
            'try_english': "   - Try with the original English name", 
            'use_shorter': "   - Use a shorter name",
            'providers_active': "🔗 Active providers:",
            'no_providers': "⚠️  No providers configured",
            'restore_script_created': "📄 Restore script created: {}",
            'restore_instructions': "💡 To restore original names, run: python {}"
        }
    }
    
    def __init__(self, language: str = 'it'):
        self.language = language
    
    def get(self, key: str, *args) -> str:
        """Ottiene il testo tradotto per la lingua corrente"""
        text = self.TEXTS.get(self.language, self.TEXTS['it']).get(key, key)
        if args:
            try:
                return text.format(*args)
            except (IndexError, KeyError, ValueError):
                return text
        return text

# ============================================================================
# PROVIDER API
# ============================================================================

class TMDBClient:
    """Client TMDB"""
    
    def __init__(self, api_key: str, http_client: SafeHTTPClient, language: str = 'it'):
        self.api_key = api_key
        self.http_client = http_client
        self.language = language
        self.cache = SimpleCache(ttl=3600)
        self.base_url = "https://api.themoviedb.org/3"
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        """Cerca serie TV"""
        cache_key = f"search_{query}_{self.language}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/search/tv"
        params = {
            'api_key': self.api_key,
            'query': query,
            'language': f'{self.language}-{self.language.upper()}'
        }
        
        try:
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
        """Ottiene informazioni episodio"""
        cache_key = f"episode_{series_id}_{season}_{episode}_{self.language}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/tv/{series_id}/season/{season}/episode/{episode}"
        params = {
            'api_key': self.api_key,
            'language': f'{self.language}-{self.language.upper()}'
        }
        
        try:
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
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 and self.language != 'en':
                # Prova in inglese
                temp_lang = self.language
                self.language = 'en'
                result = self.get_episode_info(series_id, season, episode)
                self.language = temp_lang
                return result
            return None
        except Exception:
            return None

class TVMazeClient:
    """TV Maze API - Completamente gratuito"""
    
    def __init__(self, http_client: SafeHTTPClient):
        self.http_client = http_client
        self.base_url = "https://api.tvmaze.com"
        self.cache = SimpleCache(ttl=3600)
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        """Cerca serie su TV Maze"""
        cache_key = f"tvmaze_search_{query}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/search/shows"
        params = {'q': query}
        
        try:
            response = self.http_client.get(url, params=params)
            data = response.json()
            
            results = []
            for item in data[:5]:  # Prime 5 corrispondenze
                show = item.get('show', {})
                
                # Pulisci summary da tag HTML
                summary = show.get('summary', '') or ''
                summary = re.sub(r'<[^>]+>', '', summary).strip()
                
                # Estrai anno
                premiered = show.get('premiered', '')
                year = premiered[:4] if premiered else ''
                
                # Rating
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
        """Ottiene informazioni episodio da TV Maze"""
        cache_key = f"tvmaze_episode_{series_id}_{season}_{episode}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/shows/{series_id}/episodebynumber"
        params = {'season': season, 'number': episode}
        
        try:
            response = self.http_client.get(url, params=params)
            data = response.json()
            
            # Pulisci summary
            summary = data.get('summary', '') or ''
            summary = re.sub(r'<[^>]+>', '', summary).strip()
            
            # Rating episodio
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

class IMDbClient:
    """Client IMDb semplificato"""
    
    def __init__(self, http_client: SafeHTTPClient):
        self.http_client = http_client
        self.cache = SimpleCache(ttl=3600)
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        """Ricerca serie su IMDb"""
        cache_key = f"imdb_search_{query}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            search_url = "https://www.imdb.com/find"
            params = {'q': query, 's': 'tt', 'ttype': 'tv'}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.http_client.session.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                results = []
                
                # Pattern per IMDb
                patterns = [
                    r'<a[^>]*href="/title/(tt\d+)[^>]*>([^<]+)</a>[^<]*(?:<span[^>]*class="[^"]*result_year[^"]*"[^>]*>\((\d{4})[^)]*\))?',
                    r'<a[^>]*href="/title/(tt\d+)[^>]*>([^<]+)</a>'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        break
                
                for match in matches[:3]:  # Prime 3
                    if len(match) == 3:  # Con anno
                        imdb_id, title, year = match
                    elif len(match) == 2:  # Senza anno
                        imdb_id, title = match
                        year = ''
                    else:
                        continue
                    
                    title = html.unescape(title.strip())
                    
                    # Info aggiuntive
                    additional_info = self._get_additional_info(imdb_id)
                    
                    series = SeriesInfo(
                        id=imdb_id,
                        name=title,
                        year=year or additional_info.get('year', ''),
                        overview=additional_info.get('plot', ''),
                        source='IMDb',
                        vote_average=additional_info.get('rating')
                    )
                    results.append(series)
                
                self.cache.set(cache_key, results)
                return results
            
        except Exception:
            pass
        
        return []
    
    def _get_additional_info(self, imdb_id: str) -> dict:
        """Ottiene info aggiuntive"""
        try:
            url = f"https://www.imdb.com/title/{imdb_id}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.http_client.session.get(url, headers=headers, timeout=8)
            if response.status_code == 200:
                content = response.text
                info = {}
                
                # Anno
                year_match = re.search(r'<span[^>]*class="[^"]*sc-[^"]*"[^>]*>(\d{4})', content)
                if year_match:
                    info['year'] = year_match.group(1)
                
                # Rating
                rating_match = re.search(r'<span[^>]*class="[^"]*sc-[^"]*"[^>]*>(\d+\.?\d*)</span>', content)
                if rating_match:
                    try:
                        info['rating'] = float(rating_match.group(1))
                    except ValueError:
                        pass
                
                # Plot
                plot_match = re.search(r'<span[^>]*data-testid="plot-xl"[^>]*>([^<]+)</span>', content)
                if plot_match:
                    plot = html.unescape(plot_match.group(1).strip())
                    info['plot'] = plot[:150] + "..." if len(plot) > 150 else plot
                
                return info
        except Exception:
            pass
        
        return {}

class MultiProviderSearcher:
    """Cerca su più provider"""
    
    def __init__(self, config: Config, http_client: SafeHTTPClient):
        self.config = config
        self.providers = []
        
        # TMDB (se configurato)
        if config.tmdb_api_key:
            try:
                tmdb_client = TMDBClient(config.tmdb_api_key, http_client, config.language)
                self.providers.append(tmdb_client)
                print("✅ TMDB configurato")
            except Exception:
                pass
        
        # TV Maze (sempre disponibile)
        try:
            tvmaze_client = TVMazeClient(http_client)
            self.providers.append(tvmaze_client)
            print("✅ TVMaze configurato")
        except Exception:
            pass
        
        # IMDb (fallback)
        try:
            imdb_client = IMDbClient(http_client)
            self.providers.append(imdb_client)
            print("✅ IMDb configurato")
        except Exception:
            pass
        
        if not self.providers:
            print("❌ ERRORE: Nessun provider disponibile!")
        else:
            provider_names = [p.__class__.__name__.replace('Client', '') for p in self.providers]
            print(f"🔗 Provider attivi: {', '.join(provider_names)}")
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        """Cerca serie su tutti i provider"""
        all_results = []
        
        for provider in self.providers:
            try:
                provider_name = provider.__class__.__name__.replace('Client', '')
                print(f"🔄 Ricerca su {provider_name}...")
                
                results = provider.search_series(query)
                if results:
                    all_results.extend(results)
                    print(f"✅ {len(results)} risultati da {provider_name}")
                
            except Exception:
                pass
        
        # Deduplica migliorata
        seen_entries = set()
        unique_results = []
        
        for result in all_results:
            name_key = result.name.lower().replace(' ', '').replace("'", "").replace('-', '').replace('.', '')
            entry_key = (name_key, result.source, result.year)
            
            if entry_key not in seen_entries:
                seen_entries.add(entry_key)
                unique_results.append(result)
        
        return unique_results[:10]
    
    def get_episode_info(self, series_info: SeriesInfo, season: int, episode: int) -> Optional[EpisodeInfo]:
        """Ottiene info episodio dal provider appropriato"""
        # Prima prova il provider che ha trovato la serie
        for provider in self.providers:
            provider_name = provider.__class__.__name__.replace('Client', '')
            
            if provider_name == series_info.source and hasattr(provider, 'get_episode_info'):
                try:
                    episode_info = provider.get_episode_info(series_info.id, season, episode)
                    if episode_info:
                        return episode_info
                except Exception:
                    pass
        
        # Fallback: prova tutti i provider
        for provider in self.providers:
            if hasattr(provider, 'get_episode_info'):
                try:
                    episode_info = provider.get_episode_info(series_info.id, season, episode)
                    if episode_info:
                        return episode_info
                except Exception:
                    continue
        
        return None

# ============================================================================
# UTILITÀ FILE
# ============================================================================

class FileUtils:
    """Utilità per gestione file"""
    
    VIDEO_EXTENSIONS = {'.mkv', '.avi', '.mp4', '.m4v', '.mov', '.wmv', '.flv', '.webm', '.ts', '.m2ts'}
    
    @staticmethod
    def extract_series_info(filename: str) -> str:
        """Estrae nome serie dal filename"""
        name = Path(filename).stem
        
        # Pattern più aggressivi per rimuovere tutto dopo stagione/episodio
        patterns_to_remove = [
            r'[Ss]\d+[Ee]\d+.*',  # S01E01...
            r'\d+x\d+.*',         # 1x01...
            r'[Ss]eason\s*\d+.*', # Season 1...
            r'(720p|1080p|480p|2160p|4K).*',
            r'(HDTV|WEB-?DL|BluRay|BDRip|DVDRip).*',
            r'\[.*?\].*',         # [qualsiasi cosa]
            r'\(.*?\).*',         # (qualsiasi cosa)
            r'\..*$',             # Tutto dopo il primo punto
        ]
        
        series_name = name
        for pattern in patterns_to_remove:
            series_name = re.sub(pattern, '', series_name, flags=re.IGNORECASE)
        
        # Pulisci separatori
        series_name = re.sub(r'[._\-]+', ' ', series_name)
        series_name = re.sub(r'\s+', ' ', series_name).strip()
        
        # Rimuovi caratteri finali indesiderati
        series_name = series_name.rstrip(' -._[](){}')
        
        return series_name
    
    @staticmethod
    def extract_episode_info(filename: str) -> Tuple[Optional[int], Optional[int]]:
        """Estrae stagione e episodio"""
        patterns = [
            r'[Ss](\d+)[Ee](\d+)',
            r'(\d+)x(\d+)',
            r'[Ss]eason\s*(\d+).*[Ee]pisode\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return int(match.group(1)), int(match.group(2))
        
        return None, None
    
    @staticmethod
    def find_video_files(directory: Path, recursive: bool = False) -> List[Path]:
        """Trova file video"""
        files = []
        pattern = directory.rglob('*') if recursive else directory.iterdir()
        
        for file_path in pattern:
            if file_path.is_file() and file_path.suffix.lower() in FileUtils.VIDEO_EXTENSIONS:
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

# ============================================================================
# SISTEMA DI RIPRISTINO
# ============================================================================

class RestoreManager:
    """Gestisce il ripristino delle rinomine"""
    
    def __init__(self, directory: Path, text_manager: TextManager):
        self.directory = directory
        self.text_manager = text_manager
        self.renames = []  # Lista di tuple (old_name, new_name)
    
    def add_rename(self, old_name: str, new_name: str):
        """Aggiunge una rinomina alla lista"""
        self.renames.append((old_name, new_name))
    
    def create_restore_script(self) -> Optional[str]:
        """Crea lo script di ripristino Python"""
        if not self.renames:
            return None
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        script_name = f"restore_tv_names_{timestamp}.py"
        script_path = self.directory / script_name
        
        # Genera il contenuto dello script
        script_content = self._generate_script_content()
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Rendi eseguibile su Linux/Mac
            try:
                os.chmod(script_path, 0o755)
            except:
                pass
            
            return script_name
        except Exception as e:
            print(f"❌ Errore nella creazione dello script di ripristino: {e}")
            return None
    
    def _generate_script_content(self) -> str:
        """Genera il contenuto dello script di ripristino"""
        lang = self.text_manager.language
        
        if lang == 'en':
            header_comment = "TV Renamer - Restore Script"
            description = "This script restores the original filenames"
            warning = "WARNING: This script will restore the original filenames!"
            confirm_msg = "Do you want to proceed? (y/N): "
            cancelled_msg = "Operation cancelled."
            processing_msg = "Processing restores..."
            not_found_msg = "File not found"
        else:
            header_comment = "TV Renamer - Script di Ripristino"
            description = "Questo script ripristina i nomi file originali"
            warning = "ATTENZIONE: Questo script ripristinerà i nomi file originali!"
            confirm_msg = "Vuoi procedere? (s/N): "
            cancelled_msg = "Operazione annullata."
            processing_msg = "Elaborazione ripristini..."
            not_found_msg = "File non trovato"
        
        # Prepara la lista delle rinomine per il codice Python
        renames_code = "    # (current_name, original_name)\n    renames = [\n"
        for old_name, new_name in self.renames:
            # Escapa le stringhe per Python
            old_escaped = repr(old_name)
            new_escaped = repr(new_name)
            renames_code += f"        ({new_escaped}, {old_escaped}),\n"
        renames_code += "    ]\n"
        
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{header_comment}
{description}

Creato automaticamente da Universal TV Series Renamer
Data: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

import os
import sys
from pathlib import Path

def main():
    print("📺 {header_comment}")
    print("=" * 50)
    print("{warning}")
    print()
    
    # Directory dello script
    script_dir = Path(__file__).parent.absolute()
    print(f"📁 Directory: {{script_dir}}")
    print()
    
{renames_code}
    
    print(f"📋 Trovati {{len(renames)}} file da ripristinare")
    
    # Conferma utente
    try:
        confirm = input("{confirm_msg}").strip().lower()
        if confirm not in ['s', 'y', 'si', 'yes']:
            print("{cancelled_msg}")
            return
    except KeyboardInterrupt:
        print("\\n{cancelled_msg}")
        return
    
    print("\\n{processing_msg}")
    print("=" * 80)
    print(f"{{'STATO':<10}} {{'FILE CORRENTE':<35}} {{'NOME ORIGINALE':<35}}")
    print("-" * 80)
    
    successi = 0
    errori = 0
    
    for current_name, original_name in renames:
        current_path = script_dir / current_name
        original_path = script_dir / original_name
        
        # Tronca nomi per visualizzazione
        current_display = current_name[:32] + "..." if len(current_name) > 35 else current_name
        original_display = original_name[:32] + "..." if len(original_name) > 35 else original_name
        
        try:
            if not current_path.exists():
                print(f"{{'❌ SKIP':<10}} {{current_display:<35}} {{original_display:<35}} ({not_found_msg})")
                errori += 1
                continue
            
            if original_path.exists():
                print(f"{{'❌ EXISTS':<10}} {{current_display:<35}} {{original_display:<35}}")
                errori += 1
                continue
            
            # Rinomina
            current_path.rename(original_path)
            print(f"{{'✅ OK':<10}} {{current_display:<35}} {{original_display:<35}}")
            successi += 1
            
        except Exception as e:
            error_detail = str(e)[:20] + "..." if len(str(e)) > 20 else str(e)
            print(f"{{'❌ ERROR':<10}} {{current_display:<35}} {{error_detail:<35}}")
            errori += 1
    
    print("=" * 80)
    print(f"📊 RISULTATI: {{successi}} successi, {{errori}} errori")
    
    if successi > 0:
        print("\\n✅ Ripristino completato!")
        
        # Rimuovi questo script dopo il successo
        try:
            script_path = Path(__file__)
            print(f"🗑️  Rimozione script: {{script_path.name}}")
            script_path.unlink()
        except:
            print("⚠️  Non è stato possibile rimuovere automaticamente lo script")
    
    input("\\nPremi INVIO per uscire...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n👋 Operazione interrotta")
    except Exception as e:
        print(f"\\n❌ Errore: {{e}}")
        input("Premi INVIO per uscire...")
'''

# ============================================================================
# RENAMER PRINCIPALE
# ============================================================================

class TVSeriesRenamer:
    """Renamer principale"""
    
    def __init__(self, config: Config):
        self.config = config
        self.text_manager = TextManager(config.interface_language)
        self.http_client = SafeHTTPClient(config)
        self.searcher = MultiProviderSearcher(config, self.http_client)
    
    def interactive_series_selection(self, results: List[SeriesInfo], series_name: str) -> Optional[SeriesInfo]:
        """Selezione interattiva serie"""
        if not results:
            print(self.text_manager.get('no_series_found', series_name))
            return None
        
        print(f"\n{self.text_manager.get('search_results')} '{series_name}':")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            name = html.unescape(result.name)
            line = f"{i:2d}. {result.source}"
            
            if result.source == 'IMDb':
                line += f" ({result.id})"
            
            line += f" | {name}"
            
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
    
    def check_missing_episodes(self, episodes_found: List[Tuple[int, int]]):
        """Controlla episodi mancanti"""
        lang = self.text_manager.language
        
        # Raggruppa per stagione
        seasons = {}
        for season, episode in episodes_found:
            if season not in seasons:
                seasons[season] = []
            seasons[season].append(episode)
        
        missing_found = False
        for season, episodes in seasons.items():
            episodes.sort()
            
            # Trova episodi mancanti
            if len(episodes) > 1:
                min_ep = min(episodes)
                max_ep = max(episodes)
                expected = set(range(min_ep, max_ep + 1))
                found = set(episodes)
                missing = sorted(expected - found)
                
                if missing:
                    if not missing_found:
                        print(f"\n⚠️  {'EPISODI MANCANTI RILEVATI:' if lang == 'it' else 'MISSING EPISODES DETECTED:'}")
                        missing_found = True
                    
                    missing_str = ", ".join([f"E{ep:02d}" for ep in missing])
                    print(f"   📺 {'Stagione' if lang == 'it' else 'Season'} {season}: {'Mancano' if lang == 'it' else 'Missing'} {missing_str}")
        
        if missing_found:
            print("=" * 80)
            suggestion = "💡 Suggerimento: Verifica se hai tutti gli episodi della serie" if lang == 'it' else "💡 Suggestion: Check if you have all episodes of the series"
            print(f"{suggestion}")
            print("=" * 80)
    
    def generate_filename(self, series_name: str, season: int, episode: int, 
                         episode_title: str, original_ext: str) -> str:
        """Genera nuovo nome file"""
        series_name = FileUtils.clean_filename(series_name)
        episode_title = FileUtils.clean_filename(episode_title)
        
        formats = {
            "standard": f"{series_name} - [{season:02d}x{episode:02d}] - {episode_title}{original_ext}",
            "plex": f"{series_name} - S{season:02d}E{episode:02d} - {episode_title}{original_ext}",
            "simple": f"{series_name} {season}x{episode:02d} {episode_title}{original_ext}",
            "minimal": f"{series_name} S{season:02d}E{episode:02d}{original_ext}",
            "kodi": f"{series_name} S{season:02d}E{episode:02d} {episode_title}{original_ext}"
        }
        
        return formats.get(self.config.format_style, formats["standard"])
    
    def process_directory(self, directory: Path):
        """Processa directory"""
        print(self.text_manager.get('header'))
        print(self.text_manager.get('developer'))
        print(self.text_manager.get('license'))
        print("=" * 50)
        print(f"{self.text_manager.get('directory')} {directory.absolute()}")
        print(f"{self.text_manager.get('format')} {self.config.format_style}")
        print(f"{self.text_manager.get('language')} {self.config.language}")
        print(f"{self.text_manager.get('recursive')} {self.text_manager.get('yes') if self.config.recursive else self.text_manager.get('no')}")
        print(f"{self.text_manager.get('mode')} {self.text_manager.get('execution') if not self.config.dry_run else self.text_manager.get('preview')}")
        print("=" * 50)
        
        # Trova file video
        video_files = FileUtils.find_video_files(directory, self.config.recursive)
        
        if not video_files:
            print(self.text_manager.get('no_files'))
            return
        
        print(f"\n{self.text_manager.get('files_found', len(video_files))}")
        
        # Raggruppa per serie
        series_groups = {}
        for video_file in video_files:
            series_name = FileUtils.extract_series_info(video_file.name)
            if series_name not in series_groups:
                series_groups[series_name] = []
            series_groups[series_name].append(video_file)
        
        # Processa ogni serie
        for series_name, files in series_groups.items():
            print(f"\n{'='*80}")
            print(f"{self.text_manager.get('series_title')} {series_name} ({len(files)} file)")
            print(f"{'='*80}")
            
            self.process_series(series_name, files, directory)
    
    def process_series(self, series_name: str, files: List[Path], directory: Path):
        """Processa una serie specifica"""
        print(f"{self.text_manager.get('searching_for')} '{series_name}'")
        
        # Cerca serie
        results = self.searcher.search_series(series_name)
        
        if not results:
            print(f"{self.text_manager.get('no_series_found', series_name)}")
            print(self.text_manager.get('suggestions'))
            print(self.text_manager.get('check_spelling'))
            print(self.text_manager.get('try_english'))
            print(self.text_manager.get('use_shorter'))
            return
        
        # Selezione interattiva
        selected_series = self.interactive_series_selection(results, series_name)
        if not selected_series:
            print(f"{self.text_manager.get('skipping_series')} {series_name}")
            return
        
        # Processa file e gestisci duplicati
        renames = []
        episodes_found = []
        episode_files = {}  # (season, episode) -> [files]
        
        # Raggruppa file per episodio
        for video_file in files:
            season, episode = FileUtils.extract_episode_info(video_file.name)
            
            if season is None or episode is None:
                print(self.text_manager.get('skip_unrecognized', video_file.name))
                continue
            
            episodes_found.append((season, episode))
            
            ep_key = (season, episode)
            if ep_key not in episode_files:
                episode_files[ep_key] = []
            episode_files[ep_key].append(video_file)
        
        # Controlla episodi mancanti
        if episodes_found:
            self.check_missing_episodes(episodes_found)
        
        # Processa ogni gruppo di episodi
        for (season, episode), file_list in episode_files.items():
            # Ottieni info episodio
            episode_info = self.searcher.get_episode_info(selected_series, season, episode)
            episode_title = episode_info.title if episode_info else f"Episode {episode}"
            
            if len(file_list) == 1:
                # File singolo
                video_file = file_list[0]
                new_name = self.generate_filename(
                    selected_series.name, season, episode, episode_title, video_file.suffix
                )
                renames.append((video_file, new_name))
            else:
                # File multipli - gestisci duplicati
                print(f"\n🔄 {'DUPLICATI RILEVATI' if self.text_manager.language == 'it' else 'DUPLICATES DETECTED'}: S{season:02d}E{episode:02d} - {len(file_list)} file")
                
                # Ordina per dimensione (più grande presumibilmente migliore)
                file_list.sort(key=lambda f: f.stat().st_size, reverse=True)
                
                # Mostra info sui file
                for i, video_file in enumerate(file_list):
                    size_mb = video_file.stat().st_size / (1024 * 1024)
                    print(f"   {i+1}. {video_file.name} ({size_mb:.1f} MB)")
                
                for i, video_file in enumerate(file_list):
                    # Tutti i file duplicati hanno [Versione X]
                    version_text = f"[Versione {i+1}]" if self.text_manager.language == 'it' else f"[Version {i+1}]"
                    series_clean = FileUtils.clean_filename(selected_series.name)
                    episode_clean = FileUtils.clean_filename(episode_title)
                    
                    formats = {
                        "standard": f"{series_clean} - [{season:02d}x{episode:02d}] - {episode_clean} {version_text}{video_file.suffix}",
                        "plex": f"{series_clean} - S{season:02d}E{episode:02d} - {episode_clean} {version_text}{video_file.suffix}",
                        "simple": f"{series_clean} {season}x{episode:02d} {episode_clean} {version_text}{video_file.suffix}",
                        "minimal": f"{series_clean} S{season:02d}E{episode:02d} {version_text}{video_file.suffix}",
                        "kodi": f"{series_clean} S{season:02d}E{episode:02d} {episode_clean} {version_text}{video_file.suffix}"
                    }
                    new_name = formats.get(self.config.format_style, formats["standard"])
                    
                    renames.append((video_file, new_name))
        
        # Esegui rinomine
        if renames:
            self.execute_renames(renames, directory)
    
    def execute_renames(self, renames: List[Tuple[Path, str]], directory: Path):
        """Esegue le rinomine"""
        restore_manager = RestoreManager(directory, self.text_manager)
        
        print(f"\n📋 {self.text_manager.get('execution') if not self.config.dry_run else self.text_manager.get('preview')} - {len(renames)} file")
        print("=" * 120)
        
        if self.text_manager.language == 'en':
            print(f"{'STATUS':<8} {'ORIGINAL FILE':<50} {'NEW FILE':<50}")
        else:
            print(f"{'STATO':<8} {'FILE ORIGINALE':<50} {'NUOVO FILE':<50}")
        print("-" * 120)
        
        success_count = 0
        error_count = 0
        
        for old_path, new_name in renames:
            new_path = old_path.parent / new_name
            
            # Tronca nomi per tabella
            old_display = old_path.name[:47] + "..." if len(old_path.name) > 50 else old_path.name
            new_display = new_name[:47] + "..." if len(new_name) > 50 else new_name
            
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
                    
                    # Aggiungi al restore manager e rinomina
                    restore_manager.add_rename(old_path.name, new_name)
                    old_path.rename(new_path)
                    print(f"{'✅ DONE':<8} {old_display:<50} {new_display:<50}")
                    success_count += 1
                except Exception as e:
                    error_msg = str(e)[:20] + "..." if len(str(e)) > 20 else str(e)
                    print(f"{'❌ ERROR':<8} {old_display:<50} {error_msg:<50}")
                    error_count += 1
        
        print("=" * 120)
        print(self.text_manager.get('results', success_count, error_count))
        
        # Crea script di ripristino se ci sono stati successi
        if not self.config.dry_run and restore_manager.renames:
            try:
                script_name = restore_manager.create_restore_script()
                if script_name:
                    print(f"\n{self.text_manager.get('restore_script_created', script_name)}")
                    print(f"{self.text_manager.get('restore_instructions', script_name)}")
            except Exception as e:
                print(f"\n❌ Errore nella creazione dello script di ripristino: {e}")

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
    
    # Verifica directory
    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"❌ ERRORE: '{args.directory}' non è una directory valida!")
        sys.exit(1)
    
    try:
        # Configurazione
        config = Config.from_args(args)
        
        # Crea renamer e processa
        renamer = TVSeriesRenamer(config)
        renamer.process_directory(directory)
        
    except KeyboardInterrupt:
        print("\n👋 Operazione interrotta dall'utente")
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERRORE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
