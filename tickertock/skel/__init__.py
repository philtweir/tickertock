import shutil
import logging
import pathlib
from xdg import xdg_config_home
from jinja2 import Environment, select_autoescape, FileSystemLoader


def initialize(clockify_api_key, clockify_workspace_id):
    target = xdg_config_home() / "tickertock"
    target.mkdir(exist_ok=True)
    here = pathlib.Path(__file__).parent
    (target / "assets").mkdir(exist_ok=True)

    env = Environment(loader=FileSystemLoader(here), autoescape=select_autoescape())

    template = env.get_template("config.toml.j2")
    with open(target / "config.toml", "w") as f:
        f.write(
            template.render(
                api_key=clockify_api_key,
                workspace_id=clockify_workspace_id,
            )
        )

    shutil.copyfile(here / "streamdeck_ui.json.j2", target / "streamdeck_ui.json.j2")
    shutil.copyfile(here / "projects.toml", target / "projects.toml")

    for asset in (here / "assets").iterdir():
        shutil.copyfile(asset, target / "assets" / asset.name)

    logging.info("Initialized")
