import time
import board
import terminalio
import displayio
from adafruit_magtag.magtag import MagTag
from rainbowio import colorwheel

# import time
# import board
# import digitalio
# import adafruit_lis3dh

# # def acc_to_color(value):
# #     return int(abs(value) / 10 * 256)

# # i2c = board.I2C()
# # int1 = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)  # Set this to the correct pin for the interrupt!
# # lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1, address=0x19)

# # lis3dh.range = adafruit_lis3dh.RANGE_2_G

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

# time.sleep(display.time_to_refresh)
# time.sleep(display.time_to_refresh)
# display.refresh()
# time.sleep(display.time_to_refresh)

magtag.set_text("Hello!\nSecond.")


magtag.peripherals.neopixel_disable = False

pixels = magtag.peripherals.neopixels

pixels.brightness = 0.3

while True:
    t = int(time.monotonic() * 30)
    for i in range(pixels.n):
        pixels[i] = colorwheel((t + i * 8) & 255)

    time.sleep(0.05)


# # # lis3dh.set_tap(2, 60)

# # while True:
# #     # if lis3dh.tapped:
# #     #     magtag.peripherals.play_tone(400, 0.1)
# #     #     while lis3dh.tapped:
# #     #         time.sleep(0.1)
# #     # else:
# #     x, y, z = lis3dh.acceleration
# #     magtag.peripherals.neopixels.fill((acc_to_color(x), acc_to_color(y), acc_to_color(z)))

# #     time.sleep(0.1)

# #     # if light_level < 1000:
# #     #     magtag.peripherals.neopixels.fill((255, 55, 255))
# #     # else:
# #     #     magtag.peripherals.neopixel_disable = True



# # button_colors = ((255, 0, 0), (255, 150, 0), (0, 255, 255), (180, 0, 255))

# # magtag.peripherals.neopixel_disable = False
# # magtag.peripherals.neopixels.fill((255,55,255))


# # time.sleep(10)
