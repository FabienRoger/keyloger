import time
from datetime import datetime
from pynput import keyboard, mouse


def get_compact_datetime():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


# Function to handle key press events
def on_press(key):
    print(get_compact_datetime(), str(key))


# Function to handle mouse click events
def on_click(x, y, button, pressed):
    print(get_compact_datetime(), f"({x},{y}) {button} {pressed}")


def run():
    # Set up listeners
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)

    # Start listeners
    keyboard_listener.start()
    mouse_listener.start()

    # Interval for processing logs (in seconds)
    log_interval = 60 * 10

    assert log_interval > 1

    # Main loop
    try:
        while True:
            time.sleep(log_interval)
    except KeyboardInterrupt:
        # Stop listeners on manual interruption
        keyboard_listener.stop()
        mouse_listener.stop()


if __name__ == "__main__":
    run()
