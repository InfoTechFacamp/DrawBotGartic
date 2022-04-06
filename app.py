import eel
import urllib.request
from datetime import datetime
from PIL import Image as img
import colorsys
from pynput.mouse import Controller
import keyboard
import os.path
from PIL import ImageGrab
from PIL import Image
import requests
from io import BytesIO
import colorsys
import pyautogui
import cv2
import numpy as np

eel.init('app')
urldaimagem = ""
globalConfig = []

espacoPixels = 1
tipoConversao = 'RGB'
quantidadeCores = 16000000
tamanhoImagemX = 510
tamanhoImagemY = 420
pularBranco = True
#pyautogui.PAUSE = 1/100
desenhando = False

def is_url_image(image_url):
   image_formats = ("image/png", "image/jpeg", "image/jpg")
   r = requests.head(image_url)
   if r.headers["content-type"] in image_formats:
      return True
   return False

@eel.expose
def drawImage(imageurl, conversion, xsize, ysize, skipWhite, drawarea, clicktime, numberofcolors, pixelgap):
    global pularBranco
    if skipWhite == 0:
        pularBranco = False
    else:
        pularBranco = True
    if imageurl == "" or is_url_image(imageurl) == False:
        eel.setLogText("Image URL invalid\n")
    else:
        global urldaimagem
        urldaimagem = imageurl
        global tipoConversao
        tipoConversao = conversion
        global tamanhoImagemX
        global tamanhoImagemY
        global quantidadeCores
        global desenhando
        if numberofcolors == "":
            quantidadeCores = 16000000
        else:
            quantidadeCores = int(numberofcolors)
        if clicktime == "":
            clicktime = 1/100
        else:
            clicktime = float(clicktime)
        pyautogui.PAUSE = clicktime
        if pixelgap == "":
            pixelgap = 1
        else:
            pixelgap = int(pixelgap)
        if configExiste() == 1:
            desenhando = True
            if drawarea == 1:
                getConfig()
                global globalConfig
                tamanhoImagemX = globalConfig[10] - globalConfig[8]
                tamanhoImagemY = globalConfig[11] - globalConfig[9]
                eel.prompt_alerts("Drawing process started, press ctrl+b to start\nhit q to stop drawing")
                while not keyboard.is_pressed("ctrl+b") and desenhando == True:
                    pass
                if keyboard.is_pressed("ctrl+b"):
                    pyautogui.moveTo(globalConfig[8],globalConfig[9])
                    while not keyboard.is_pressed("q"):
                        receberImagem()
                    if keyboard.is_pressed("q"):
                        desenhando = False
                        eel.setLogText("Drawing process stopped\n")
            else:
                getConfig()
                eel.prompt_alerts("Drawing process started, place the mouse over where the drawing is to be made and hit ctrl+b\nhit q to stop drawing")
                tamanhoImagemX = int(xsize)
                tamanhoImagemY = int(ysize)
                while not keyboard.is_pressed("ctrl+b") and desenhando == True:
                    pass
                if keyboard.is_pressed("ctrl+b"):
                    pyautogui.moveTo(globalConfig[8],globalConfig[9])
                    while not keyboard.is_pressed("q"):
                        receberImagem()
                    if keyboard.is_pressed("q"):
                        desenhando = False
                        eel.setLogText("Drawing process stopped\n")
        else:
            eel.setLogText("Unable to load your configs, please use the config button to continue\n")
    
def ler_file(file):
    with open(file) as f:
        return list(map(int,(str(f.read()).split(','))))

def write_file(name, array):
    f= open(name,"w");
    f.write(','.join((str(v) for v in array)));
    f.close();

def get_image_from_url(url):
    urllib.request.urlretrieve(url, "draw.png")
    img = Image.open("draw.png")
    return img

@eel.expose
def configExiste():
    if not os.path.exists('configs.log'):
        return 0
    else:
        return 1

@eel.expose
def getConfig():
    global globalConfig
    globalConfig = ler_file('configs.log')
    return globalConfig

lastRGB = "255,255,255"
def pixelar(R,G,B, canvas, ax, ay):
    global lastRGB
    if lastRGB != ("{0},{1},{2}".format(R,G,B)):
        lastRGB =  ("{0},{1},{2}".format(R,G,B))
        Hue, Saturation, Value = colorsys.rgb_to_hsv(R,G,B)
        pyautogui.click(globalConfig[2],globalConfig[3])
        pyautogui.click(globalConfig[4] + (Hue*180), globalConfig[5] - (Saturation*100))
        pyautogui.click( globalConfig[6], globalConfig[7] - (Value/2.55))
    pyautogui.click(canvas[0]+(ax*espacoPixels),canvas[1]+(ay*espacoPixels))



