import math
import sys
from PIL import Image

pixels = []
rippedBytes=[]
byteStack=[]
romBytes  = []
addedBytes = 0
fillerByte = b'\x00'
pic_width=1
pic_height=1

def addPixel(byteArray):
    global pixels,addedBytes,fillerByte
    r = fillerByte
    g = fillerByte
    b = fillerByte
    fillerBytesAdded=3
    if len(byteArray)>0:
       # print("have r %s " % byteArray[:1].decode())
        r=byteArray[:1]
        fillerBytesAdded-=1
    if len(byteArray)>1:
        #print("have g %s " % byteArray[1:2].decode())
        g=byteArray[1:2]
        fillerBytesAdded-=1
    if len(byteArray)>2:
        #print("have b %s " % byteArray[2:3].decode())
        b=byteArray[2:3]
        fillerBytesAdded-=1
    addedBytes+=fillerBytesAdded
    pixels.append([
        int.from_bytes(r, byteorder=sys.byteorder),
        int.from_bytes(g, byteorder=sys.byteorder),
        int.from_bytes(b, byteorder=sys.byteorder)
    ])

def convertRomToPng(romName):
    global rippedBytes,pic_height,pic_width
    with open(romName, "rb", buffering=0) as f:
        idx = 0
        byte = True
        while byte:
            # Do stuff with byte.
            byte = f.read(3)
            if idx < 30:
                print("[%d]=[%s]=[%s]" % (idx, byte,byte.hex()))
            rippedBytes.append(byte)
            addPixel(byte)
            idx+=3

        pic_width = math.ceil(math.sqrt(len(pixels)))
        pic_height = math.ceil(len(pixels)/pic_width)
        print("Total[%d]=/3[%d]=width[%d]=height[%d]=added[%d]" % (
            idx,
            len(pixels),
            pic_width,
            pic_height,
            addedBytes
        ))
        #
        renderImg = Image.new('RGB', (pic_width, pic_height), color=(0, 0, 0))
        pCount = 0
        printError=True
        for r in range(pic_width):
            for c in range(pic_height):
                try:
                    renderImg.putpixel((r,c), (pixels[pCount][0],pixels[pCount][1],pixels[pCount][2]))
                    pCount+=1
                except IndexError:
                    if printError:
                        print("Added some extra pixels to account for [%d] bytes"%(addedBytes))
                        printError=False
            #insert our added pixel data!
            #renderImg.putpixel((pic_width-1,pic_height), (addedBytes,00, 00))
        renderImg.save(romName.replace(".nes", ".png"))

def writeItself(romName):
    bytesStack1 = []
    bytesStack2 = []
    dumpRom = romName.replace(".nes", "-redo.nes")
    with open(romName, "rb", buffering=0) as f:
        byte=True
        while byte:
            byte = f.read(3)
            bytesStack1.append(byte)

    #print(b''.join(bytesStack1))
    w = open(dumpRom, "wb")
    w.write(b''.join(bytesStack1))
    w.close()

    with open(dumpRom, "rb", buffering=0) as f:
        byte=True
        while byte:
            byte = f.read(3)
            bytesStack2.append(byte)

    for idx in range(len(bytesStack2)):
        if(bytesStack1[idx] == bytesStack2[idx] and idx < 100):
            print("[%d] Match? [%s] == [%s] ? [%s]" % (idx, bytesStack1[idx], bytesStack2[idx], (bytesStack1[idx] == bytesStack2[idx])))


def convertPngToRom(romName):
    global romBytes,rippedBytes
    im = Image.open(romName.replace(".nes", ".png"))
    rgb_im = im.convert('RGB')
    height, width = rgb_im.size
    bytesToSubtract = rgb_im.getpixel((height-1,width-1))[0]
    bytesToAllow    = (width*(height-1)*3)
    bytesToAllow   -= bytesToSubtract
    print("Was:[%d] Subtracting:[%d] Now: [%d]" % (
        (width * height * 3),
        bytesToSubtract,
        bytesToAllow
    ))
    idx=0
    for h in range(height):
        for w in range(width):
            r, g, b = rgb_im.getpixel((h, w))
            rbyte=(r).to_bytes(1,  byteorder=sys.byteorder)
            gbyte=(g).to_bytes(1,  byteorder=sys.byteorder)
            bbyte =(b).to_bytes(1, byteorder=sys.byteorder)
            if idx < 10:
                print(
                    rbyte,
                    gbyte,
                    bbyte
                )
            romBytes.append(rbyte)
            romBytes.append(gbyte)
            romBytes.append(bbyte)
            idx+=3
    f = open(romName.replace(".nes", "-pic.nes"), "wb")
    f.write(b''.join(romBytes))
    f.close()


if __name__ == '__main__':
   # writeItself("./Kickle Cubicle (USA).nes")
    try:
        fileToWorkFix=sys.argv[1]
        print(fileToWorkFix)
        if(fileToWorkFix[-3:] == "nes"):
            convertRomToPng(fileToWorkFix)
        elif(fileToWorkFix[-3:] == "png"):
            convertPngToRom(fileToWorkFix)
        else:
            print("Not sure what to do with filetype [%s]" % fileToWorkFix[-3])
    except IndexError:
        print("Did not pass a file to work on")