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

import secrets

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label

font = bitmap_font.load_font("fonts/Arial-12.pcf")

WHITE = 0xffffff
LIGHT_GREY = 0x999999
DARK_GREY = 0x666666
BLACK = 0x000000


async def main():
    display = board.DISPLAY
    peripherals = Peripherals()
    network = Network()

    print("Woken: ", alarm.wake_alarm)

    refresh_required = start_screen_refresh(display)

    if isinstance(alarm.wake_alarm, alarm.pin.PinAlarm):
        if alarm.wake_alarm.pin == board.BUTTON_A:
            switch_light(network)
        elif alarm.wake_alarm.pin == board.BUTTON_D:
            asyncio.create_task(run_rainbow_leds(peripherals))
        calendar_text = sleep_storage.read_string(0)
    else:
        try:
            calendar_text = fetch_calendar(network)
        except RuntimeError:
            calendar_text = "Could not fetch calendar"

        refresh_required.set()

    print("Calendar length: ", len(calendar_text))
    print("Creating UI:", time.monotonic())
    screen = create_ui(display, calendar_text, peripherals.battery, ["O", "Calendar", None, "Rainbows"])
    print("UI done!", time.monotonic())

    sleep_time = time.monotonic() + 3600

    while time.monotonic() < sleep_time:
        if peripherals.button_a_pressed:
            print("Button A")
            network.connect()
            print("Connected")
            response = network._wifi.requests.post(
                "http://wren.local:8123/api/services/switch/toggle",
                headers={"Authorization": "Bearer " + secrets.key},
                json={"entity_id": "switch.tasmota"})
            # sleep_time = time.monotonic() + 10
            print("B is pressed")
            await asyncio.sleep(2.0)
#            refresh_required.set()
        elif peripherals.button_b_pressed:
            sleep_time = time.monotonic() + 10
            print("B is pressed")
            refresh_required.set()
        elif peripherals.button_c_pressed:
            pass
        elif peripherals.button_d_pressed:
            sleep_time = time.monotonic() + 10
            asyncio.create_task(run_rainbow_leds(peripherals))

        await asyncio.sleep(0.1)

    peripherals.deinit()

    sleep_storage.store_string(0, calendar_text)

    print("Ready to sleep!")

    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 120)

    pin_alarms = [
        alarm.pin.PinAlarm(pin=button, value=False, pull=True)
        for button in [board.BUTTON_A, board.BUTTON_B]
    ]
    alarm.exit_and_deep_sleep_until_alarms(time_alarm, *pin_alarms)

async def handle_buttons(peripherals, network):
    print("Handling buttons!")
    if peripherals.button_a_pressed:
        switch_light(network)
        await asyncio.sleep(1.0)
    elif peripherals.button_d_pressed:
        asyncio.create_task(run_rainbow_leds(peripherals))

def switch_light(network):
    print("Switching light.")
    network.connect()
    print("Connected to network.")
    response = network._wifi.requests.post(
        "http://wren.local:8123/api/services/switch/toggle",
        headers={"Authorization": "Bearer " + secrets.key},
        json={"entity_id": "switch.tasmota"})
    print(response)


def first_n_lines(text, n):
    return '\n'.join(text.split('\n')[:n])

def create_ui(display, calendar_text, battery_voltage, button_label_texts):
    screen = displayio.Group()
    calendar_screen = displayio.Group()
    battery_screen = displayio.Group()

    screen = displayio.Group()

    screen.append(background(display, WHITE))

    calendar_label = Label(
        font,
        anchor_point=(0.0, 0.0),
        text=first_n_lines(calendar_text, 5),
        color=BLACK,
        padding_top=3,
        padding_bottom=3,
        padding_left=3,
        padding_right=3,
        line_spacing=0.9,
        background_color=WHITE,
        anchored_position=(0, 0)
    )
    screen.append(calendar_label)

    for label in button_labels(display, button_label_texts):
        screen.append(label)

    battery_label = Label(
        font,
        anchor_point=(1.0, 0.0),
        text=f"{battery_voltage:.2f} V",
        color=BLACK,
        padding_top=3,
        padding_bottom=3,
        padding_left=3,
        padding_right=3,
        line_spacing=0.9,
        background_color=WHITE,
        anchored_position=(display.width, 0)
    )
    screen.append(battery_label)
    display.show(screen)
    return screen

def button_labels(display, label_texts):
    labels = []
    for (i, text) in enumerate(label_texts):
        if not text:
            continue
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


def fetch_calendar(network):
    network.connect()
    return network.fetch("http://192.168.0.32:5000/").text

def start_screen_refresh(display):
    refresh_required = asyncio.Event()
    asyncio.create_task(screen_refresher(display, refresh_required))
    return refresh_required

async def screen_refresher(display, refresh_required):
    print("Screen refresher starting.")
    while True:
        await refresh_required.wait()
        await refresh_screen_when_ready(display)
        refresh_required.clear()


async def refresh_screen_when_ready(display):
    print("Waiting until I can refresh the screen.")
    while display.time_to_refresh > 0:
        await asyncio.sleep(display.time_to_refresh)
    print(display.time_to_refresh, display.busy)
    await asyncio.sleep(1.0)
    display.refresh()


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
