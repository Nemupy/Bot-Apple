import time
from PIL import Image
import cv2
import os
import discord

CLIP_FRAMES = 6571

CLIP_LENGTH = 219.0666

ASCII_CHARS = ['⠀','⠄','⠆','⠖','⠶','⡶','⣩','⣪','⣫','⣾','⣿']
ASCII_CHARS.reverse()
ASCII_CHARS = ASCII_CHARS[::-1]

WIDTH = 60

TIMEOUT = 1/((int(CLIP_FRAMES/4)+1)/CLIP_LENGTH)*18

def resize(image, new_width=WIDTH):
    (old_width, old_height) = image.size
    aspect_ratio = float(old_height)/float(old_width)
    new_height = int((aspect_ratio * new_width)/2)
    new_dim = (new_width, new_height)
    new_image = image.resize(new_dim)
    return new_image

def grayscalify(image):
    return image.convert('L')

def modify(image, buckets=25):
    initial_pixels = list(image.getdata())
    new_pixels = [ASCII_CHARS[pixel_value//buckets] for pixel_value in initial_pixels]
    return ''.join(new_pixels)

def do(image, new_width=WIDTH):
    image = resize(image)
    image = grayscalify(image)
    pixels = modify(image)
    len_pixels = len(pixels)
    new_image = [pixels[index:index+int(new_width)] for index in range(0, len_pixels, int(new_width))]
    return '\n'.join(new_image)

def framecapture():
    vidObj = cv2.VideoCapture("bad_apple.mp4")
    count = 0
    success = 1
    while success:
        success, image = vidObj.read()
        cv2.imwrite("frames/frame%d.jpg" % count, image)
        count += 1

def runner(path):
    image = None
    if os.path.exists(path) == False:
        print("Start frame capture.")
        framecapture()
    else:
        try:
            print(f"Image found in {path}.")
            image = Image.open(path)
        except Exception:
            print(f"Image not found in {path}.")
            return
        image = do(image)
        return image

frames = []

for i in range(0, int(CLIP_FRAMES/4)+1):
    path = "frames/frame"+str(i*4)+".jpg"
    frames.append(runner(path))

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.content.startswith('!bad apple'):
        oldTimestamp = time.time()
        i = 0
        while i < len(frames)-1:
            disp = False
            while not disp:
                newTimestamp = time.time()
                if (newTimestamp - oldTimestamp) >= TIMEOUT:
                    await message.channel.send(frames[int(i)])
                    newTimestamp = time.time()
                    i += (newTimestamp - oldTimestamp)/TIMEOUT
                    oldTimestamp = newTimestamp
                    disp = True

client.run('TOKEN')
