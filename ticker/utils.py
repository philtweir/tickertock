import cairo
from io import BytesIO
import math

from .config import DECK_BUTTON_SIZE


class ClockButtonBuffer(BytesIO):
    """
    Extension for BytesIO so that hashing is unique
    for a given draw_time image. Avoids clashes in
    streamdeck_ui display pipeline caching.
    """

    current_time = (0, 0)

    def set_current_time(self, hours, mins):
        self.current_time = (hours, mins)

    def __hash__(self):
        return hash(self.current_time)


def draw_time(time_secs):
    """
    Draws a clockface representing minutes overlaid
    with a number representing hours.
    """

    image_buffer = ClockButtonBuffer()
    surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, DECK_BUTTON_SIZE, DECK_BUTTON_SIZE
    )
    cr = cairo.Context(surface)
    cr.set_source_rgba(1, 1, 1)
    cr.move_to(DECK_BUTTON_SIZE / 2, DECK_BUTTON_SIZE / 2)
    arc = 2 * math.pi * (time_secs // 60 % 60) / 60
    hours = int(time_secs // 3600)
    cr.arc(
        DECK_BUTTON_SIZE / 2,
        DECK_BUTTON_SIZE / 2,
        DECK_BUTTON_SIZE / 3,
        -math.pi / 2,
        -math.pi / 2 + arc,
    )
    cr.close_path()
    cr.fill()

    if hours > 0:
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

        cr.set_font_size(50.0)
        xb, yb, w, h, dx, dy = cr.text_extents(str(hours))
        x = DECK_BUTTON_SIZE / 2 - (w / 2 + xb)
        y = DECK_BUTTON_SIZE / 2 - (h / 2 + yb)

        cr.move_to(x, y)
        cr.set_source_rgba(0.5, 0.5, 0.5)
        cr.show_text(str(hours))

    image_buffer.seek(0)
    surface.write_to_png(image_buffer)
    image_buffer.set_current_time(hours, time_secs // 60 % 60)
    return image_buffer


def draw_colour(code, colour):
    surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, DECK_BUTTON_SIZE, DECK_BUTTON_SIZE
    )
    cr = cairo.Context(surface)
    rgba = [x / 255 for x in PIL.ImageColor.getcolor("#" + colour, "RGB")] + [1]
    cr.set_source_rgba(*rgba)
    cr.rectangle(0, 0, DECK_BUTTON_SIZE, DECK_BUTTON_SIZE)
    cr.fill()

    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    cr.set_font_size(80.0)
    xb, yb, w, h, dx, dy = cr.text_extents(code[0])
    x = DECK_BUTTON_SIZE / 2 - (w / 2 + xb)
    y = 0.9 * DECK_BUTTON_SIZE / 2 - (h / 2 + yb)

    cr.move_to(x, y)
    if min(rgba[:2]) > 0.5:
        cr.set_source_rgba(0, 0, 0)
    else:
        cr.set_source_rgba(1, 1, 1)
    cr.show_text(code[0])

    image_file = BytesIO()
    surface.write_to_png(image_file)
    return image_file
