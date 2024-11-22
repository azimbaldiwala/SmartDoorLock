import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
RELAY_PIN = 18          # Relay connected to this GPIO pin
BUTTON_PIN = 17         # Button connected to this GPIO pin (replace with your actual button GPIO pin)

# Set up relay and button pins
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Use an internal pull-up resistor

def turn_off_relay_on_button_press():
    """
    Turns off the relay on pin 18 when the push button connected to BUTTON_PIN is pressed.
    """
    try:
        # Initially turn on the relay for demonstration (if needed)
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        print("Relay is ON. Waiting for button press to turn it off...")

        # Wait for the button to be pressed
        while True:
            button_state = GPIO.input(BUTTON_PIN)
            if button_state == GPIO.LOW:  # Button pressed (assuming active-low button)
                print("Button pressed! Turning off relay...")
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off the relay
                break
            time.sleep(0.1)  # Small delay to avoid CPU overload

    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        GPIO.cleanup()

# Usage example
turn_off_relay_on_button_press()
