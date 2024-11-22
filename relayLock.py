import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
RELAY_PIN = 18          # Replace with the GPIO pin connected to the relay module

GPIO.setup(RELAY_PIN, GPIO.OUT)

def control_relay(turn_on):
    """
    Controls a relay module. Turns on the relay if turn_on is 1, then automatically turns it off after 15 seconds.
    :param turn_on: Pass 1 to turn on the relay, any other value to do nothing.
    """
    if turn_on == 1:
        print("Turning on the relay...")
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn on the relay
        time.sleep(15)                     # Wait for 15 seconds
        GPIO.output(RELAY_PIN, GPIO.LOW)   # Turn off the relay
        print("Relay turned off automatically after 15 seconds.")
    else:
        print("Relay remains off.")


if __name__ == "__main__":
    # Usage example
    try:
        control_relay(1)  # Pass 1 to turn on the relay
    except KeyboardInterrupt:
        print("Operation interrupted by user")
    finally:
        GPIO.cleanup()
