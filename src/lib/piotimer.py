from machine import Timer

class Piotimer:
    def __init__(self, freq, callback):
        self.timer = Timer()
        period = int(1000 / freq)
        self.timer.init(period=period, mode=Timer.PERIODIC, callback=lambda t: callback(0))

    def deinit(self):
        self.timer.deinit()
