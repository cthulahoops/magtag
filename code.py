import time
import asyncio
import board
import terminalio
import alarm
import sleep_storage
import displayio
from adafruit_magtag.peripherals import Peripherals
from adafruit_magtag.network import Network
from rainbowio import colorwheel

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label

font = bitmap_font.load_font("fonts/PermianSansTypeface-11.bdf")

WHITE = 0xffffff
LIGHT_GREY = 0x999999
DARK_GREY = 0x666666
BLACK = 0x000000

async def main():
    print("Woken: ", alarm.wake_alarm)
    display = board.DISPLAY
    peripherals = Peripherals()

    refresh_required = start_screen_refresh(display)

    screen = displayio.Group()
    calendar_screen = displayio.Group()
    battery_screen = displayio.Group()

    screen.append(background(display, WHITE))
    screen.append(calendar_screen)

    # palette = displayio.Palette(4)
    # palette[3] = BLACK
    # palette[2] = DARK_GREY
    # palette[1] = WHITE_GREY
    # palette[0] = WHITE

    # tilegrid = displayio.TileGrid(
    #     bitmap=ring_bitmap(), pixel_shader=palette, x=0, y=0, width=6, height=3
    # )

    # display_things.append(tilegrid)

    if isinstance(alarm.wake_alarm, alarm.pin.PinAlarm):
        calendar_text = sleep_storage.read_string(0)
    else:
        try:
            peripherals.neopixel_disable = False
            peripherals.neopixels.fill(0xff00ff)
            calendar_text = fetch_calendar()
        except RuntimeError:
            calendar_text = "Could not fetch calendar"
        finally:
            peripherals.neopixel_disable = True

    # calendar_text = calendar
    print(len(calendar_text))

#    calendar_text = "Today: Minimal viable code!"
#    calendar_text = '\n'.join(f"{entry['time']}   {entry['summary']}" for entry in calendar)
#    print(calendar)

    calendar_label = Label(
        font,
        anchor_point=(0.0, 0.0),
        text=calendar_text,
        color=BLACK,
        padding_top=3,
        padding_bottom=3,
        padding_left=3,
        padding_right=3,
        line_spacing=0.9,
        background_color=WHITE,
        anchored_position=(5, 5)
    )
    calendar_screen.append(calendar_label)

    for label in button_labels(display, ["O", "Calendar", "Battery", "Rainbows"]):
        screen.append(label)

    battery_label = Label(
        font,
        anchor_point=(0.0, 0.0),
        text=f"Battery: {peripherals.battery} V",
        color=BLACK,
        padding_top=3,
        padding_bottom=3,
        padding_left=3,
        padding_right=3,
        line_spacing=0.9,
        background_color=WHITE,
        anchored_position=(5, 5)
    )
    battery_screen.append(battery_label)

    display.show(screen)
    refresh_required.set()

    sleep_time = time.monotonic() + 10

    while time.monotonic() < sleep_time:
        if peripherals.button_b_pressed:
            sleep_time = time.monotonic() + 10
            print("A is pressed")
            if screen[1] != calendar_screen:
                screen[1] = calendar_screen
            refresh_required.set()

        elif peripherals.button_c_pressed:
            sleep_time = time.monotonic() + 10
            print("B is pressed")
            battery_label.text = f"Battery: {peripherals.battery} V"
            if screen[1] != battery_screen:
                screen[1] = battery_screen
            refresh_required.set()

        elif peripherals.button_d_pressed:
            sleep_time = time.monotonic() + 10
            asyncio.create_task(run_rainbow_leds(peripherals))

        await asyncio.sleep(0.1)

    peripherals.deinit()

    sleep_storage.store_string(0, calendar_text)

    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 120)
    pin_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_A, value=False, pull=True)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm, pin_alarm)

def button_labels(display, label_texts):
    labels = []
    for (i, text) in enumerate(label_texts):
        labels.append(Label(
               font,
               anchor_point=(0.5, 0.0),
               text=text,
               color=BLACK,
               padding_top=3,
               padding_bottom=3,
               padding_left=3,
               padding_right=3,
               line_spacing=0.9,
               background_color=LIGHT_GREY,
               anchored_position=((2 * i + 1) * display.width / 8.0 - 12.0, display.height - 25),
               base_alignment=True,
        ))
    return labels


def fetch_calendar():
    network = Network()
    return network.fetch("http://192.168.0.17:5000/").text

def start_screen_refresh(display):
    refresh_required = asyncio.Event()
    asyncio.create_task(screen_refresher(display, refresh_required))
    return refresh_required

async def screen_refresher(display, refresh_required):
    while True:
        await refresh_required.wait()
        print("Waiting until I can refresh the screen.")
        await asyncio.sleep(display.time_to_refresh + 0.1)
        refresh_required.clear()
        print(display.time_to_refresh, display.busy)
        display.refresh()

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


async def run_rainbow_leds(peripherals):
    peripherals.neopixel_disable = False
    pixels = peripherals.neopixels

    pixels.brightness = 0.3

    while True:
        t = int(time.monotonic() * 30)
        for i in range(pixels.n):
            pixels[i] = colorwheel((t + i * 8) & 255)

        await asyncio.sleep(0.05)


def background(display, color):
    color_bitmap = displayio.Bitmap(display.width, display.height, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = color
    return displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

if __name__ == "__main__":
    asyncio.run(main())
