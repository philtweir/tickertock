#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import json
import datetime
import logging
import sys
import os
import toml
import click
import time
from xdg import xdg_cache_home

from tickertock.config import CONFIG_DIR
from tickertock import __version__
from tickertock.ui import TickertockApplication, merge_streamdeck_config, TickertockStreamDeckServer
from tickertock.skel import initialize as skel_initialize
from tickertock.tickertock import Tickertock

logging.basicConfig(filename=xdg_cache_home() / "settoggl.log", level=logging.INFO)

_BEAR_COMMANDS = ("init", "version")


@click.group()
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand not in _BEAR_COMMANDS:
        ctx.obj = Tickertock("clockify")
        ctx.obj.initialize()


@cli.command()
@click.argument("project")
@click.pass_obj
def toggle(obj, project):
    logging.info(project)

    success = obj.toggle(project)

    return success


@cli.command()
@click.argument("deckfile", required=False)
@click.pass_obj
def writeout(obj, deckfile):
    application = TickertockApplication(obj)
    if deckfile:
        shutil.copyfile(deckfile, f'{deckfile}.{datetime.datetime.now().strftime("%s")}.bak')
        with open(deckfile, "r") as f:
            streamdeck_input = json.load(f)
    else:
        streamdeck_input = {
                "state": {}
        }

    server = TickertockStreamDeckServer(obj)
    server.start()
    print("Waiting for decks to attach (3s)")
    time.sleep(3)
    print("Found:")
    for deck in server.decks:
        print("  ", deck)
        if deck not in streamdeck_input["state"]:
            streamdeck_input["state"][deck] = {}
    streamdeck_input = merge_streamdeck_config(
        obj,
        streamdeck_input,
        get_deck=server.get_deck,
        with_images=False,
    )

    HOME = os.environ.get("HOME")
    with open(os.path.join(HOME, ".streamdeck_ui.json"), "w") as f:
        json.dump(streamdeck_input, f)
    logging.info("Streamdeck UI configuration written")
    server.stop()


@cli.command()
@click.pass_obj
def version(obj):
    print("Tickertock version:", __version__)
    print("https://xkcd.com/479/")


@cli.command()
@click.pass_obj
def ui(obj):
    sys.argv = ["streamdeck", "-n"] + sys.argv[3:]
    application = TickertockApplication(obj)
    code = application.run()
    return code


@cli.command()
@click.option("--clockify-api-key", required=True)
@click.option("--clockify-workspace-id", required=True)
def init(clockify_api_key, clockify_workspace_id):
    skel_initialize(
        clockify_api_key=clockify_api_key, clockify_workspace_id=clockify_workspace_id
    )

    tickertock = Tickertock("clockify")
    tickertock.initialize()
    projects = tickertock.tocker.get_all_projects()
    projects = [
        p
        for p in projects
        if (
            p.get("memberships", False)
            and p["memberships"][0].get("membershipStatus", False) == "ACTIVE"
        )
        and not p.get("archived", True)
    ]
    print("Loaded for", len(projects), "projects")
    project_toml = {
        "projects": {
            p["name"]: {"name": p["name"], "colour": p["color"].replace("#", "")}
            for p in projects
        },
        "page": {"entries": [p["name"] for p in projects]},
    }
    with open(CONFIG_DIR / "projects.toml", "w") as f:
        toml.dump(project_toml, f)
        logging.info(
            f"Projects list written out to {CONFIG_DIR / 'project.toml'} - look here to start building!"
        )


if __name__ == "__main__":
    cli()
