"""
Management (deviant manipulation) of streamdeck_ui.

Credit to streamdeck_ui for several snippets below. We don't
want to break your code, so thank you for exposing hooks where
you have (e.g. handle_keypress) and sorry for inserting them
where we shouldn't (e.g. create_tray).
"""

import filetype
import datetime
from functools import partial
from streamdeck_ui import gui, api, display
from pynput.keyboard import Controller
from PySide2.QtWidgets import QApplication
from streamdeck_ui.config import LOGO
from PySide2.QtGui import QIcon, QPixmap, QImage
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QSystemTrayIcon
from StreamDeck.Devices import StreamDeck

from .utils import draw_time

# Ew.
filetype_guess = filetype.guess


def _filetype_guess(*args, **kwargs):
    try:
        return filetype_guess(*args, **kwargs)
    except TypeError:
        return True


display.image_filter.filetype.guess = _filetype_guess


class TickertockStreamDeckServer(api.StreamDeckServer):
    """
    Hacky way to ensure we can inject non-string values and
    prevent overwriting of users' own StreamDeck configuration.
    """

    def __init__(self, tickertock) -> None:
        super().__init__()
        self.tickertock = tickertock

    def export_config(self, output_file: str) -> None:
        pass  # we don't actually want to export this config

    def open_config(self, config_file: str):
        # Make sure we have a working config file first
        super().open_config(config_file)

        # from api.py
        config = self.tickertock.merge_streamdeck_config(
            {"streamdeck_ui_version": api.CONFIG_FILE_VERSION, "state": self.state},
            with_images=True,
        )
        self.state = {}
        for deck_id, deck in config["state"].items():
            deck["buttons"] = {
                int(page_id): {
                    int(button_id): button for button_id, button in buttons.items()
                }
                for page_id, buttons in deck.get("buttons", {}).items()
            }
            self.state[deck_id] = deck


class TickertockApplication:
    """
    Singleton to look after the Qt application and all who
    sail in her.
    """

    def handle_update_time(self):
        """
        Periodically make sure everything is synced, including
        clock on the bottom-right button.
        """

        entry = self.tickertock.tocker.get_active_time_entry()
        for deck_id, _ in self.api.state.items():
            deck = self.api.decks.get(deck_id, None)
            if deck:
                page = self.api.get_page(deck_id)
                layout = self.api.get_deck(deck_id)["layout"]
                key_count = layout[0] * layout[1]
                text = self.api.get_button_text(
                    deck_id, page if page != 1 else 0, key_count - 1
                )

                project, elapsed = self.tickertock.tocker.elapsed()
                if project:
                    if text != f"@{project}":
                        self.api.set_page(deck_id, 0)
                        self.api.set_button_text(
                            deck_id, 0, key_count - 1, f"@{project}"
                        )
                    image = draw_time(elapsed.total_seconds())
                    self.api.set_button_icon(deck_id, 0, key_count - 1, image)

    def handle_keypress_additional(self, deck_id: str, key: int, state: bool) -> None:
        """
        Confuse anyone who is looking at handle_keypress in streamdeck_ui in the naive
        hope that that's where the logic is.
        """

        if not state:
            return

        keyboard = Controller()
        page = self.api.get_page(deck_id)
        layout = self.api.get_deck(deck_id)["layout"]
        key_count = layout[0] * layout[1]
        text = self.api.get_button_text(deck_id, page if page != 1 else 0, key)
        if text and key != key_count - 1:
            self.tickertock.toggle(text)
            project = self.tickertock.projects[text]
            self.api.set_button_text(deck_id, 0, key_count - 1, f"@{text}")
            image = project.get("image", LOGO)
            if isinstance(image, str):
                logo = QIcon(image)
            else:
                qimage = QImage()
                qimage.loadFromData(image.getvalue(), "PNG")
                qpixmap = QPixmap.fromImage(qimage)
                logo = QIcon(qpixmap)
        else:
            self.tickertock.toggle("None")
            self.api.set_button_text(deck_id, 0, key_count - 1, "NOT RUN")
            logo = QIcon(LOGO)
        self.tray.setIcon(logo)

        page_count = round(len(self.tickertock.entries) / (key_count - 1) + 0.4999) + 1
        # We do not know the original page
        # switch_page = api.get_button_switch_page(deck_id, page, key)
        if key != key_count - 1:
            self.api.set_page(deck_id, 0)
            self.tickertock.tocker.when = datetime.datetime.utcnow()
            self.handle_update_time()
        elif text.startswith("@"):
            self.api.set_page(deck_id, 1)
        elif page > 0:
            self.api.set_page(deck_id, page % (page_count - 1) + 1)
        else:
            self.api.set_page(deck_id, min(page_count - 1, 2))

    def __init__(self, tickertock):
        self.tickertock = tickertock
        # Ew. We want the tray, so we take the tray.
        # Carpe trayem.
        self._sd_create_tray = gui.create_tray
        gui.create_tray = self.create_tray

    def create_tray(self, *args, **kwargs):
        self.tray = self._sd_create_tray(*args, **kwargs)
        return self.tray

    def _load_streamdeck_config(self):
        # from api.py
        # Credit to streamdeck_ui folks for this snippet.
        self.api.state = {}
        for deck_id, deck in self.tickertock.streamdeck_config["state"].items():
            deck["buttons"] = {
                int(page_id): {
                    int(button_id): button for button_id, button in buttons.items()
                }
                for page_id, buttons in deck.get("buttons", {}).items()
            }
            self.api.state[deck_id] = deck

    def run(self):
        gui.StreamDeckServer = partial(TickertockStreamDeckServer, self.tickertock)

        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_update_time)

        # from gui.py
        # Credit to streamdeck_ui folks for this snippet.
        code = gui.start(_exit=True)
        self.api = gui.api
        self.handle_update_time()

        app = QApplication.instance()

        self.api.streamdeck_keys.key_pressed.connect(self.handle_keypress_additional)
        self.timer.start(self.tickertock.config["syncRate"])
        app.exec_()

        self.api.stop()
        return code


def merge_streamdeck_config(tickertock, streamdeck_input, with_images=False):
    env = Environment(
        loader=FileSystemLoader(CONFIG_DIR), autoescape=select_autoescape()
    )
    template = env.get_template("streamdeck_ui.json.j2")
    for device, deck in streamdeck_input["state"].items():
        buttons = len(list(deck["buttons"].values())[0]) - 1
        items = tickertock.entries
        pages = [
            {
                "entries": {
                    code: tickertock.projects[code] for code in items[i : i + buttons]
                }
            }
            for i in range(0, len(items), buttons)
        ]
        inset_json = template.render(
            len=len,
            enumerate=enumerate,
            isinstance=isinstance,
            streamdeck_image_dir=STREAMDECK_IMAGE_DIR,
            str=str,
            list=list,
            pages=pages,
            buttons=buttons + 1,
        )
        inset = json.loads(inset_json)

        if with_images:
            for page in inset["buttons"].values():
                for entry in page.values():
                    if "text" in entry:
                        project = tickertock.projects.get(entry["text"], {})
                        if "image" in project:
                            entry["icon"] = project["image"]
        streamdeck_input["state"][device] = inset

    return streamdeck_input
