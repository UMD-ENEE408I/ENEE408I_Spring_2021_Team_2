import serial
import time

ser = serial.Serial('/dev/ttyUSB0')
time.sleep(1)
ser.write(b'f')

time.sleep(3)
# while True:
#     left1 = ser.read(2)
#     center1 = ser.read(2)
#     right1 = ser.read(2)

#     print('left:', int.from_bytes(left1, "big"), end='\t')
#     print('center:', int.from_bytes(center1, "big"), end='\t')
#     print('right:', int.from_bytes(right1, "big"))
    