"""Search and last-known-good storage. One shared instance per server process."""
import json
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

FRESH_SECONDS = 3600
COOLDOWN_SECONDS = 600


class SearchService:
    def __init__(self, path, search=None, clock=time.time, pause=time.sleep):
        self.path = Path(path)
        self.search = search or self._search
        self.clock, self.pause = clock, pause
        self.lock = threading.Lock()
        self.state = {"results": [], "last_attempt": 0, "last_success": 0,
                      "issues": [], "complete": False}
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(saved, dict) and isinstance(saved.get("results"), list):
                self.state.update(saved)
        except (OSError, ValueError):
            pass

    @staticmethod
    def _search(query):
        from ddgs import DDGS
        return list(DDGS(timeout=10).text(query, region="in-en", max_results=8,
                                         backend="auto"))

    def snapshot(self):
        with self.lock:
            return json.loads(json.dumps(self.state))

    def refresh(self, force=False):
        if not self.lock.acquire(blocking=False):
            return "A refresh is already running. Your saved listings remain available."
        try:
            now = self.clock()
            if self.state["last_attempt"] and now - self.state["last_attempt"] < COOLDOWN_SECONDS:
                return "Using saved listings. Live searches are limited to once every 10 minutes."
            if (not force and self.state["complete"] and self.state["last_success"]
                    and now - self.state["last_success"] < FRESH_SECONDS):
                return "Using the saved search from the last hour."
            self.state["last_attempt"] = now
            year = datetime.fromtimestamp(now).year
            queries = [
                f"dental workshop Manipal {year} {year + 1}",
                f"dental conference Udupi {year} {year + 1}",
                "endodontics hands-on course Manipal MCODS",
                "dental implant course Udupi Manipal",
                "MCODS Manipal continuing dental education CDE workshop",
            ]
            found, issues = {}, []
            for index, query in enumerate(queries):
                if index:
                    self.pause(1)
                try:
                    rows = list(self.search(query))
                    if not rows:
                        issues.append(f"No response listings: {query}")
                    for row in rows:
                        title, desc = str(row.get("title", "")), str(row.get("body", ""))
                        link = str(row.get("href", ""))
                        parsed = urlsplit(link)
                        if parsed.scheme not in ("http", "https") or not parsed.netloc:
                            continue
                        content = (title + " " + desc + " " + link).lower()
                        if not any(k in content for k in ("manipal", "udupi")):
                            continue
                        if not any(k in content for k in ("dental", "dentist", "endodont", "implant", "mcods", "root canal")):
                            continue
                        link = urlunsplit(parsed._replace(fragment=""))
                        found[link] = {"title": title or link, "link": link, "desc": desc,
                                       "last_seen": now}
                except Exception as exc:
                    logging.exception("Search failed: %s", query)
                    issues.append(f"{query}: {type(exc).__name__}")
            self.state["issues"] = issues
            self.state["complete"] = bool(found) and not issues
            if found:
                # Retain older listings, with individual last-seen timestamps.
                older = {r["link"]: r for r in self.state["results"]}
                older.update(found)
                self.state["results"] = sorted(older.values(), key=lambda r: r["last_seen"], reverse=True)[:250]
                self.state["last_success"] = now
                message = f"Found {len(found)} matching pages in this refresh."
                if issues:
                    message += " Some searches were incomplete; older listings were retained."
            else:
                message = "The search returned no matching pages or was unavailable. Previous listings were retained."
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                temporary = self.path.with_suffix(".tmp")
                temporary.write_text(json.dumps(self.state, ensure_ascii=False), encoding="utf-8")
                os.replace(temporary, self.path)
            except OSError:
                logging.exception("Cannot save listings")
                message += " Disk saving failed; results are available in server memory only."
            return message
        finally:
            self.lock.release()
