from micropython import const
import framebuf

# SSD1306 commands
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xA4)
SET_NORM_INV        = const(0xA6)
SET_DISP            = const(0xAE)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xA0)
SET_MUX_RATIO       = const(0xA8)
SET_COM_OUT_DIR     = const(0xC0)
SET_DISP_OFFSET     = const(0xD3)
SET_COM_PIN_CFG     = const(0xDA)
SET_DISP_CLK_DIV    = const(0xD5)
SET_PRECHARGE       = const(0xD9)
SET_VCOM_DESEL      = const(0xDB)
SET_CHARGE_PUMP     = const(0x8D)


class SSD1306:
    def __init__(self, width, height, external_vcc=False):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = height // 8

        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(
            self.buffer, self.width, self.height, framebuf.MONO_VLSB
        )

        self.init_display()

    def init_display(self):
        self.write_cmd(SET_DISP | 0x00)           # display off
        self.write_cmd(SET_DISP_CLK_DIV)
        self.write_cmd(0x80)
        self.write_cmd(SET_MUX_RATIO)
        self.write_cmd(self.height - 1)
        self.write_cmd(SET_DISP_OFFSET)
        self.write_cmd(0x00)
        self.write_cmd(SET_DISP_START_LINE | 0x00)
        self.write_cmd(SET_CHARGE_PUMP)
        self.write_cmd(0x10 if self.external_vcc else 0x14)
        self.write_cmd(SET_MEM_ADDR)
        self.write_cmd(0x00)                      # horizontal addressing
        self.write_cmd(SET_SEG_REMAP | 0x01)
        self.write_cmd(SET_COM_OUT_DIR | 0x08)

        self.write_cmd(SET_COM_PIN_CFG)
        self.write_cmd(0x12)                      # 128x64

        self.write_cmd(SET_CONTRAST)
        self.write_cmd(0x9F if self.external_vcc else 0xCF)

        self.write_cmd(SET_PRECHARGE)
        self.write_cmd(0x22 if self.external_vcc else 0xF1)

        self.write_cmd(SET_VCOM_DESEL)
        self.write_cmd(0x30)

        self.write_cmd(SET_ENTIRE_ON)
        self.write_cmd(SET_NORM_INV)
        self.write_cmd(SET_DISP | 0x01)           # display on

        self.fill(0)
        self.show()

    def write_cmd(self, cmd):
        raise NotImplementedError

    def write_data(self, buf):
        raise NotImplementedError

    # Drawing helpers
    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col=None):
        if col is None:
            return self.framebuf.pixel(x, y)
        self.framebuf.pixel(x, y, col)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)

    def line(self, x0, y0, x1, y1, col=1):
        self.framebuf.line(x0, y0, x1, y1, col)

    def rect(self, x, y, w, h, col=1):
        self.framebuf.rect(x, y, w, h, col)

    def fill_rect(self, x, y, w, h, col=1):
        self.framebuf.fill_rect(x, y, w, h, col)

    def invert(self, invert):
        self.write_cmd(0xA7 if invert else 0xA6)

    def show(self):
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.width - 1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.cmd = bytearray(2)
        self.cmd[0] = 0x80
        self.data = bytearray(1)
        self.data[0] = 0x40
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.cmd[1] = cmd
        self.i2c.writeto(self.addr, self.cmd)

    def write_data(self, buf):
        self.i2c.writeto(self.addr, self.data + buf)
