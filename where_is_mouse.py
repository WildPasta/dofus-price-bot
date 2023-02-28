import pynput
from pynput.mouse import Button
from time import sleep

mouse = pynput.mouse.Controller()


while 1: 
    print(mouse.position)
    sleep(0.5)