def screenshot():
    im = get_image_from_url(urldaimagem)
    im.thumbnail((tamanhoImagemX,tamanhoImagemY), img.ANTIALIAS)
    return im.convert(tipoConversao, palette=img.ADAPTIVE, colors=quantidadeCores).convert('RGB')

def checkPixel(imageMapPixels, x,y, tox, toy):
    if "{0}_{1}".format(x+tox, y+toy) not in imageMapPixels or  "{0}_{1}".format(x, y) not in imageMapPixels:
        return False
    return imageMapPixels["{0}_{1}".format(x, y)] != imageMapPixels["{0}_{1}".format(x+tox, y+toy)]

def mapImageToDictionary(imagem):
    imageMapPixels = {};
    imageMapColor = {}
    largura, altura = imagem.size
    for y in range(altura):
        for x in range(largura):
            pixel = imagem.getpixel((x, y))
            rgb = "%d,%d,%d" % ((pixel[0]), (pixel[1]), (pixel[2]));
            pixel = "%d_%d" % (x,y);
            if rgb not in imageMapColor.keys():
                imageMapColor[rgb] = []
            imageMapColor[rgb].append([x,y])
            imageMapPixels[pixel] = rgb
    return [imageMapPixels, imageMapColor]

def receberImagem():
    #print ('Carregando imagem ...')
    eel.setLogText('Loading Image...\n')
    global globalConfig
    canvas = list(Controller().position)
    pyautogui.click(globalConfig[0], globalConfig[1])
    #print ('Mapeando imagem ...')
    eel.setLogText('Mapping Image...\n')
    imagem = screenshot()
    (imageMapPixels, imageMapColor) = mapImageToDictionary(imagem)
    #print("Contabilizado cores: ", len(imageMapColor), "\n\nImagem processada com sucesso!")
    eel.setLogText("Counting colors: " + str(len(imageMapColor)) + "\n\nImage processed successfully!\n")
    for rgb in imageMapColor.keys():
        R, G, B = (map(int,(rgb.split(','))))
        if R > 200 and G > 200 and B > 200 and pularBranco:
            continue
        conta = -1
        while(conta < len(imageMapColor[rgb]) - 1) or keyboard.is_pressed("q"):
            conta += 1
            if not checkPixel(imageMapPixels, imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1], -1, -1):
                continue
            if not checkPixel(imageMapPixels, imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1], 1, 1):
                continue
            if not checkPixel(imageMapPixels, imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1], -1, 0):
                    continue
            if not checkPixel(imageMapPixels, imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1], 0, -1):
                    continue
            if not checkPixel(imageMapPixels, imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1], 1, 0):
                    continue
            if not checkPixel(imageMapPixels, imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1], 0, 1):
                    continue
            pixelar(R,G,B, canvas, imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1])
            del imageMapPixels["{0}_{1}" .format( imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1])]

    for rgb in imageMapColor.keys():
        R, G, B = (map(int,(rgb.split(','))))
        if R > 200 and G > 200 and B > 200 and pularBranco:
            continue
        conta = -1
        while(conta < len(imageMapColor[rgb]) - 1):
            conta += 1
            if  "{0}_{1}" .format( imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1]) not in imageMapPixels:
                continue
            pixelar(R,G,B, canvas, imageMapColor[rgb][conta][0], imageMapColor[rgb][conta][1])

    #print('Desenho completado!')
    global desenhando
    desenhando = False
    eel.setLogText('Drawing completed!\n')

