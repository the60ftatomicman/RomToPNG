import math
import sys
from PIL import Image

pixels = []
romBytes  = []
addedBytes = 0
fillerByte = b'\x00'
pic_width=0
pic_height=0
def addPixel(byteArray):
    global pixels,addedBytes,fillerByte
    r = fillerByte
    g = fillerByte
    b = fillerByte
    fillerBytesAdded=3
    if len(byteArray)>0:
        r=byteArray[0]
        fillerBytesAdded-=1
    if len(byteArray)>1:
        g=byteArray[1]
        fillerBytesAdded-=1
    if len(byteArray)>2:
        b=byteArray[2]
        fillerBytesAdded-=1
    addedBytes+=fillerBytesAdded
    pixels.append([
        int.from_bytes(r,byteorder=sys.byteorder),
        int.from_bytes(g,byteorder=sys.byteorder),
        int.from_bytes(b,byteorder=sys.byteorder)
    ])

def convertRomToPng(romName):
    idx=0
    with open(romName, "rb") as f:
        byteStack = []
        byte = f.read(1)
        print("[%d]=[%s]=[%s]" % (idx, byte, byte.hex()))
        byteStack.append(byte)
        idx += 1
        while byte:
            # Do stuff with byte.
            byte = f.read(1)
            if idx < 30:
                print("[%d]=[%s]=[%s]" % (idx, byte,byte.hex()))
            byteStack.append(byte)
            idx+=1
            if(len(byteStack) == 3):
                addPixel(byteStack)
                byteStack.clear()
        if (len(byteStack) > 0):
            addPixel(byteStack)
        pic_width=math.isqrt(len(pixels))
        pic_height=pic_width
        #to do later -- in case we have uneven roms!
        #while(pic_width*pic_height < len(pixels)):
        #    pic_height+=1
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
        for r in range(pic_width):
            for c in range(pic_height):
                renderImg.putpixel((r,c), (pixels[pCount][0],pixels[pCount][1],pixels[pCount][2]))
                pCount+=1
        #insert our added pixel data!
        #renderImg.putpixel((pic_width-1,pic_height), (addedBytes,00, 00))
        renderImg.save(romName.replace(".nes", ".png"))

def convertPngToRom(romName):
    global romBytes
    im = Image.open(romName.replace(".nes", ".png"))
    rgb_im = im.convert('RGB')
    height, width = rgb_im.size
    bytesToSubtract = rgb_im.getpixel((height-1,width-1))[0]
    bytesToAllow    = (width*(height-1)*3)
    bytesToAllow   -= bytesToSubtract
    #bytesToAllow   -= width
    print("Was:[%d] Subtracting:[%d] Now: [%d]" % (
        (width * height * 3),
        bytesToSubtract,
        bytesToAllow
    ))
    idx=0
    for h in range(height):
        for w in range(width):
            r, g, b = rgb_im.getpixel((h, w))
            if idx < 10:
                print(
                    (r).to_bytes(1, byteorder=sys.byteorder),
                    (g).to_bytes(1, byteorder=sys.byteorder),
                    (b).to_bytes(1, byteorder=sys.byteorder)
                )
            romBytes.append((r).to_bytes(1, byteorder=sys.byteorder))
            romBytes.append((g).to_bytes(1, byteorder=sys.byteorder))
            romBytes.append((b).to_bytes(1, byteorder=sys.byteorder))
            idx+=1
    f = open(romName.replace(".nes", "-pic.nes"), "wb")
    f.write(b''.join(romBytes))
    f.close()


if __name__ == '__main__':
    convertRomToPng("./Kickle Cubicle (USA).nes")
    convertPngToRom("./Kickle Cubicle (USA).nes")