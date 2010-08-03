import serial 
import struct 

S_BEEP = "\x02\x0B\xFF"
R_BEEP = 2

S_FIND = "\x02\x02\x26"
R_FIND = 3

S_SELECT = "\x01\x04"
R_SELECT = 2

S_RW_1 = "\x02\x02\x52"
R_RW_1 = 4

S_RW_2 = "\x01\x03"
R_RW_2 = 6
ID_MASK = "\x00\x00\x01\x01\x01\x01"

S_RW_3 = "\x01\x04"
R_RW_3 = 4

BAUD = 9600

def ByteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """
    
    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        
    return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()

def HexToByte( hexStr ):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case    
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )

    bytes = []

    hexStr = ''.join( hexStr.split(" ") )

    for i in range(0, len(hexStr), 2):
        bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )

    return ''.join( bytes )

# 16 Sectors x 4 Blocks per Sector. 
# Note: 0x0 is the Manufacturer Block and is read-only. This is IC Manufacturer data
# Note: *x3 is the "Sector Trailer"
# Each block is 16 bytes
# Each sector has 3 blocks of RW space. (Sector 0 has 2)
# The 4th block of each sector contains: 
# - Byte 0-5 Secret Key A
# - Byte 6-9 Access Bits
# - Byte 10-15 Secret Key B (optional) 
class CardReader:
    def __init__(self, device):
        self.ser = serial.Serial(device, 9600)
    
    def send(self, command):
        print "> %s" % ByteToHex(command) 
        
        self.ser.write(command)
        size = ord(self.ser.read(1))
        ret = self.ser.read(size)
        print "%s " % ByteToHex(ret)
        return ByteToHex(ret)

    def beep(self):
        print "BEEP"
        ret = self.send(S_BEEP)
        assert ret == "00"

    def find(self):
        print "FIND"
        ret = self.send(S_FIND)
        assert ret == "00 04 00"
        
    def select(self):
        print "SELECT"
        self.send(S_SELECT)
        
    def read(self, blocks):
        ret = self.send("\x02\x02\x52")
        ret = self.send("\x01\x03")
        ret = self.send("\x01\x04")
        ret = self.send("\x04\x05\x60\x00\x00")
        data = []
        for i in blocks:
            data.append(self.send("\x02\x08" + struct.pack('b',i)))
        return data
        
c = CardReader('/dev/cu.PL2303-00002006')
c.beep()
c.find()
print c.read(range(64))
