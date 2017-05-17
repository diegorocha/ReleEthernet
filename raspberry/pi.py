try:
    from RPi import GPIO
except RuntimeError:
    from mock import GPIO


class ReleInterface(object):
    def __init__(self, gpio_pin=17):
        self.pin = gpio_pin
        self._setup()

    def _setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)

    @property
    def is_on(self):
        return bool(GPIO.input(self.pin))

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)

    def toggle(self):
        if self.is_on:
            self.off()
        else:
            self.on()
