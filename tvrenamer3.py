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
from typing import Optional, Dict, List, Tuple, Set
from dataclasses import dataclass
from collections import Counter
from abc import ABC, abstractmethod
from enum import Enum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================================
# CONFIGURAZIONE E MODELLI
# ============================================================================

class FormatStyle(Enum):
    STANDARD = "standard"
    PLEX = "plex"
    SIMPLE = "simple"
    MINIMAL = "minimal"
    KODI = "kodi"

class Language(Enum):
    ITALIAN = "it"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"

@dataclass(frozen=True)
class Config:
    """Configurazione immutabile dell'applicazione"""
    tmdb_api_key: Optional[str] = None
    timeout: int = 10
    max_retries: int = 3
    language: Language = Language.ITALIAN
    interface_language: Language = Language.ITALIAN
    format_style: FormatStyle = FormatStyle.STANDARD
    recursive: bool = False
    dry_run: bool = True

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'Config':
        return cls(
            tmdb_api_key=args.tmdb_key or os.getenv('TMDB_API_KEY'),
            language=Language(args.language),
            interface_language=Language(args.interface),
            format_style=FormatStyle(args.format),
            recursive=args.recursive,
            dry_run=not args.execute
        )

@dataclass(frozen=True)
class SeriesInfo:
    """Informazioni su una serie TV"""
    id: str
    name: str
    year: str
    overview: str
    source: str
    vote_average: Optional[float] = None

@dataclass(frozen=True)
class EpisodeInfo:
    """Informazioni su un episodio"""
    title: str
    season: int
    episode: int

@dataclass(frozen=True)
class RenameOperation:
    """Operazione di rinomina"""
    old_path: Path
    new_name: str

# ============================================================================
# UTILITÀ E COSTANTI
# ============================================================================

class Constants:
    """Costanti dell'applicazione"""
    VIDEO_EXTENSIONS = {'.mkv', '.avi', '.mp4', '.m4v', '.mov', '.wmv', '.flv', '.webm', '.ts', '.m2ts'}
    
    GENERIC_NAMES = {
        'downloads', 'download', 'episodi', 'episodes', 'tv', 'series', 'tv series', 
        'tv shows', 'shows', 'video', 'videos', 'media', 'file', 'files',
        'season', 'stagione', 'complete', 'completo', 'finished', 'finito'
    }
    
    SERIES_CORRECTIONS = {
        'better call soul': 'Better Call Saul',
        'breaking bad': 'Breaking Bad',
        'game of thrones': 'Game of Thrones',
        'the walking dead': 'The Walking Dead',
        'stranger things': 'Stranger Things',
        'quantum leap': 'Quantum Leap'
    }

class FileUtils:
    """Utilità per la gestione dei file"""
    
    @staticmethod
    def find_video_files(directory: Path, recursive: bool = False) -> List[Path]:
        """Trova tutti i file video in una directory"""
        files = []
        pattern = directory.rglob('*') if recursive else directory.iterdir()
        
        for file_path in pattern:
            if (file_path.is_file() and 
                file_path.suffix.lower() in Constants.VIDEO_EXTENSIONS and
                not file_path.name.startswith('.')):
                files.append(file_path)
        
        return sorted(files)
    
    @staticmethod
    def clean_filename(name: str) -> str:
        """Pulisce un nome file da caratteri non validi"""
        name = html.unescape(name)
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')
        name = name.replace('&', 'and')
        return re.sub(r'\s+', ' ', name).strip()

class PatternUtils:
    """Utilità per l'estrazione di pattern dai nomi file"""
    
    SEASON_EPISODE_PATTERNS = [
        r'[Ss](\d+)[Ee](\d+)',
        r'(\d+)x(\d+)',
        r'[Ss]eason\s*(\d+).*[Ee]pisode\s*(\d+)'
    ]
    
    @classmethod
    def extract_season_episode(cls, filename: str) -> Tuple[Optional[int], Optional[int]]:
        """Estrae numero stagione e episodio dal nome file"""
        for pattern in cls.SEASON_EPISODE_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return int(match.group(1)), int(match.group(2))
        return None, None
    
    @classmethod
    def find_season_episode_position(cls, text: str) -> int:
        """Trova la posizione del pattern stagione/episodio nel testo"""
        patterns = [r'[Ss]\d+[Ee]\d+', r'\d+x\d+', r'[Ss]eason\s*\d+']
        earliest = len(text)
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                earliest = min(earliest, match.start())
        
        return earliest

# ============================================================================
# ESTRATTORE NOME SERIE
# ============================================================================

