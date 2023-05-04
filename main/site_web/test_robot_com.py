import serial
import time

ser = serial.Serial("COM8", 115200)
print("Running")
print(ser.readline())
ser.write(b'mogo 1:10 2:10\r')

begin_time = time.time()
# clear buffer
# ser.reset_input_buffer()*
buffer = ser.read(ser.in_waiting)
print(buffer)
ser.flushInput()
ser.flushOutput()
time.sleep(1)
ser.flushInput()
ser.flushOutput()
try:
    while True:
        start_time = time.time()
        ser.write(b'getenc 1 2\r')
        # print((time.time()-begin_time)/1000,"ms")
        # read all characters in buffer
        buffer = ser.read(ser.in_waiting)
        buffer2 = ser.readline()
        print(buffer2)
        buffer2 = ser.readline()
        print(buffer2)
        buffer2 = ser.readline()
        print(buffer2)
        # convert bytes to string
        buffer = buffer.decode("utf-8")
        # split string into list
        buffer = buffer.split("\r\n")
        # remove last element of list
        buffer.pop()
        # buffer = buffer[1]
        print(buffer)
        # print(buffer.split(" "))
        # time.sleep(0)
except KeyboardInterrupt:
    # if interrupt stop serial
    ser.write(b'stop\r')
    ser.close()
    print("Serial closed")
    exit()
