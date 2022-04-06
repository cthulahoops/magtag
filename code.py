import time
import board
import terminalio
import displayio
from adafruit_magtag.peripherals import Peripherals
from rainbowio import colorwheel

# from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label


def main():
    display = board.DISPLAY
    peripherals = Peripherals()

    display_things = displayio.Group(scale=1)

    palette = displayio.Palette(4)
    palette[3] = 0x000000
    palette[2] = 0x666666
    palette[1] = 0x999999
    palette[0] = 0xFFFFFF

    tilegrid = displayio.TileGrid(
        bitmap=ring_bitmap(), pixel_shader=palette, x=0, y=0, width=6, height=3
    )

    display_things.append(tilegrid)

    label = Label(
        terminalio.FONT,
        anchor_point=(0.5, 0.5),
        text="Hello, World",
        scale=3,
        color=0x000000,
        padding_top=3,
        padding_bottom=3,
        padding_left=3,
        padding_right=3,
        background_color=0xFFFFFF,
        anchored_position=(
            (display.width // 2),
            (display.height // 2),
        ),
    )
    display_things.append(label)

    display.show(display_things)
    refresh(display)

    run_rainbow_leds(peripherals)


def refresh(display):
    while True:
        try:
            display.refresh()
            return
        except RuntimeError:
            print("Too soon.")
            time.sleep(1.0)


def in_ring(center, x, y, radius=20, thickness=1):
    return (
        (radius - thickness) ** 2
        < (x - center[0]) ** 2 + (y - center[1]) ** 2
        < (radius + thickness) ** 2
    )


def ring_bitmap():
    bitmap = displayio.Bitmap(51, 51, 4)
    for x in range(51):
        for y in range(51):
            if any(
                in_ring(center, x, y, radius=32)
                for center in [(0, 0), (50, 0), (0, 50), (50, 50)]
            ):
                bitmap[x, y] = 3
            else:
                bitmap[x, y] = 0
    return bitmap


def run_rainbow_leds(peripherals):
    peripherals.neopixel_disable = False
    pixels = peripherals.neopixels

    pixels.brightness = 0.3

    while True:
        t = int(time.monotonic() * 30)
        for i in range(pixels.n):
            pixels[i] = colorwheel((t + i * 8) & 255)

        time.sleep(0.05)


if __name__ == "__main__":
    main()
