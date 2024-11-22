import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
TRIG = 23               # Replace with your TRIG pin number
ECHO = 24               # Replace with your ECHO pin number

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def is_in_range(threshold=30):
    """
    Checks if an object is within the specified threshold distance using an ultrasonic sensor.
    :param threshold: The distance in cm to check for detection (default is 30 cm).
    :return: True if object is within the threshold distance, False otherwise.
    """
    # Send a 10us pulse to trigger the sensor
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for the start of the echo response
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Wait for the end of the echo response
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate distance based on the time of flight
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound: 34300 cm/s divided by 2 for round trip

    # Return True if the distance is within the threshold, otherwise False
    return distance <= threshold



if __name__ == "__main__":

    # Usage example
    try:
        while True:
            if is_in_range():
                print("Object detected within 30 cm")
            else:
                print("No object within range")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")
    finally:
        GPIO.cleanup()
