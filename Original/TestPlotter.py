import socket
import sys
import time
import TIA
import RT






try:

    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore, QtGui
    import numpy as np
    # import scipy.fftpack
    import serial

except Exception as e:
    print (e)
    print("please install the prerequisite packages")
    input("press enter to exit")
    raise Exception()

# User Variables
DOWNSAMPLE = 640
WINDOW_SIZE = 10

# Calculated Values
CHUNK_SIZE = 1
SAMPLE_PERIOD = 1
SAMPLE_FREQ = 100
BUFFER_DEPTH = 1000

# Globals

win = None
curve1 = None
curve2 = None
curve3 = None
curve4 = None

data1 = None
data2 = None
data3 = None
data4 = None

dev = None

RTConverter = RT.RTThermistor4(A=float(6.71742703E-04), B=float(2.20416992E-04), C=float(9.98713347E-08), D=float(-4.61649439E-11))

def init():
    global curve1, curve2, curve3, curve4, data1, data2, data3, data4, xVals, dev, win, SAMPLE_FREQ, BUFFER_DEPTH, SAMPLE_PERIOD, DOWNSAMPLE

    dev = TIA.TIABuffer('com3', DOWNSAMPLE)
    dev.stopTrans()
    dev.resetBuffer()

    SAMPLE_FREQ = dev.getSampleRate()/DOWNSAMPLE
    SAMPLE_PERIOD = 1.0/SAMPLE_FREQ
    BUFFER_DEPTH = int(SAMPLE_FREQ * WINDOW_SIZE)


    win = pg.GraphicsWindow()

    p1 = win.addPlot(title = "Channel 1")
    p1.setLabel('bottom', 'Time', 's')
    p1.setLabel('left', 'Deg', 'c')
    p1.setMouseEnabled(y = False)
    p1.enableAutoRange(y=True)
    win.nextRow()

    p2 = win.addPlot(title = "Channel 2")
    p2.setLabel('bottom', 'Time', 's')
    p2.setLabel('left', 'Deg', 'c')
    p2.setMouseEnabled(y = False)
    p2.enableAutoRange(y=True)
    win.nextRow()

    p3 = win.addPlot(title = "Channel 3")
    p3.setLabel('bottom', 'Time', 's')
    p3.setLabel('left', 'Deg', 'c')
    p3.setMouseEnabled(y = False)
    p3.enableAutoRange(y=True)
    win.nextRow()

    p4 = win.addPlot(title = "Channel 4")
    p4.setLabel('bottom', 'Time', 's')
    p4.setLabel('left', 'Deg', 'c')
    p4.setMouseEnabled(y = False)
    p4.enableAutoRange(y=True)
    win.nextRow()


    data1 = [0]
    data2 = [0]
    data3 = [0]
    data4 = [0]
    #updateChunk(1)
    data1 = data1 * BUFFER_DEPTH
    data2 = data2 * BUFFER_DEPTH
    data3 = data3 * BUFFER_DEPTH
    data4 = data4 * BUFFER_DEPTH

    xVals = np.linspace(-1*SAMPLE_PERIOD*BUFFER_DEPTH, 0,BUFFER_DEPTH).tolist()

    curve1 = p1.plot(x=xVals,y=data1)
    curve2 = p2.plot(x=xVals,y=data2)
    curve3 = p3.plot(x=xVals,y=data3)
    curve4 = p4.plot(x=xVals,y=data4)

    print("filled buffer")
    return

def updateChunk(size):
    data1[:(-1*size)] = data1[size:]
    data2[:(-1*size)] = data2[size:]
    data3[:(-1*size)] = data3[size:]
    data4[:(-1*size)] = data4[size:]

    for pos in range((-1*size) , 0):


        # packet = (sock.recv(PACKET_SIZE-1))
        # if(len(packet) < PACKET_SIZE-1):
        #     # print len(packet)
        #     packet = packet + (sock.recv(PACKET_SIZE-1-len(packet)))

        # packet = processData(packet)
        packet = dev.readBuffer()
        packet = convertPacket(packet)
        data1[pos]=packet[0]
        data2[pos]=packet[1]
        data3[pos]=packet[2]
        data4[pos]=packet[3]

def convertPacket(data):
    output = []
    for i in range(len(data)):
        output.append(RTConverter.getTempC(data[i]))
    return output

def update():
##    global CHUNK_SIZE
##    maxChunk = int(com.inWaiting()/PACKET_SIZE)
##    if(maxChunk > CHUNK_SIZE):
##        updateChunk(maxChunk)
##        CHUNK_SIZE = CHUNK_SIZE + 5
##    else:
##        updateChunk(CHUNK_SIZE)
##        CHUNK_SIZE = CHUNK_SIZE - 1

    waiting = min(BUFFER_DEPTH, dev.inBuffer())
    waiting = max(1, waiting)
    updateChunk(waiting)


  
    
    # print(CHUNK_SIZE)
    curve1.setData(xVals, data1)
    curve2.setData(xVals, data2)
    curve3.setData(xVals, data3)
    curve4.setData(xVals, data4)

# def processData(raw):
#     output = []

#     raw = toIntArray(raw)
#     # print raw
#     # print
   
#     output.append(((raw[0]<<3) + (raw[1]>>5))%1023)
#     output.append((((raw[1]&31)<<6) + (raw[2]>>2))%1023)
#     output.append((((raw[2]&3)<<9) + (raw[3]<<1) + (raw[4]>>7))%1023)
#     output.append((((raw[4]&127)<<4) + (raw[5]>>4))%1023)
#     return output

# def findStart():
#     print("finding start")
#     while(ord(sock.recv(1)) != PACKET_HEADER):
#         continue
#     sock.recv(PACKET_SIZE-1)

#     sock.recv(PACKET_SIZE-1)
#     print("done")
#     return




# def toIntArray(charArray):
#     out = []
#     for x in charArray:
#         out.append(ord(x))
#     return out

def run():
    # findStart()
    print("starting")
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(1)
    dev.start()
    dev.startTrans()

    ## Start Qt event loop unless running in interactive mode or using pyside.
    if __name__ == '__main__':
        import sys
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
            print("done")







def shutdown():
    dev.stop()


   


init()
run()
shutdown()




