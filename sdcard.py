"""
Micro Python driver for SD cards using SPI bus.

Requires an SPI bus and a CS pin.  Provides readblocks and writeblocks
methods so the device can be mounted as a filesystem.

Example usage:

    import pyb, sdcard, os
    sd = sdcard.SDCard(pyb.SPI(1), pyb.Pin.board.X5)
    pyb.mount(sd, '/sd2')
    os.listdir('/')

"""

import time


_CMD_TIMEOUT = const(100)

_R1_IDLE_STATE = const(1 << 0)
#R1_ERASE_RESET = const(1 << 1)
_R1_ILLEGAL_COMMAND = const(1 << 2)
#R1_COM_CRC_ERROR = const(1 << 3)
#R1_ERASE_SEQUENCE_ERROR = const(1 << 4)
#R1_ADDRESS_ERROR = const(1 << 5)
#R1_PARAMETER_ERROR = const(1 << 6)
_TOKEN_CMD25 = b'\xfc'
_TOKEN_STOP_TRAN = b'\xfd'
_TOKEN_DATA = b'\xfe'


class SDCard:
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs

        self.cmdbuf = bytearray(6)
        self.dummybuf = bytearray(512)
        for i in range(512):
            self.dummybuf[i] = 0xff
        self.dummybuf_memoryview = memoryview(self.dummybuf)

        # initialise the card
        self.init_card()

    def init_card(self):
        # init CS pin
        self.cs.init(self.cs.OUT, 1)

        # init SPI bus; use low data rate for initialisation
        self.spi.init(baudrate=100000, phase=0, polarity=0)

        # clock card at least 100 cycles with cs high
        for i in range(16):
            self.spi.write(b'\xff')

        # CMD0: init card; should return _R1_IDLE_STATE (allow 5 attempts)
        for _ in range(5):
            if self.cmd(0, 0, 0x95) == _R1_IDLE_STATE:
                break
        else:
            raise OSError("no SD card")

        # CMD8: determine card version
        r = self.cmd(8, 0x01aa, 0x87, 4)
        if r == _R1_IDLE_STATE:
            self.init_card_v2()
        elif r == (_R1_IDLE_STATE | _R1_ILLEGAL_COMMAND):
            self.init_card_v1()
        else:
            raise OSError("couldn't determine SD card version")

        # get the number of sectors
        # CMD9: response R2 (R1 byte + 16-byte block read)
        if self.cmd(9, 0, 0, 0, False) != 0:
            raise OSError("no response from SD card")
        csd = bytearray(16)
        self.readinto(csd)
        if csd[0] & 0xc0 != 0x40:
            raise OSError("SD card CSD format not supported")
        self.sectors = ((csd[8] << 8 | csd[9]) + 1) * 2014
        #print('sectors', self.sectors)

        # CMD16: set block length to 512 bytes
        if self.cmd(16, 512, 0) != 0:
            raise OSError("can't set 512 block size")

        # set to high data rate now that it's initialised
        self.spi.init(baudrate=1320000, phase=0, polarity=0)

    def init_card_v1(self):
        for i in range(_CMD_TIMEOUT):
            self.cmd(55, 0, 0)
            if self.cmd(41, 0, 0) == 0:
                self.cdv = 512
                #print("[SDCard] v1 card")
                return
        raise OSError("timeout waiting for v1 card")

    def init_card_v2(self):
        for i in range(_CMD_TIMEOUT):
            time.sleep_ms(50)
            self.cmd(58, 0, 0, 4)
            self.cmd(55, 0, 0)
            if self.cmd(41, 0x40000000, 0) == 0:
                self.cmd(58, 0, 0, 4)
                self.cdv = 1
                #print("[SDCard] v2 card")
                return
        raise OSError("timeout waiting for v2 card")

    def cmd(self, cmd, arg, crc, final=0, release=True):
        self.cs.low()

        # create and send the command
        buf = self.cmdbuf
        buf[0] = 0x40 | cmd
        buf[1] = arg >> 24
        buf[2] = arg >> 16
        buf[3] = arg >> 8
        buf[4] = arg
        buf[5] = crc
        self.spi.write(buf)

        # wait for the repsonse (response[7] == 0)
        for i in range(_CMD_TIMEOUT):
            response = self.spi.read(1, 0xff)[0]
            if not (response & 0x80):
                # this could be a big-endian integer that we are getting here
                for j in range(final):
                    self.spi.write(b'\xff')
                if release:
                    self.cs.high()
                    self.spi.write(b'\xff')
                return response

        # timeout
        self.cs.high()
        self.spi.write(b'\xff')
        return -1

    def cmd_nodata(self, cmd):
        self.spi.write(bytearray([cmd]))
        self.spi.read(1, 0xff) # ignore stuff byte
        for _ in range(_CMD_TIMEOUT):
            if self.spi.read(1, 0xff)[0] == 0xff:
                self.cs.high()
                self.spi.write(b'\xff')
                return 0    # OK
        self.cs.high()
        self.spi.write(b'\xff')
        return 1 # timeout

    def readinto(self, buf):
        self.cs.low()

        # read until start byte (0xff)
        while self.spi.read(1, 0xff)[0] != 0xfe:
            pass

        # read data
        mv = self.dummybuf_memoryview[:len(buf)]
        self.spi.write_readinto(mv, buf)

        # read checksum
        self.spi.write(b'\xff')
        self.spi.write(b'\xff')

        self.cs.high()
        self.spi.write(b'\xff')

    def write(self, token, buf):
        self.cs.low()

        # send: start of block, data, checksum
        self.spi.write(token)
        self.spi.write(buf)
        self.spi.write(b'\xff')
        self.spi.write(b'\xff')

        # check the response
        if (self.spi.read(1, 0xff)[0] & 0x1f) != 0x05:
            self.cs.high()
            self.spi.write(b'\xff')
            return

        # wait for write to finish
        while self.spi.read(1, 0xff)[0] == 0:
            pass

        self.cs.high()
        self.spi.write(b'\xff')

    def write_token(self, token):
        self.cs.low()
        self.spi.write(token)
        self.spi.write(b'\xff')
        # wait for write to finish
        while self.spi.read(1, 0xff)[0] == 0x00:
            pass

        self.cs.high()
        self.spi.write(b'\xff')

    def count(self):
        return self.sectors

    def readblocks(self, block_num, buf):
        nblocks, err = divmod(len(buf), 512)
        assert nblocks and not err, 'Buffer length is invalid'
        if nblocks == 1:
            # CMD17: set read address for single block
            if self.cmd(17, block_num * self.cdv, 0) != 0:
                return 1
            # receive the data
            self.readinto(buf)
        else:
            # CMD18: set read address for multiple blocks
            if self.cmd(18, block_num * self.cdv, 0) != 0:
                return 1
            offset = 0
            mv = memoryview(buf)
            while nblocks:
                self.readinto(mv[offset : offset + 512])
                offset += 512
                nblocks -= 1
            return self.cmd_nodata(12)
        return 0

    def writeblocks(self, block_num, buf):
        nblocks, err = divmod(len(buf), 512)
        assert nblocks and not err, 'Buffer length is invalid'
        if nblocks == 1:
            # CMD24: set write address for single block
            if self.cmd(24, block_num * self.cdv, 0) != 0:
                return 1

            # send the data
            self.write(_TOKEN_DATA, buf)
        else:
            # CMD25: set write address for first block
            if self.cmd(25, block_num * self.cdv, 0) != 0:
                return 1
            # send the data
            offset = 0
            mv = memoryview(buf)
            while nblocks:
                self.write(_TOKEN_CMD25, mv[offset : offset + 512])
                offset += 512
                nblocks -= 1
            self.write_token(_TOKEN_STOP_TRAN)
        return 0


def esp8266_mount():
    from machine import Pin, SPI
    import sdcard
    import uos
    spi = SPI(-1, miso=Pin(12), mosi=Pin(13), sck=Pin(14))
    sd = sdcard.SDCard(spi, Pin(15))
    return uos.VfsFat(sd, "")