@eel.expose
def setarConfig():
    screen = ImageGrab.grab()
    screen.save("./images/print.png")
    lapis = cv2.imread('./images/lapis.png', 0)
    gartic = cv2.imread('./images/print.png', 0)
    checkres = cv2.matchTemplate(gartic, lapis, cv2.TM_CCOEFF_NORMED)
    minValcheck, maxValcheck, minLoccheck, maxLoccheck = cv2.minMaxLoc(checkres)
    if maxValcheck > 0.8:
        eel.setLogText('Gartic practice mode detected, using model 1\n')
        eel.prompt_alerts("Configuration process started, open the color picker in gartic and press ctrl+x")
        while not keyboard.is_pressed("ctrl+x"):
            pass
        if keyboard.is_pressed("ctrl+x"):
            screen = ImageGrab.grab()
            screen.save("./images/print.png")
            gartic = cv2.imread('./images/print.png', 0)
            selector = cv2.imread('./images/selector.png', 0)
            paleta = cv2.imread('./images/paleta.png', 0)
            lapis = cv2.imread('./images/lapis.png', 0)

            res1 = cv2.matchTemplate(gartic, lapis, cv2.TM_CCOEFF_NORMED)
            minVal1, maxVal1, minLoc1, maxLoc1 = cv2.minMaxLoc(res1)
            startLoc1 = maxLoc1
            endLoc1 = (startLoc1[0]+lapis.shape[1], startLoc1[1]+lapis.shape[0])

            res2 = cv2.matchTemplate(gartic, selector, cv2.TM_CCOEFF_NORMED)
            minVal2, maxVal2, minLoc2, maxLoc2 = cv2.minMaxLoc(res2)
            startLoc2 = maxLoc2
            endLoc2 = (startLoc2[0]+selector.shape[1], startLoc2[1]+selector.shape[0])

            res3 = cv2.matchTemplate(gartic, paleta, cv2.TM_CCOEFF_NORMED)
            minVal3, maxVal3, minLoc3, maxLoc3 = cv2.minMaxLoc(res3)
            startLoc3 = maxLoc3
            endLoc3 = (startLoc3[0]+paleta.shape[1], startLoc3[1]+paleta.shape[0])

            pencil_res = []
            pencil_res.append(int((startLoc1[0]+endLoc1[0])/2))
            pencil_res.append(int((startLoc1[1]+endLoc1[1])/2))

            selector_res = []
            selector_res.append(startLoc2[0] + 13)
            selector_res.append(startLoc2[1] + 115)

            paleta_res = []
            paleta_res.append(int((startLoc3[0]+endLoc3[0])/2))
            paleta_res.append(int((startLoc3[1]+endLoc3[1])/2))

            bright_res = []
            bright_res.append(startLoc2[0] + 215)
            bright_res.append(startLoc2[1] + 115)

            eel.setTextBox("colorpalete", str(paleta_res[0]) + "," + str(paleta_res[1]))
            eel.setTextBox("pencil", str(pencil_res[0]) + "," + str(pencil_res[1]))
            eel.setTextBox("colorpicker", str(selector_res[0]) + "," + str(selector_res[1]))
            eel.setTextBox("brightpicker", str(bright_res[0]) + "," + str(bright_res[1]))

            res_file = []
            res_file.append(pencil_res[0])
            res_file.append(pencil_res[1])
            res_file.append(paleta_res[0])
            res_file.append(paleta_res[1])
            res_file.append(selector_res[0])
            res_file.append(selector_res[1])
            res_file.append(bright_res[0])
            res_file.append(bright_res[1])
            
            eel.prompt_alerts("Now let's set the drawing area\nPress ctrl+b in the upper left corner and then ctrl+n in the lower right corner.")
            while not keyboard.is_pressed("ctrl+b"):
                pass
            if keyboard.is_pressed("ctrl+b"):
                posicaoX = pyautogui.position()
                res_file.append(posicaoX[0])
                res_file.append(posicaoX[1])
                eel.setLogText('First point set!\n')
            while not keyboard.is_pressed("ctrl+n"):
                pass
            if keyboard.is_pressed("ctrl+n"):
                posicaoY = pyautogui.position()
                res_file.append(posicaoY[0])
                res_file.append(posicaoY[1])
                eel.setLogText('Second point set\n')
            eel.setTextBox("xsize", str(res_file[10] - res_file[8]))
            eel.setTextBox("ysize", str(res_file[11] - res_file[9]))
            write_file("configs.log", res_file) 
            eel.setLogText('Configuration process finished!\n')
    else:
        eel.setLogText('Gartic normal mode detected, using model 2\n')
        eel.prompt_alerts("Configuration process started, open the color picker in gartic and press ctrl+x")
        while not keyboard.is_pressed("ctrl+x"):
            pass
        if keyboard.is_pressed("ctrl+x"):
            screen = ImageGrab.grab()
            screen.save("./images/print.png")
            gartic = cv2.imread('./images/print.png', 0)
            selector = cv2.imread('./images/seletor2.png', 0)
            paleta = cv2.imread('./images/paleta2.png', 0)
            lapis = cv2.imread('./images/lapis2.png', 0)

            res1 = cv2.matchTemplate(gartic, lapis, cv2.TM_CCOEFF_NORMED)
            minVal1, maxVal1, minLoc1, maxLoc1 = cv2.minMaxLoc(res1)
            startLoc1 = maxLoc1
            endLoc1 = (startLoc1[0]+lapis.shape[1], startLoc1[1]+lapis.shape[0])

            res2 = cv2.matchTemplate(gartic, selector, cv2.TM_CCOEFF_NORMED)
            minVal2, maxVal2, minLoc2, maxLoc2 = cv2.minMaxLoc(res2)
            startLoc2 = maxLoc2
            endLoc2 = (startLoc2[0]+selector.shape[1], startLoc2[1]+selector.shape[0])

            res3 = cv2.matchTemplate(gartic, paleta, cv2.TM_CCOEFF_NORMED)
            minVal3, maxVal3, minLoc3, maxLoc3 = cv2.minMaxLoc(res3)
            startLoc3 = maxLoc3
            endLoc3 = (startLoc3[0]+paleta.shape[1], startLoc3[1]+paleta.shape[0])

            pencil_res = []
            pencil_res.append(int((startLoc1[0]+endLoc1[0])/2))
            pencil_res.append(int((startLoc1[1]+endLoc1[1])/2))

            selector_res = []
            selector_res.append(startLoc2[0] + 11)
            selector_res.append(startLoc2[1] + 111)

            paleta_res = []
            paleta_res.append(int((startLoc3[0]+endLoc3[0])/2))
            paleta_res.append(int((startLoc3[1]+endLoc3[1])/2))

            bright_res = []
            bright_res.append(startLoc2[0] + 214)
            bright_res.append(startLoc2[1] + 111)

            eel.setTextBox("colorpalete", str(paleta_res[0]) + "," + str(paleta_res[1]))
            eel.setTextBox("pencil", str(pencil_res[0]) + "," + str(pencil_res[1]))
            eel.setTextBox("colorpicker", str(selector_res[0]) + "," + str(selector_res[1]))
            eel.setTextBox("brightpicker", str(bright_res[0]) + "," + str(bright_res[1]))

            res_file = []
            res_file.append(pencil_res[0])
            res_file.append(pencil_res[1])
            res_file.append(paleta_res[0])
            res_file.append(paleta_res[1])
            res_file.append(selector_res[0])
            res_file.append(selector_res[1])
            res_file.append(bright_res[0])
            res_file.append(bright_res[1])
            
            eel.prompt_alerts("Now let's set the drawing area\nPress ctrl+b in the upper left corner and then ctrl+n in the lower right corner.")
            while not keyboard.is_pressed("ctrl+b"):
                pass
            if keyboard.is_pressed("ctrl+b"):
                posicaoX = pyautogui.position()
                res_file.append(posicaoX[0])
                res_file.append(posicaoX[1])
                eel.setLogText('First point set!\n')
            while not keyboard.is_pressed("ctrl+n"):
                pass
            if keyboard.is_pressed("ctrl+n"):
                posicaoY = pyautogui.position()
                res_file.append(posicaoY[0])
                res_file.append(posicaoY[1])
                eel.setLogText('Second point set\n')
            eel.setTextBox("xsize", str(res_file[10] - res_file[8]))
            eel.setTextBox("ysize", str(res_file[11] - res_file[9]))
            write_file("configs.log", res_file) 
            eel.setLogText('Configuration process finished!\n')

def grabScreen():
    screen = ImageGrab.grab()
    screen = np.array(screen)
    screen= cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
    return screen


@eel.expose
def init():
    if configExiste() == 1:
        getConfig()
        global globalConfig
        eel.setTextBox("pencil", str(globalConfig[0]) + "," + str(globalConfig[1]))
        eel.setTextBox("colorpalete", str(globalConfig[2]) + "," + str(globalConfig[3]))
        eel.setTextBox("colorpicker", str(globalConfig[4]) + "," + str(globalConfig[5]))
        eel.setTextBox("brightpicker", str(globalConfig[6]) + "," + str(globalConfig[7]))
        eel.setTextBox("xsize", str(globalConfig[8]))
        eel.setTextBox("ysize", str(globalConfig[9]))
    else:
        eel.setLogText("Unable to load your configs, please use the config button to continue")

eel.start('/index.html')