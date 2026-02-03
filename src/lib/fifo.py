class Fifo:
    def __init__(self, size):
        self.size = size
        self.buffer = [0] * size
        self.head = 0
        self.tail = 0
        self.count = 0

    def put(self, value):
        if self.count < self.size:
            self.buffer[self.head] = value
            self.head = (self.head + 1) % self.size
            self.count += 1

    def get(self):
        if self.count > 0:
            value = self.buffer[self.tail]
            self.tail = (self.tail + 1) % self.size
            self.count -= 1
            return value
        return None

    def empty(self):
        return self.count == 0
