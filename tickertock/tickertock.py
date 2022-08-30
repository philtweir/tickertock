import PIL
import toml
import os
import logging
import json
from jinja2 import Environment, select_autoescape, FileSystemLoader
import cairo
from . import clockify, ui
from .config import CONFIG_DIR, STREAMDECK_IMAGE_DIR, DECK_BUTTON_SIZE
from .utils import draw_colour

TOCKERS = {"clockify": clockify.ClockifyTocker}


class Tickertock:
    """
    Governor class to manage the other bits and pieces, linking
    the "tocker", or timetracking app wrapper, with all the generic
    behaviour of tickertock application.
    """

    def __init__(self, tocker_type):
        self._projects = None
        self.load_config()
        self.tocker = TOCKERS[tocker_type].from_config(self.config[tocker_type])

    def initialize(self):
        self.load_images()
        self.tocker.initialize()

    def load_images(self):
        for code, project in self.projects.items():
            image_path = os.path.join(STREAMDECK_IMAGE_DIR, f"{code.lower()}.png")
            if os.path.exists(image_path):
                project["image"] = image_path
            elif "colour" in project:
                project["image"] = draw_colour(code, project["colour"])

    @property
    def projects(self):
        if self._projects is None:
            self.load_projects()
        return self._projects

    def toggle(self, project):
        if project in self.projects:
            pid = self.tocker.get_project_id(self.projects[project]["name"])
            try:
                result = self.tocker.start_time_entry("(to fill in)", pid)
            except Exception as e:
                print(e)
                logging.error("could not toggl")
                success = False
            else:
                logging.info(f"Toggled {project}")
                success = project
        elif project == "None":
            current_timer = self.tocker.stop_time_entry()
            logging.info("Toggl off")
            success = True
        else:
            logging.error("Unknown project")
            success = False

        return success

    def load_config(self):
        if not CONFIG_DIR.exists():
            raise RuntimeError("Must initialize with Clockify API key [tickertock init]")

        with open(CONFIG_DIR / "config.toml", "r") as f:
            config = toml.load(f)

        self.config = config

        with open(CONFIG_DIR / "projects.toml", "r") as f:
            project_config = toml.load(f)
        self._projects = {
            key: {"name": project} if isinstance(project, str) else project
            for key, project in project_config["projects"].items()
        }
        self.entries = project_config["page"]["entries"]
