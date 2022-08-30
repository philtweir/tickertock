from xdg import xdg_config_home

CONFIG_DIR = xdg_config_home() / "tickertock"
STREAMDECK_IMAGE_DIR = CONFIG_DIR / "assets"
DECK_BUTTON_SIZE = 128
