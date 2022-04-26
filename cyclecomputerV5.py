###############################################################
# Cycle Computer using pi pico and SSD1306 OLED I2C Display
# maker pi pico dev board.
# Dave Gunning Nov 2021
#
# I2C display to pi pico pins: VCC 3.3v, SDA - GP4, SCL - GP5.
# Input from cycle wheel reed switch to GP1. Switch debounce using CR network.
# Reed switch closes on each wheel rotation and discharges 1uF, causing logic 0 pulse on GP1.
#
# 3.3v---1k----1k------>GP1
#         |     |
#      reed-sw  1uF
#         |     |
#        GND   GND
#
# oled driver examples at Pico Micropython repository:
# https://github.com/raspberrypi/pico-micropython-examples/tree/master/i2c/1306oled
###############################################################
#

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf,sys,utime
#import imgfile

WHEEL_DIA= 27
WHEEL_CIRC = WHEEL_DIA*3.142
INCHES_MILE = 63360

samples = 5 # number of one second samples in sample window
totalDistance = 0
pulses = 0

led = machine.Pin(25,machine.Pin.OUT)
buzzer = machine.Pin(18,machine.Pin.OUT)
button = machine.Pin(1,machine.Pin.IN,machine.Pin.PULL_DOWN)


def button_handler(pin):
    # interupts detect GP1 0>1 pulses via button or reed-switch
    global pulses
    #button.irq(trigger=none)
    #state = machine.disable_irq()
    utime.sleep(0.1) #debounce
    pulses += 1
    #machine.enable_irq(state)
    button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)

def setupDisplay():
    pix_res_x  = 128 # SSD1306 horizontal resolution
    pix_res_y = 64   # SSD1306 vertical resolution

    i2c_dev = I2C(0,scl=Pin(5),sda=Pin(4),freq=200000)  # start I2C on I2C1 (GPIO 5/4)
    i2c_addr = [hex(ii) for ii in i2c_dev.scan()] # get I2C address in hex format
    if i2c_addr==[]:
        print('No I2C Display Found') 
        sys.exit() # exit routine if no dev found
    else:
        print("I2C Address      : {}".format(i2c_addr[0])) # I2C device address
        print("I2C Configuration: {}".format(i2c_dev)) # print I2C params


    oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev) # oled controller

    # Raspberry Pi logo as 32x32 bytearray
    buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

    # Load the raspberry pi logo into the framebuffer (the image is 32x32)
    fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)

    # Clear the oled display in case it has junk on it.
    oled.fill(0)

    # Blit the image from the framebuffer to the oled display
    oled.blit(fb, 40, 30)
    
    return(oled)



    
#------------------ main code -------------
 
oled = setupDisplay() 
oled.show()

button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)

while(1):
    utime.sleep(0) 
    oled.fill(0)
    oled.text("CYCLE COMP V5",5,20)
    
    # wait a while to allow wheel rotations to be counted via GP1 interrupts
    # blink led and buzzer at the end of each second
    for sample in range(samples):
        if True:              
            led.value(1)
            buzzer.value(1)
            utime.sleep(0.01)
            buzzer.value(0)
            utime.sleep(0.49)
            led.value(0)
            utime.sleep(0.49)
    print("final sample", sample)
    #irq_state = pyb.disable_irq() # Start of critical section
    
    #maths
    pps = pulses/samples #
    InchesPerHour = pps*3600* WHEEL_CIRC
    speed = InchesPerHour/INCHES_MILE #mph
    totalDistance =   totalDistance + (speed/3600)*samples #miles per second * number of seconds
   
    #oled.text("pps",5,30)
    #oled.text(str(pps),40,30)
    oled.text("MPH",10,40)
    oled.text(str(round(speed,2)),50,40)
    oled.text("DIST",10,50)
    oled.text(str(round(totalDistance,2)),50,50)
    
    oled.show()
    
    if pulses > 0:
        print ("samples, pulses, pps, speed, totalDistance",samples,pulses,pps,speed,totalDistance)
        pulses = 0
        
    #pyb.enable_irq(irq_state) # End of critical section
    
    #buzzer.value(1)
    utime.sleep(0.1)
    #buzzer.value(0)
    
    