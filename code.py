import time
import board
import terminalio
import displayio
from adafruit_magtag.magtag import MagTag
from rainbowio import colorwheel


print("Version 1")

magtag = MagTag()
display = magtag.display

magtag.add_text(
     text_font=terminalio.FONT,
     text_position=(
                      20,
                        (magtag.graphics.display.height // 2) - 1,
         ),
         text_scale=2.0,

)

display_things = displayio.Group(scale=1)


bitmap = displayio.Bitmap(51, 51, 4)

palette = displayio.Palette(4)
palette[3] = 0x000000
palette[2] = 0x666666
palette[1] = 0x999999
palette[0] = 0xffffff

def in_ring(center, x, y, radius=30, thickness=2):
    return (radius - thickness)**2 < (x - center[0]) **2 + (y - center[1]) ** 2 < (radius+thickness)**2


tilegrid = displayio.TileGrid(bitmap=bitmap, pixel_shader=palette, x=0, y=0, width=6, height=3)

for x in range(51):
    for y in range(51):
        if any(in_ring(center, x, y, radius=32) for center in [(0, 0), (50, 0), (0, 50), (50, 50)]):
            bitmap[x, y] = 3
        else:
            bitmap[x, y] = 0

magtag.graphics.set_background(0xffffff)

display.show(display_things)
display_things.append(tilegrid)

magtag.set_text("Hello!\nSecond.")


magtag.peripherals.neopixel_disable = False

pixels = magtag.peripherals.neopixels

pixels.brightness = 0.3

while True:
    t = int(time.monotonic() * 30)
    for i in range(pixels.n):
        pixels[i] = colorwheel((t + i * 8) & 255)

    time.sleep(0.05)