class SeriesExtractor:
    """Estrattore intelligente del nome della serie dai file"""
    
    @classmethod
    def extract_from_files(cls, files: List[Path], directory_name: str = "") -> str:
        """Estrae il nome della serie da una lista di file"""
        if not files:
            return "Unknown Series"
        
        # Strategia 1: Estrai da nomi file
        series_from_files = cls._extract_from_filenames(files)
        if series_from_files != "Unknown Series":
            return cls._clean_and_correct(series_from_files)
        
        # Strategia 2: Usa directory se significativa
        series_from_dir = cls._extract_from_directory(directory_name)
        if series_from_dir != "Unknown Series":
            return cls._clean_and_correct(series_from_dir)
        
        # Strategia 3: Analizza pattern comuni
        series_from_patterns = cls._extract_from_patterns(files)
        if series_from_patterns != "Unknown Series":
            return cls._clean_and_correct(series_from_patterns)
        
        return "Unknown Series"
    
    @classmethod
    def _extract_from_filenames(cls, files: List[Path]) -> str:
        """Estrae il nome della serie dai nomi dei file"""
        series_candidates = []
        
        for file_path in files[:10]:  # Analizza solo i primi 10 file
            stem = file_path.stem
            season_pos = PatternUtils.find_season_episode_position(stem)
            
            if season_pos > 0:
                series_part = stem[:season_pos].strip()
                series_part = re.sub(r'[\s\-\._]+', ' ', series_part)
                
                if len(series_part) >= 3:
                    series_candidates.append(series_part.lower())
        
        if series_candidates:
            counter = Counter(series_candidates)
            most_common = counter.most_common(1)[0]
            
            if most_common[1] >= len(series_candidates) * 0.7:
                return most_common[0]
        
        return "Unknown Series"
    
    @classmethod
    def _extract_from_directory(cls, directory_name: str) -> str:
        """Estrae il nome della serie dal nome della directory"""
        if not directory_name or not cls._is_meaningful_directory(directory_name):
            return "Unknown Series"
        
        cleaned = directory_name.lower()
        
        # Rimuovi suffissi comuni
        suffixes = [
            r'\.finito', r'\.completo', r'\.complete', r'\.finished',
            r'\s*-\s*(complete|completo|finito).*', r'\s*\(\d{4}\).*',
            r'\s*\[.*?\].*', r'\s*S\d+.*'
        ]
        
        for suffix in suffixes:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        cleaned = re.sub(r'[._]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned if len(cleaned) >= 3 else "Unknown Series"
    
    @classmethod
    def _extract_from_patterns(cls, files: List[Path]) -> str:
        """Estrae il nome della serie analizzando pattern comuni"""
        words_counter = Counter()
        
        for file_path in files[:10]:
            stem = file_path.stem
            
            # Rimuovi pattern comuni
            cleaned = re.sub(r'[Ss]\d+[Ee]\d+.*', '', stem)
            cleaned = re.sub(r'\d+x\d+.*', '', cleaned)
            cleaned = re.sub(r'(720p|1080p|480p|2160p|4K|HDTV|WEB-?DL|BluRay|BDRip|DVDRip).*', 
                           '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'\[.*?\]', '', cleaned)
            cleaned = re.sub(r'\(.*?\)', '', cleaned)
            
            words = re.findall(r'[A-Za-z]{3,}', cleaned)
            for word in words:
                words_counter[word.lower()] += 1
        
        min_frequency = max(1, len(files) // 2)
        common_words = [word for word, count in words_counter.items() 
                       if count >= min_frequency]
        
        if common_words:
            series_words = sorted(common_words, key=lambda w: words_counter[w], reverse=True)[:3]
            return ' '.join(series_words)
        
        return "Unknown Series"
    
    @classmethod
    def _clean_and_correct(cls, series_name: str) -> str:
        """Pulisce e corregge il nome serie"""
        if not series_name or series_name == "Unknown Series":
            return series_name
        
        cleaned = series_name.lower()
        
        # Rimuovi anni alla fine
        cleaned = re.sub(r'\.\d{4}', '', cleaned)
        cleaned = re.sub(r'\s+\d{4}', '', cleaned)
        cleaned = re.sub(r'\(\d{4}\)', '', cleaned)
        
        # Sostituisci separatori con spazi
        cleaned = re.sub(r'[._\-]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Applica correzioni note
        for incorrect, correct in Constants.SERIES_CORRECTIONS.items():
            if incorrect in cleaned:
                return correct
        
        return cleaned.title()
    
    @classmethod
    def _is_meaningful_directory(cls, directory_name: str) -> bool:
        """Verifica se il nome della directory è significativo"""
        cleaned = re.sub(r'[^\w\s]', '', directory_name.lower().strip())
        
        if len(cleaned) < 3:
            return False
        
        if cleaned in Constants.GENERIC_NAMES:
            return False
        
        if re.match(r'^[\d\s\-\.]+', cleaned):
            return False
        
        return True

# ============================================================================
# COSTRUTTORE NOMI FILE
# ============================================================================

class FilenameBuilder:
    """Costruttore di nomi file per diversi formati"""
    
    FORMAT_TEMPLATES = {
        FormatStyle.STANDARD: "{series} - S{season:02d}E{episode:02d} - {title}{ext}",
        FormatStyle.PLEX: "{series} - S{season:02d}E{episode:02d} - {title}{ext}",
        FormatStyle.SIMPLE: "{series} {season}x{episode:02d} {title}{ext}",
        FormatStyle.MINIMAL: "{series} S{season:02d}E{episode:02d}{ext}",
        FormatStyle.KODI: "{series} S{season:02d}E{episode:02d} {title}{ext}"
    }
    
    @classmethod
    def build(cls, series_name: str, season: int, episode: int, 
              episode_title: str, extension: str, format_style: FormatStyle) -> str:
        """Costruisce il nome file nel formato specificato"""
        template = cls.FORMAT_TEMPLATES.get(format_style, cls.FORMAT_TEMPLATES[FormatStyle.STANDARD])
        
        return template.format(
            series=FileUtils.clean_filename(series_name),
            season=season,
            episode=episode,
            title=FileUtils.clean_filename(episode_title),
            ext=extension
        )

# ============================================================================
# PROVIDER API (PATTERN STRATEGY)
# ============================================================================

class HTTPClient:
    """Client HTTP con retry e rate limiting"""
    
    def __init__(self, config: Config):
        self.session = requests.Session()
        self.timeout = config.timeout
        self._last_call = 0
        self._min_interval = 0.2
        
        # Configura retry strategy
        retry_strategy = Retry(
            total=config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            'User-Agent': 'UniversalTVRenamer/1.2',
            'Accept': 'application/json'
        })
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Esegue una richiesta GET con rate limiting"""
        elapsed = time.time() - self._last_call
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        
        kwargs.setdefault('timeout', self.timeout)
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        
        self._last_call = time.time()
        return response

class SimpleCache:
    """Cache semplice con TTL"""
    
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._cache: Dict = {}
        self._timestamps: Dict = {}
    
    def get(self, key: str):
        """Recupera un valore dalla cache"""
        if key not in self._cache:
            return None
        
        if time.time() - self._timestamps[key] > self.ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value):
        """Imposta un valore nella cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()

class APIProvider(ABC):
    """Classe base astratta per i provider API"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
        self.cache = SimpleCache()
    
    @abstractmethod
    def search_series(self, query: str) -> List[SeriesInfo]:
        """Cerca serie TV"""
        pass
    
    @abstractmethod
    def get_episode_info(self, series_id: str, season: int, episode: int) -> Optional[EpisodeInfo]:
        """Ottiene informazioni su un episodio"""
        pass

class TMDBProvider(APIProvider):
    """Provider per The Movie Database"""
    
    def __init__(self, api_key: str, http_client: HTTPClient, language: Language):
        super().__init__(http_client)
        self.api_key = api_key
        self.language = language
        self.base_url = "https://api.themoviedb.org/3"
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        cache_key = f"tmdb_{query}_{self.language.value}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/search/tv"
            params = {
                'api_key': self.api_key,
                'query': query,
                'language': f'{self.language.value}-{self.language.value.upper()}'
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
                    vote_average=item.get('vote_average')
                )
                results.append(series)
            
            self.cache.set(cache_key, results)
            return results
        except Exception:
            return []
    
    def get_episode_info(self, series_id: str, season: int, episode: int) -> Optional[EpisodeInfo]:
        cache_key = f"tmdb_ep_{series_id}_{season}_{episode}_{self.language.value}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/tv/{series_id}/season/{season}/episode/{episode}"
            params = {
                'api_key': self.api_key,
                'language': f'{self.language.value}-{self.language.value.upper()}'
            }
            
            response = self.http_client.get(url, params=params)
            data = response.json()
            
            episode_info = EpisodeInfo(
                title=data.get('name', f'Episode {episode}'),
                season=season,
                episode=episode
            )
            
            self.cache.set(cache_key, episode_info)
            return episode_info
        except Exception:
            return None

class TVMazeProvider(APIProvider):
    """Provider per TVMaze"""
    
    def __init__(self, http_client: HTTPClient):
        super().__init__(http_client)
        self.base_url = "https://api.tvmaze.com"
    
    def search_series(self, query: str) -> List[SeriesInfo]:
        cache_key = f"tvmaze_{query}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/search/shows"
            response = self.http_client.get(url, params={'q': query})
            data = response.json()
            
            results = []
            for item in data[:5]:
                show = item.get('show', {})
                summary = re.sub(r'<[^>]+>', '', show.get('summary', '') or '').strip()
                
                series = SeriesInfo(
                    id=str(show.get('id')),
                    name=show.get('name', 'Nome non disponibile'),
                    year=show.get('premiered', '')[:4] if show.get('premiered') else '',
                    overview=summary,
                    source='TVMaze',
                    vote_average=show.get('rating', {}).get('average') if show.get('rating') else None
                )
                results.append(series)
            
            self.cache.set(cache_key, results)
            return results
        except Exception:
            return []
    
    def get_episode_info(self, series_id: str, season: int, episode: int) -> Optional[EpisodeInfo]:
        cache_key = f"tvmaze_ep_{series_id}_{season}_{episode}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/shows/{series_id}/episodebynumber"
            response = self.http_client.get(url, params={'season': season, 'number': episode})
            data = response.json()
            
            episode_info = EpisodeInfo(
                title=data.get('name', f'Episode {episode}'),
                season=season,
                episode=episode
            )
            
            self.cache.set(cache_key, episode_info)
            return episode_info
        except Exception:
            return None

# ============================================================================
# GESTORE API
# ============================================================================

class APIManager:
    """Gestore che coordina múltipli provider API"""
    
    def __init__(self, config: Config, http_client: HTTPClient):
        self.providers: List[APIProvider] = []
        
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
        """Cerca serie utilizzando tutti i provider disponibili"""
        all_results = []
        
        for provider in self.providers:
            try:
                results = provider.search_series(query)
                all_results.extend(results)
            except Exception:
                continue
        
        return self._deduplicate_results(all_results)
    
    def get_episode_info(self, series_info: SeriesInfo, season: int, episode: int) -> Optional[EpisodeInfo]:
        """Ottiene informazioni sull'episodio dal provider appropriato"""
        for provider in self.providers:
            provider_name = provider.__class__.__name__.replace('Provider', '')
            if provider_name == series_info.source:
                try:
                    return provider.get_episode_info(series_info.id, season, episode)
                except Exception:
                    continue
        return None
    
    def _deduplicate_results(self, results: List[SeriesInfo]) -> List[SeriesInfo]:
        """Rimuove duplicati dai risultati"""
        seen: Set[Tuple] = set()
        unique = []
        
        for result in results:
            key = (result.name.lower().replace(' ', ''), result.source, result.year)
            if key not in seen:
                seen.add(key)
                unique.append(result)
        
        return unique[:10]

# ============================================================================
# INTERFACCIA UTENTE
# ============================================================================

class TextManager:
    """Gestore dei testi multilingua"""
    
    TEXTS = {
        Language.ITALIAN: {
            'header': "📺 Universal TV Series Renamer v1.2 (Refactored)",
            'developer': "👨‍💻 Sviluppato da: Andres Zanzani",
            'license': "📄 Licenza: GPL-3.0",
            'files_found': "📁 Trovati {} file video",
            'no_files': "❌ Nessun file video trovato!",
            'searching_for': "🔍 Ricerca in corso per:",
            'no_series_found': "❌ Nessuna serie trovata per: '{}'",
            'search_results': "🔍 Risultati di ricerca per:",
            'none_above': "❌ Nessuna delle opzioni sopra",
            'exit': "🚪 Esci dal programma",
            'select_prompt': "Seleziona (1-{}, 0, q):",
            'results': "📊 RISULTATI: ✅ {} successi, ❌ {} errori",
            'preview': "PREVIEW",
            'execution': "ESECUZIONE",
            'restore_script_created': "📄 Script di ripristino creato: {}",
            'restore_instructions': "💡 Per ripristinare i nomi originali, esegui: python {}"
        },
        Language.ENGLISH: {
            'header': "📺 Universal TV Series Renamer v1.2 (Refactored)",
            'developer': "👨‍💻 Developed by: Andres Zanzani",
            'license': "📄 License: GPL-3.0",
            'files_found': "📁 Found {} video files",
            'no_files': "❌ No video files found!",
            'searching_for': "🔍 Searching for:",
            'no_series_found': "❌ No series found for: '{}'",
            'search_results': "🔍 Results for:",
            'none_above': "❌ None of the above options",
            'exit': "🚪 Exit",
            'select_prompt': "Select (1-{}, 0, q):",
            'results': "📊 RESULTS: ✅ {} successes, ❌ {} errors",
            'preview': "PREVIEW",
            'execution': "EXECUTION",
            'restore_script_created': "📄 Restore script created: {}",
            'restore_instructions': "💡 To restore original names, run: python {}"
        }
    }
    
    def __init__(self, language: Language):
        self.language = language
    
    def get(self, key: str, *args) -> str:
        """Ottiene un testo tradotto"""
        text = self.TEXTS.get(self.language, self.TEXTS[Language.ITALIAN]).get(key, key)
        if args:
            try:
                return text.format(*args)
            except:
                return text
        return text

class UserInterface:
    """Interfaccia utente per l'interazione"""
    
    def __init__(self, text_manager: TextManager):
        self.text_manager = text_manager
    
    def show_header(self, config: Config, directory: Path):
        """Mostra l'header dell'applicazione"""
        print(self.text_manager.get('header'))
        print(self.text_manager.get('developer'))
        print(self.text_manager.get('license'))
        print("=" * 50)
        print(f"📁 Directory: {directory.absolute()}")
        print(f"🎨 Formato: {config.format_style.value}")
        print(f"🌍 Lingua: {config.language.value}")
        mode = self.text_manager.get('execution') if not config.dry_run else self.text_manager.get('preview')
        print(f"⚙️  Modalità: {mode}")
        print("=" * 50)
    
    def select_series(self, results: List[SeriesInfo], series_name: str) -> Optional[SeriesInfo]:
        """Permette all'utente di selezionare una serie"""
        if not results:
            print(self.text_manager.get('no_series_found', series_name))
            return None
        
        print(f"\n{self.text_manager.get('search_results')} '{series_name}':")
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
        
        return self._get_user_choice(len(results))
    
    def _get_user_choice(self, max_choice: int) -> Optional[SeriesInfo]:
        """Gestisce l'input dell'utente per la selezione"""
        while True:
            try:
                choice = input(f"{self.text_manager.get('select_prompt', max_choice)} ").strip().lower()
                
                if choice == 'q':
                    sys.exit(0)
                elif choice == '0':
                    return None
                else:
                    choice_num = int(choice) - 1
                    if 0 <= choice_num < max_choice:
                        return choice_num  # Restituisce l'indice per la selezione
                    else:
                        print("❌ Selezione non valida!")
            except (ValueError, KeyboardInterrupt):
                if choice == 'q':
                    sys.exit(0)
                print("❌ Selezione non valida!")

# ============================================================================
# RINOMINATORE PRINCIPALE
# ============================================================================

class TVSeriesRenamer:
    """Classe principale per la rinomina delle serie TV"""
    
    def __init__(self, config: Config):
        self.config = config
        self.text_manager = TextManager(config.interface_language)
        self.ui = UserInterface(self.text_manager)
        self.http_client = HTTPClient(config)
        self.api_manager = APIManager(config, self.http_client)
    
    def process_directory(self, directory: Path):
        """Processa una directory per la rinomina"""
        self.ui.show_header(self.config, directory)
        
        # Trova file video
        video_files = FileUtils.find_video_files(directory, self.config.recursive)
        
        if not video_files:
            print(self.text_manager.get('no_files'))
            return
        
        print(f"\n{self.text_manager.get('files_found', len(video_files))}")
        
        # Ottieni nome directory corretto
        directory_name = Path.cwd().name if str(directory) in ['.', './'] else directory.name
        
        # Estrai nome serie intelligentemente
        series_name = SeriesExtractor.extract_from_files(video_files, directory_name)
        
        print(f"📺 Serie rilevata: '{series_name}'")
        
        if series_name == "Unknown Series":
            print("⚠️  Impossibile rilevare automaticamente il nome della serie.")
            print("💡 Suggerimenti:")
            print("   - Assicurati che i file abbiano il nome della serie nel filename")
            print("   - Oppure rinomina la directory con il nome della serie")
            return
        
        # Processa la serie
        self._process_series(series_name, video_files, directory)
    
    def _process_series(self, series_name: str, files: List[Path], directory: Path):
        """Processa una serie specifica"""
        print(f"\n{'='*80}")
        print(f"📺 SERIE: {series_name} ({len(files)} file)")
        print(f"{'='*80}")
        print(f"{self.text_manager.get('searching_for')} '{series_name}'")
        
        # Cerca serie online
        results = self.api_manager.search_series(series_name)
        choice_index = self.ui.select_series(results, series_name)
        
        if choice_index is None:
            print(f"⏭️  Saltando serie: {series_name}")
            return
        
        selected_series = results[choice_index]
        
        # Prepara operazioni di rinomina
        operations = self._prepare_rename_operations(selected_series, files)
        
        if not operations:
            print("⚠️  Nessuna rinomina da eseguire per questa serie.")
            return
        
        # Esegui rinomine
        self._execute_renames(operations, directory)
    
    def _prepare_rename_operations(self, series: SeriesInfo, files: List[Path]) -> List[RenameOperation]:
        """Prepara le operazioni di rinomina"""
        operations = []
        episode_files = {}
        
        # Raggruppa file per episodio
        for video_file in files:
            season, episode = PatternUtils.extract_season_episode(video_file.name)
            
            if season is None or episode is None:
                print(f"⚠️  SKIP: {video_file.name} (formato non riconosciuto)")
                continue
            
            ep_key = (season, episode)
            if ep_key not in episode_files:
                episode_files[ep_key] = []
            episode_files[ep_key].append(video_file)
        
        # Crea operazioni per ogni episodio
        for (season, episode), file_list in episode_files.items():
            episode_info = self.api_manager.get_episode_info(series, season, episode)
            episode_title = episode_info.title if episode_info else f"Episode {episode}"
            
            for i, video_file in enumerate(file_list):
                new_name = FilenameBuilder.build(
                    series.name, season, episode, episode_title, 
                    video_file.suffix, self.config.format_style
                )
                
                # Se ci sono duplicati, aggiungi versione
                if len(file_list) > 1:
                    version_text = f"[Versione {i+1}]" if self.config.interface_language == Language.ITALIAN else f"[Version {i+1}]"
                    name_part, ext = os.path.splitext(new_name)
                    new_name = f"{name_part} {version_text}{ext}"
                
                # Skip se il file è già nel formato corretto
                if video_file.name == new_name:
                    if self.config.dry_run:
                        print(f"⏭️  SKIP: {video_file.name} (già corretto)")
                    continue
                
                operations.append(RenameOperation(
                    old_path=video_file,
                    new_name=new_name
                ))
        
        return operations
    
    def _execute_renames(self, operations: List[RenameOperation], directory: Path):
        """Esegue le operazioni di rinomina"""
        restore_manager = RestoreScriptManager(directory, self.text_manager)
        
        mode = self.text_manager.get('execution') if not self.config.dry_run else self.text_manager.get('preview')
        print(f"\n📋 {mode} - {len(operations)} operazioni")
        print("=" * 100)
        
        if self.config.interface_language == Language.ENGLISH:
            print(f"{'STATUS':<8} {'ORIGINAL FILE':<45} {'NEW FILE':<45}")
        else:
            print(f"{'STATO':<8} {'FILE ORIGINALE':<45} {'NUOVO FILE':<45}")
        print("-" * 100)
        
        success_count = 0
        error_count = 0
        
        for operation in operations:
            new_path = operation.old_path.parent / operation.new_name
            
            # Tronca nomi per visualizzazione
            old_display = self._truncate_filename(operation.old_path.name, 42)
            new_display = self._truncate_filename(operation.new_name, 42)
            
            if self.config.dry_run:
                print(f"{'📹 OK':<8} {old_display:<45} {new_display:<45}")
                success_count += 1
            else:
                try:
                    if new_path.exists():
                        status = "❌ EXISTS" if self.config.interface_language == Language.ENGLISH else "❌ ESISTE"
                        print(f"{status:<8} {old_display:<45} {new_display:<45}")
                        error_count += 1
                        continue
                    
                    # Aggiungi alla lista per il ripristino PRIMA della rinomina
                    restore_manager.add_rename(operation.old_path.name, operation.new_name)
                    
                    operation.old_path.rename(new_path)
                    print(f"{'✅ DONE':<8} {old_display:<45} {new_display:<45}")
                    success_count += 1
                    
                except Exception as e:
                    error_msg = str(e)[:12] + "..." if len(str(e)) > 15 else str(e)
                    print(f"{'❌ ERROR':<8} {old_display:<45} {error_msg:<45}")
                    error_count += 1
        
        print("=" * 100)
        print(self.text_manager.get('results', success_count, error_count))
        
        # Crea script di ripristino se ci sono state rinomine successful
        if not self.config.dry_run and restore_manager.renames:
            try:
                script_name = restore_manager.create_script()
                if script_name:
                    if self.config.interface_language == Language.ENGLISH:
                        print(f"\n📄 Restore script created: {script_name}")
                        print(f"💡 To restore original names, run: python {script_name}")
                    else:
                        print(f"\n📄 Script di ripristino creato: {script_name}")
                        print(f"💡 Per ripristinare i nomi originali, esegui: python {script_name}")
            except Exception as e:
                if self.config.interface_language == Language.ENGLISH:
                    print(f"\n❌ Error creating restore script: {e}")
                else:
                    print(f"\n❌ Errore nella creazione dello script di ripristino: {e}")
    
    @staticmethod
    def _truncate_filename(filename: str, max_length: int) -> str:
        """Tronca un nome file se troppo lungo"""
        return filename[:max_length-3] + "..." if len(filename) > max_length else filename

# ============================================================================
# FACTORY E BUILDER PATTERNS
# ============================================================================

class RenamerFactory:
    """Factory per creare istanze del rinominatore"""
    
    @staticmethod
    def create_renamer(config: Config) -> TVSeriesRenamer:
        """Crea un'istanza del rinominatore con la configurazione specificata"""
        return TVSeriesRenamer(config)

class ConfigBuilder:
    """Builder per costruire configurazioni complesse"""
    
    def __init__(self):
        self._config_dict = {}
    
    def with_tmdb_key(self, api_key: str) -> 'ConfigBuilder':
        self._config_dict['tmdb_api_key'] = api_key
        return self
    
    def with_language(self, language: Language) -> 'ConfigBuilder':
        self._config_dict['language'] = language
        return self
    
    def with_format(self, format_style: FormatStyle) -> 'ConfigBuilder':
        self._config_dict['format_style'] = format_style
        return self
    
    def with_dry_run(self, dry_run: bool) -> 'ConfigBuilder':
        self._config_dict['dry_run'] = dry_run
        return self
    
    def with_recursive(self, recursive: bool) -> 'ConfigBuilder':
        self._config_dict['recursive'] = recursive
        return self
    
    def build(self) -> Config:
        return Config(**self._config_dict)

# ============================================================================
# GESTORE SCRIPT DI RIPRISTINO
# ============================================================================

class RestoreScriptManager:
    """Gestore per la creazione di script di ripristino"""
    
    def __init__(self, directory: Path, text_manager: TextManager):
        self.directory = directory
        self.text_manager = text_manager
        self.renames: List[Tuple[str, str]] = []
    
    def add_rename(self, old_name: str, new_name: str):
        """Aggiunge una rinomina alla lista"""
        self.renames.append((old_name, new_name))
    
    def create_script(self) -> Optional[str]:
        """Crea lo script di ripristino"""
        if not self.renames:
            return None
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        script_name = f"restore_tv_names_{timestamp}.py"
        script_path = self.directory / script_name
        
        try:
            script_content = self._generate_script_content()
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Rendi eseguibile (Unix/Linux)
            try:
                os.chmod(script_path, 0o755)
            except (OSError, AttributeError):
                pass  # Ignora errori su Windows o se chmod non disponibile
            
            return script_name
        except Exception as e:
            print(f"❌ Errore creazione script: {e}")
            return None
    
    def _generate_script_content(self) -> str:
        """Genera il contenuto dello script di ripristino"""
        lines = [
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '"""',
            'TV Renamer - Script di Ripristino',
            f'Creato: {time.strftime("%Y-%m-%d %H:%M:%S")}',
            '"""',
            '',
            'import os',
            'from pathlib import Path',
            'import sys',
            '',
            'def main():',
            '    """Funzione principale dello script di ripristino"""',
            '    print("📺 TV Renamer - Script di Ripristino")',
            '    print("=" * 50)',
            '    print("ATTENZIONE: Questo script ripristinerà i nomi file originali!")',
            '    print()',
            '    ',
            '    script_dir = Path(__file__).parent.absolute()',
            '    ',
            '    # Lista delle rinomine da ripristinare (nuovo_nome, nome_originale)',
            '    renames = ['
        ]
        
        # Aggiungi le rinomine
        for old_name, new_name in self.renames:
            lines.append(f'        ({repr(new_name)}, {repr(old_name)}),')
        
        lines.extend([
            '    ]',
            '    ',
            '    print(f"📋 Trovati {len(renames)} file da ripristinare")',
            '    ',
            '    # Conferma utente',
            '    try:',
            '        confirm = input("Vuoi procedere con il ripristino? (s/N): ").strip().lower()',
            '        if confirm not in [\'s\', \'y\', \'si\', \'yes\']:',
            '            print("Operazione annullata.")',
            '            return',
            '    except KeyboardInterrupt:',
            '        print("\\nOperazione annullata.")',
            '        return',
            '    ',
            '    print("\\nElaborazione ripristini...")',
            '    print("-" * 50)',
            '    ',
            '    success = 0',
            '    errors = 0',
            '    ',
            '    for current_name, original_name in renames:',
            '        try:',
            '            current_path = script_dir / current_name',
            '            original_path = script_dir / original_name',
            '            ',
            '            if current_path.exists() and not original_path.exists():',
            '                current_path.rename(original_path)',
            '                print(f"✅ {original_name}")',
            '                success += 1',
            '            elif original_path.exists():',
            '                print(f"⚠️  {original_name} (già esistente, skip)")',
            '            else:',
            '                print(f"❌ {current_name} (file non trovato)")',
            '                errors += 1',
            '        except Exception as e:',
            '            print(f"❌ {original_name} (errore: {e})")',
            '            errors += 1',
            '    ',
            '    print("-" * 50)',
            '    print(f"📊 Ripristinati: {success}, Errori: {errors}")',
            '    ',
            '    if success > 0:',
            '        print("\\n✅ Ripristino completato!")',
            '        # Auto-elimina lo script dopo l\'uso',
            '        try:',
            '            Path(__file__).unlink()',
            '            print("🗑️  Script di ripristino eliminato automaticamente")',
            '        except Exception:',
            '            print("⚠️  Non è stato possibile eliminare lo script automaticamente")',
            '    ',
            '    input("\\nPremi INVIO per uscire...")',
            '',
            'if __name__ == "__main__":',
            '    try:',
            '        main()',
            '    except Exception as e:',
            '        print(f"❌ Errore critico: {e}")',
            '        import traceback',
            '        traceback.print_exc()',
            '        input("Premi INVIO per uscire...")',
            '        sys.exit(1)'
        ])
        
        return '\n'.join(lines)

# ============================================================================
# COMMAND PATTERN PER OPERAZIONI
# ============================================================================

class Command(ABC):
    """Interfaccia per il pattern Command"""
    
    @abstractmethod
    def execute(self) -> bool:
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        pass

class RenameCommand(Command):
    """Comando per rinominare un file"""
    
    def __init__(self, old_path: Path, new_path: Path):
        self.old_path = old_path
        self.new_path = new_path
        self._executed = False
    
    def execute(self) -> bool:
        """Esegue la rinomina"""
        try:
            if self.new_path.exists():
                return False
            self.old_path.rename(self.new_path)
            self._executed = True
            return True
        except Exception:
            return False
    
    def undo(self) -> bool:
        """Annulla la rinomina"""
        if not self._executed:
            return False
        try:
            self.new_path.rename(self.old_path)
            self._executed = False
            return True
        except Exception:
            return False

class CommandInvoker:
    """Invoker per gestire i comandi"""
    
    def __init__(self):
        self._history: List[Command] = []
    
    def execute_command(self, command: Command) -> bool:
        """Esegue un comando e lo aggiunge alla cronologia"""
        if command.execute():
            self._history.append(command)
            return True
        return False
    
    def undo_last(self) -> bool:
        """Annulla l'ultimo comando"""
        if self._history:
            command = self._history.pop()
            return command.undo()
        return False
    
    def undo_all(self) -> int:
        """Annulla tutti i comandi nella cronologia"""
        count = 0
        while self._history:
            if self.undo_last():
                count += 1
        return count

# ============================================================================
# EXCEPTION HANDLING MIGLIORATO
# ============================================================================

class TVRenamerException(Exception):
    """Eccezione base per il TV Renamer"""
    pass

class APIException(TVRenamerException):
    """Eccezione per errori API"""
    pass

class FileProcessingException(TVRenamerException):
    """Eccezione per errori di elaborazione file"""
    pass

class ConfigurationException(TVRenamerException):
    """Eccezione per errori di configurazione"""
    pass

# ============================================================================
# LOGGING MIGLIORATO
# ============================================================================

import logging
from typing import Union

class Logger:
    """Logger centralizzato per l'applicazione"""
    
    def __init__(self, name: str = "TVRenamer", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str, exc_info: bool = False):
        self.logger.error(message, exc_info=exc_info)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

# ============================================================================
# MAIN E PARSING ARGOMENTI
# ============================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """Crea il parser per gli argomenti della linea di comando"""
    parser = argparse.ArgumentParser(
        description="Universal TV Series Renamer v1.2 (Refactored) - by Andres Zanzani",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi di utilizzo:
  %(prog)s /path/to/series --execute
  %(prog)s /path/to/series --format plex --language en
  %(prog)s /path/to/series --recursive --tmdb-key YOUR_API_KEY
        """
    )
    
    parser.add_argument(
        'directory', 
        help='Directory contenente i file video'
    )
    
    parser.add_argument(
        '--execute', 
        action='store_true', 
        help='Esegui rinomine (default: solo preview)'
    )
    
    parser.add_argument(
        '--format', 
        choices=[style.value for style in FormatStyle],
        default=FormatStyle.STANDARD.value, 
        help='Formato nome file'
    )
    
    parser.add_argument(
        '--recursive', 
        action='store_true', 
        help='Cerca ricorsivamente'
    )
    
    parser.add_argument(
        '--language', 
        choices=[lang.value for lang in Language], 
        default=Language.ITALIAN.value, 
        help='Lingua episodi'
    )
    
    parser.add_argument(
        '--interface', 
        choices=[Language.ITALIAN.value, Language.ENGLISH.value], 
        default=Language.ITALIAN.value, 
        help='Lingua interfaccia'
    )
    
    parser.add_argument(
        '--tmdb-key', 
        help='API key TMDB'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='Universal TV Series Renamer v1.2 (Refactored)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Abilita output verboso'
    )
    
    return parser

def validate_directory(directory_path: str) -> Path:
    """Valida che il percorso della directory sia valido"""
    directory = Path(directory_path)
    if not directory.exists():
        raise ConfigurationException(f"Directory non trovata: {directory_path}")
    if not directory.is_dir():
        raise ConfigurationException(f"Il percorso non è una directory: {directory_path}")
    return directory

def main():
    """Funzione principale dell'applicazione"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Configura logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = Logger(level=log_level)
    
    try:
        # Valida directory
        directory = validate_directory(args.directory)
        
        # Crea configurazione
        config = Config.from_args(args)
        
        # Crea e esegui rinominatore
        renamer = RenamerFactory.create_renamer(config)
        renamer.process_directory(directory)
        
        logger.info("Elaborazione completata con successo")
        
    except ConfigurationException as e:
        logger.error(f"Errore di configurazione: {e}")
        sys.exit(1)
    except APIException as e:
        logger.error(f"Errore API: {e}")
        sys.exit(1)
    except FileProcessingException as e:
        logger.error(f"Errore elaborazione file: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operazione interrotta dall'utente")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Errore imprevisto: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
