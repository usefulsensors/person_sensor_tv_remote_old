
import pulseio
import adafruit_irremote
from adafruit_circuitplayground.express import cpx
import time
import struct
import displayio
import digitalio
import busio
import board
import bitmaptools
while True:
    if cpx.button_a:
        print("Button A pressed! \n")
        cpx.red_led = True
        # encoder.transmit(pulseout, 0x20DF10EF)
        # encoder.transmit(pulseout, [0xdf, 0x20, 0xef, 0x10])
        # 0x20DF0DF2
        encoder.transmit(pulseout, [0xdf, 0x20, 0xf2, 0x0d])
        # encoder.transmit(pulseout, [223, 32, 239, 16])
        cpx.red_led = False
        # wait so the receiver can get the full message
        time.sleep(0.2)
    if cpx.button_b:
        print("Button B pressed! \n")
        cpx.red_led = True
        # 0x20DF5DA2
        encoder.transmit(pulseout, [0xdf, 0x20, 0xa2, 0x5d])
        cpx.red_led = False
        time.sleep(0.2)

# Example of accessing the Person Sensor from Useful Sensors on a Pico using
# CircuitPython. See https://usfl.ink/ps_dev for the full developer guide.


PAUSE_IR_CODES =

# The person sensor has the I2C ID of hex 62, or decimal 98.
PERSON_SENSOR_I2C_ADDRESS = 0x62

# We will be reading raw bytes over I2C, and we'll need to decode them into
# data structures. These strings define the format used for the decoding, and
# are derived from the layouts defined in the developer guide.
PERSON_SENSOR_I2C_HEADER_FORMAT = "BBH"
PERSON_SENSOR_I2C_HEADER_BYTE_COUNT = struct.calcsize(
    PERSON_SENSOR_I2C_HEADER_FORMAT)

PERSON_SENSOR_FACE_FORMAT = "BBBBBBbB"
PERSON_SENSOR_FACE_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_FACE_FORMAT)

PERSON_SENSOR_FACE_MAX = 4
PERSON_SENSOR_RESULT_FORMAT = PERSON_SENSOR_I2C_HEADER_FORMAT + \
    "B" + PERSON_SENSOR_FACE_FORMAT * PERSON_SENSOR_FACE_MAX + "H"
PERSON_SENSOR_RESULT_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_RESULT_FORMAT)

# How long to pause between sensor polls.
PERSON_SENSOR_DELAY = 0.2

# The Pico doesn't support board.I2C(), so check before calling it. If it isn't
# present then we assume we're on a Pico and call an explicit function.
try:
    i2c = board.I2C()
except:
    i2c = busio.I2C(scl=board.GP5, sda=board.GP4)

# Wait until we can access the bus.
while not i2c.try_lock():
    pass

# Create a 'pulseio' output, to send infrared signals on the IR transmitter @ 38KHz
pulseout = pulseio.PulseOut(board.IR_TX, frequency=38000, duty_cycle=2 ** 15)
# Create an encoder that will take numbers and turn them into NEC IR pulses
encoder = adafruit_irremote.GenericTransmit(header=[9500, 4500], one=[550, 550],
                                            zero=[550, 1700], trail=0)

time_since_face_seen = 0
is_paused = False

# Keep looping and reading the person sensor results.
while True:
    read_data = bytearray(PERSON_SENSOR_RESULT_BYTE_COUNT)
    i2c.readfrom_into(PERSON_SENSOR_I2C_ADDRESS, read_data)

    offset = 0
    (pad1, pad2, payload_bytes) = struct.unpack_from(
        PERSON_SENSOR_I2C_HEADER_FORMAT, read_data, offset)
    offset = offset + PERSON_SENSOR_I2C_HEADER_BYTE_COUNT

    (num_faces) = struct.unpack_from("B", read_data, offset)
    num_faces = int(num_faces[0])
    offset = offset + 1

    faces = []
    for i in range(num_faces):
        (box_confidence, box_left, box_top, box_right, box_bottom, id_confidence, id,
         is_facing) = struct.unpack_from(PERSON_SENSOR_FACE_FORMAT, read_data, offset)
        offset = offset + PERSON_SENSOR_FACE_BYTE_COUNT
        face = {
            "box_confidence": box_confidence,
            "box_left": box_left,
            "box_top": box_top,
            "box_right": box_right,
            "box_bottom": box_bottom,
            "id_confidence": id_confidence,
            "id": id,
            "is_facing": is_facing,
        }
        faces.append(face)
    checksum = struct.unpack_from("H", read_data, offset)

    has_face = (num_faces > 0)
    if has_face:
        time_since_face_seen = 0
    else:
        time_since_face_seen += 1

    if time_since_main_face_seen == FACE_TIMEOUT_COUNT:
        print("Locking!")

    time.sleep(PERSON_SENSOR_DELAY)
