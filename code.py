import time
import board
import terminalio
import alarm
import displayio
from adafruit_magtag.peripherals import Peripherals
from adafruit_magtag.network import Network
from rainbowio import colorwheel

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label

font = bitmap_font.load_font("fonts/PermianSansTypeface-11.bdf")

def button_labels(display, label_texts):
    labels = []
    for (i, text) in enumerate(label_texts):
        labels.append(Label(
               font,
               anchor_point=(0.5, 0.0),
               text=text,
               color=0xffffff,
               padding_top=3,
               padding_bottom=3,
               padding_left=3,
               padding_right=3,
               line_spacing=0.9,
               background_color=0x000000,
               anchored_position=((2 * i + 1) * display.width / 8.0 - 12.0, display.height - 25),
               base_alignment=True,
        ))
    return labels


def main():
    display = board.DISPLAY
    peripherals = Peripherals()

    calendar_screen = displayio.Group()
    battery_screen = displayio.Group()

    # palette = displayio.Palette(4)
    # palette[3] = 0x000000
    # palette[2] = 0x666666
    # palette[1] = 0x999999
    # palette[0] = 0xFFFFFF

    # tilegrid = displayio.TileGrid(
    #     bitmap=ring_bitmap(), pixel_shader=palette, x=0, y=0, width=6, height=3
    # )

    # display_things.append(tilegrid)


    network = Network()
    calendar_text = network.fetch("http://192.168.0.17:5000/").text
    # calendar_text = calendar
    # print(calendar_text)

#    calendar_text = "Today: Minimal viable code!"
#    calendar_text = '\n'.join(f"{entry['time']}   {entry['summary']}" for entry in calendar)
#    print(calendar)

    calendar_label = Label(
        font,
        anchor_point=(0.0, 0.0),
        text=calendar_text,
        color=0x000000,
        padding_top=3,
        padding_bottom=3,
        padding_left=3,
        padding_right=3,
        line_spacing=0.9,
        background_color=0xFFFFFF,
        anchored_position=(5, 5)
    )
    calendar_screen.append(calendar_label)

    for label in button_labels(display, ["O", "Calendar", "Battery", "Rainbows"]):
        calendar_screen.append(label)

    battery_label = Label(
        font,
        anchor_point=(0.0, 0.0),
        text=f"Battery: {peripherals.battery} V",
        color=0x000000,
        padding_top=3,
        padding_bottom=3,
        padding_left=3,
        padding_right=3,
        line_spacing=0.9,
        background_color=0xFFFFFF,
        anchored_position=(5, 5)
    )
    battery_screen.append(battery_label)

    active_display = calendar_screen
    display.show(active_display)
    refresh(display)

    # time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 120)
    # alarm.exit_and_deep_sleep_until_alarms(time_alarm)

    while True:
        if peripherals.button_b_pressed:
            print("A is pressed")
            active_display = calendar_screen
            display.show(active_display)
            refresh(display)

        elif peripherals.button_c_pressed:
            print("B is pressed")
            battery_label.text = f"Battery: {peripherals.battery} V"
            active_display = battery_screen
            display.show(active_display)
            refresh(display)

        elif peripherals.button_d_pressed:
            run_rainbow_leds(peripherals)

        time.sleep(0.1)


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
