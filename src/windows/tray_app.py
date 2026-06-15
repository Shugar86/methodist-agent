"""
TrayApp — System Tray интеграция для Methodist Agent (Windows).

Использует pystray для иконки в системном трее и tkinter для диалогов.
"""

import os
import threading
import logging
from typing import Optional, Callable

from core.config import Config, get_output_dir, get_default_config_path
from core.ui_text import (
    error_generic,
    info_no_search_results,
    progress_creating_document,
    progress_searching,
    success_document_created,
    success_search_results,
)

logger = logging.getLogger(__name__)

# Windows-specific imports
try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    _HAS_PYSTRAY = True
except ImportError:
    _HAS_PYSTRAY = False
    logger.warning("pystray / PIL не установлены — System Tray недоступен")

try:
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    _HAS_TKINTER = True
except ImportError:
    _HAS_TKINTER = False
    logger.warning("tkinter не доступен — диалоги будут ограничены")


class TrayAppError(Exception):
    """Ошибка System Tray приложения."""
    pass


class TrayApp:
    """Приложение в системном трее Windows для Methodist Agent."""

    def __init__(self, config: Config):
        self.config = config
        self.output_dir = get_output_dir(config)
        self.icon: Optional[pystray.Icon] = None
        self._stop_event = threading.Event()
        self._workspace = None

        if not _HAS_PYSTRAY:
            raise TrayAppError("Для работы System Tray необходимо установить pystray и PIL: "
                               "pip install pystray pillow")

    # ------------------------------------------------------------------
    # Icon generation
    # ------------------------------------------------------------------

    def _create_icon_image(self) -> Image.Image:
        """Создать иконку программно: цветной круг с буквой 'М'."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Цвета
        bg_color = (59, 130, 246)      # синий (#3B82F6)
        text_color = (255, 255, 255)   # белый

        # Круг с небольшим отступом
        margin = 2
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=bg_color,
            outline=(37, 99, 235),
            width=2
        )

        # Буква "М" по центру
        text = "М"
        # Пытаемся использовать системный шрифт, иначе дефолтный
        font_size = 32
        try:
            # Windows системные шрифты
            font_paths = [
                "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/tahoma.ttf",
            ]
            font = None
            for fp in font_paths:
                if os.path.exists(fp):
                    font = ImageFont.truetype(fp, font_size)
                    break
            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # Вычисляем позицию текста для центрирования
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 2  # чуть выше центра

        draw.text((x, y), text, fill=text_color, font=font)
        return img

    # ------------------------------------------------------------------
    # Menu actions
    # ------------------------------------------------------------------

    def _on_create_document(self, template_type: str) -> Callable:
        """Вернуть callback для создания документа указанного типа."""
        def handler(icon, item):
            logger.info(f"Запрос создания документа: {template_type}")
            self._run_in_thread(self._create_document_dialog, template_type)
        return handler

    def _create_document_dialog(self, template_type: str) -> None:
        """Диалог создания документа (выполняется в отдельном потоке)."""
        if not _HAS_TKINTER:
            self._show_notification("Ошибка", "tkinter не доступен для диалогов")
            return

        root = tk.Tk()
        root.withdraw()  # скрыть главное окно
        root.attributes("-topmost", True)

        subject = simpledialog.askstring(
            "Создание документа",
            f"Введите название предмета для {template_type}:",
            parent=root
        )
        root.destroy()

        if not subject:
            return

        try:
            # Импортируем здесь, чтобы избежать циклических зависимостей
            from agents.document_specialist import DocumentSpecialist
            agent = DocumentSpecialist(self.config)
            self._show_notification(
                "📝 Создание документа",
                progress_creating_document(template_type),
            )
            result = agent.create_from_template({
                "template_name": template_type,
                "subject": subject,
            })
            if result.get("success"):
                self._show_notification(
                    "✅ Готово",
                    success_document_created(result["path"]),
                )
            else:
                self._show_notification(
                    "❌ Ошибка",
                    error_generic("создать документ", result.get("error", "")),
                )
        except Exception as e:
            logger.exception("Ошибка создания документа")
            self._show_notification(
                "❌ Ошибка",
                error_generic("создать документ", str(e)),
            )

    def _on_search(self, icon, item) -> None:
        """Открыть диалог поиска."""
        logger.info("Запрос поиска")
        self._run_in_thread(self._search_dialog)

    def _search_dialog(self) -> None:
        """Диалог поиска методических материалов."""
        if not _HAS_TKINTER:
            self._show_notification("Ошибка", "tkinter не доступен для диалогов")
            return

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        query = simpledialog.askstring(
            "🔍 Поиск методических материалов",
            "Введите поисковый запрос:",
            parent=root
        )
        root.destroy()

        if not query:
            return

        try:
            from agents.web_search import WebSearchAgent
            agent = WebSearchAgent(self.config)
            self._show_notification("🔍 Поиск", progress_searching(query))
            results = agent.search(query, max_results=10)

            if not results:
                self._show_notification("Результат", info_no_search_results())
                return

            # Формируем краткое сообщение
            lines = [f"{i+1}. {r.get('title', 'Без названия')[:40]}"
                     for i, r in enumerate(results[:5])]
            msg = "\n".join(lines)
            self._show_notification(success_search_results(len(results)), msg)
        except Exception as e:
            logger.exception("Ошибка поиска")
            self._show_notification(
                "❌ Ошибка поиска",
                error_generic("выполнить поиск", str(e)),
            )

    def _on_open_folder(self, icon, item) -> None:
        """Открыть папку с выходными файлами."""
        logger.info(f"Открытие папки: {self.output_dir}")
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            os.startfile(str(self.output_dir))
        except Exception as e:
            logger.exception("Не удалось открыть папку")
            self._show_notification(
                "❌ Ошибка",
                error_generic("открыть папку", str(e)),
            )

    def _on_settings(self, icon, item) -> None:
        """Открыть файл конфигурации."""
        config_path = get_default_config_path()
        logger.info(f"Открытие настроек: {config_path}")
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            if not config_path.exists():
                from core.config import save_config, Config
                save_config(Config(), str(config_path))
            os.startfile(str(config_path))
        except Exception as e:
            logger.exception("Не удалось открыть настройки")
            self._show_notification(
                "❌ Ошибка",
                error_generic("открыть настройки", str(e)),
            )

    def _on_open_workspace(self, icon, item) -> None:
        """Открыть основное рабочее пространство Methodist Agent."""
        if not _HAS_TKINTER:
            self._show_notification("Ошибка", "tkinter не доступен для рабочего пространства")
            return

        if self._workspace is None:
            from windows.workspace import MethodistWorkspace
            self._workspace = MethodistWorkspace(config=self.config)

        self._workspace.show()

    def _on_exit(self, icon, item) -> None:
        """Завершить приложение."""
        logger.info("Завершение работы TrayApp")
        self._stop_event.set()
        if self.icon:
            self.icon.stop()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _run_in_thread(self, target: Callable, *args) -> None:
        """Запустить функцию в отдельном потоке."""
        t = threading.Thread(target=target, args=args, daemon=True)
        t.start()

    def _show_notification(self, title: str, message: str) -> None:
        """Показать уведомление через pystray или tkinter."""
        try:
            if self.icon:
                self.icon.notify(message, title)
            elif _HAS_TKINTER:
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo(title, message, parent=root)
                root.destroy()
        except Exception as e:
            logger.warning(f"Не удалось показать уведомление: {e}")

    # ------------------------------------------------------------------
    # Menu construction
    # ------------------------------------------------------------------

    def _build_menu(self) -> pystray.Menu:
        """Построить меню трея."""
        return pystray.Menu(
            pystray.MenuItem(
                "📝 Создать документ",
                pystray.Menu(
                    pystray.MenuItem(
                        "Рабочая программа",
                        self._on_create_document("curriculum")
                    ),
                    pystray.MenuItem(
                        "Ведомость",
                        self._on_create_document("schedule")
                    ),
                    pystray.MenuItem(
                        "Презентация",
                        self._on_create_document("presentation")
                    ),
                    pystray.MenuItem(
                        "Отчёт",
                        self._on_create_document("report")
                    ),
                )
            ),
            pystray.MenuItem("🔍 Поиск", self._on_search),
            pystray.MenuItem("📂 Открыть папку", self._on_open_folder),
            pystray.MenuItem("⚙️ Настройки", self._on_settings),
            pystray.MenuItem("🖥️ Открыть рабочее пространство", self._on_open_workspace),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Выход", self._on_exit),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Запустить приложение в системном трее (блокирующий вызов)."""
        logger.info("Запуск TrayApp...")

        icon_image = self._create_icon_image()
        menu = self._build_menu()

        self.icon = pystray.Icon(
            "methodist-agent",
            icon_image,
            "Методист-Агент",
            menu
        )

        # Уведомление при старте
        self.icon.visible = True

        logger.info("TrayApp запущен. Иконка в системном трее.")
        self.icon.run()

    def run_detached(self) -> threading.Thread:
        """Запустить трей в фоновом потоке и вернуть объект потока."""
        t = threading.Thread(target=self.run, daemon=True, name="TrayAppThread")
        t.start()
        return t

    def stop(self) -> None:
        """Остановить приложение трея."""
        self._on_exit(None, None)
