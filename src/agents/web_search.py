"""
Агент поиска в интернете для Методист-Агента.

Поддерживает поиск через DuckDuckGo и SerpAPI (Google),
загрузку и парсинг веб-страниц, скачивание файлов.
Реализовано кэширование результатов поиска для экономии запросов.

Windows-first, русский язык, graceful degradation.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from core.config import Config, get_data_dir


class SearchCache:
    """Простой файловый кэш для результатов поиска с TTL."""

    def __init__(self, cache_dir: Path, ttl_seconds: int = 3600):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, query: str, engine: str, max_results: int) -> str:
        raw = f"{engine}:{max_results}:{query}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest() + ".json"

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / key

    def get(self, query: str, engine: str, max_results: int) -> Optional[List[Dict[str, Any]]]:
        key = self._cache_key(query, engine, max_results)
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            mtime = path.stat().st_mtime
            if time.time() - mtime > self.ttl_seconds:
                path.unlink(missing_ok=True)
                return None
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def set(self, query: str, engine: str, max_results: int, results: List[Dict[str, Any]]) -> None:
        key = self._cache_key(query, engine, max_results)
        path = self._cache_path(key)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def clear(self) -> None:
        for f in self.cache_dir.glob("*.json"):
            f.unlink(missing_ok=True)


class WebSearchAgent:
    """Агент для поиска материалов в интернете и работы с веб-страницами."""

    # Таймауты для HTTP-запросов
    REQUEST_TIMEOUT = 30

    def __init__(self, config: Config):
        self.config = config
        self.cache = SearchCache(
            cache_dir=get_data_dir(config) / "search_cache",
            ttl_seconds=3600,
        )

    # ------------------------------------------------------------------
    # Диспетчер
    # ------------------------------------------------------------------
    def execute(self, task_type: Any, params: Dict[str, Any]) -> Any:
        """Диспетчер задач агента."""
        task_str = str(task_type).lower()

        if "search" in task_str or "find" in task_str or "найти" in task_str:
            query = params.get("query") or params.get("user_input", "")
            max_results = params.get("max_results", self.config.search.max_results)
            return self.search(query, max_results)

        if "fetch" in task_str or "загрузить" in task_str or "прочитать" in task_str:
            url = params.get("url", "")
            return self.fetch_url(url)

        if "download" in task_str or "скачать" in task_str:
            url = params.get("url", "")
            output = params.get("output_path", "")
            return self.download_file(url, output)

        if "parse" in task_str or "парсинг" in task_str:
            html = params.get("html", "")
            return self.parse_page(html)

        # По умолчанию — поиск по user_input
        query = params.get("query") or params.get("user_input", "")
        if query:
            return self.search(query)
        return {"error": "Неизвестный тип задачи или отсутствуют параметры"}

    # ------------------------------------------------------------------
    # Поиск
    # ------------------------------------------------------------------
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Универсальный поиск. Выбирает движок по конфигурации."""
        if not query or not query.strip():
            return []

        engine = self.config.search.engine.lower()
        max_results = min(max(1, max_results), 50)

        # Проверяем кэш
        cached = self.cache.get(query, engine, max_results)
        if cached is not None:
            return cached

        results: List[Dict[str, Any]] = []

        if engine == "serpapi":
            results = self.search_serpapi(query, max_results)
        elif engine == "google":
            results = self.search_duckduckgo(query, max_results)
        else:
            # По умолчанию DuckDuckGo — не требует API-ключа
            results = self.search_duckduckgo(query, max_results)

        # Сохраняем в кэш
        if results:
            self.cache.set(query, engine, max_results, results)

        return results

    def search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Поиск через DuckDuckGo. Не требует API-ключа."""
        results: List[Dict[str, Any]] = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                        "source": "duckduckgo",
                    })
        except Exception as e:
            # Graceful degradation: логируем, но не падаем
            results.append({
                "title": "Ошибка поиска DuckDuckGo",
                "url": "",
                "snippet": str(e),
                "source": "error",
            })
        return results

    def search_serpapi(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Поиск через SerpAPI (Google). Требует API-ключа."""
        results: List[Dict[str, Any]] = []
        api_key = self.config.search.serpapi_key

        if not api_key:
            # Fallback на DuckDuckGo
            return self.search_duckduckgo(query, max_results)

        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": api_key,
                "engine": "google",
                "num": max_results,
                "hl": "ru",
            }
            response = requests.get(url, params=params, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            organic = data.get("organic_results", [])
            for item in organic[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "serpapi",
                })
        except Exception as e:
            # Fallback на DuckDuckGo
            return self.search_duckduckgo(query, max_results)

        return results

    # ------------------------------------------------------------------
    # Работа со страницами
    # ------------------------------------------------------------------
    def fetch_url(self, url: str) -> Dict[str, Any]:
        """Загрузка HTML-страницы по URL."""
        if not url or not url.strip():
            return {"error": "URL не указан"}

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            }
            response = requests.get(url, headers=headers, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()

            # Определяем кодировку
            if response.encoding is None:
                response.encoding = "utf-8"

            return {
                "url": url,
                "status_code": response.status_code,
                "html": response.text,
                "encoding": response.encoding,
            }
        except requests.exceptions.Timeout:
            return {"error": f"Таймаут при загрузке {url}"}
        except requests.exceptions.ConnectionError:
            return {"error": f"Ошибка соединения с {url}"}
        except Exception as e:
            return {"error": f"Ошибка загрузки страницы: {e}"}

    def download_file(self, url: str, output_path: str) -> Dict[str, Any]:
        """Скачивание файла по URL с сохранением на диск."""
        if not url or not url.strip():
            return {"error": "URL не указан"}

        # Если путь не указан — сохраняем во временную директорию
        if not output_path:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path) or "downloaded_file"
            output_path = str(Path.home() / "Downloads" / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            }
            with requests.get(url, headers=headers, stream=True, timeout=self.REQUEST_TIMEOUT) as r:
                r.raise_for_status()
                with open(output_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            return {
                "url": url,
                "output_path": str(output_path),
                "size_bytes": output_path.stat().st_size,
                "success": True,
            }
        except Exception as e:
            return {"error": f"Ошибка скачивания файла: {e}", "url": url}

    def parse_page(self, html: str) -> Dict[str, Any]:
        """Парсинг HTML через BeautifulSoup."""
        if not html or not html.strip():
            return {"error": "HTML пустой"}

        try:
            soup = BeautifulSoup(html, "lxml")

            # Удаляем скрипты и стили для чистого текста
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            title = soup.title.get_text(strip=True) if soup.title else ""

            # Основной текст
            text = soup.get_text(separator="\n", strip=True)
            # Убираем лишние пустые строки
            lines = [line for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)

            # Ссылки
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                link_text = a.get_text(strip=True)
                if href.startswith("http"):
                    links.append({"url": href, "text": link_text})

            # Изображения
            images = []
            for img in soup.find_all("img"):
                src = img.get("src", "")
                alt = img.get("alt", "")
                if src:
                    images.append({"src": src, "alt": alt})

            return {
                "title": title,
                "text": clean_text[:10000],  # ограничиваем объём
                "links": links[:50],
                "images": images[:20],
                "success": True,
            }
        except Exception as e:
            return {"error": f"Ошибка парсинга HTML: {e}"}
