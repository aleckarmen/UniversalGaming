#import board support libraries, including HID.
#test
import board
import digitalio
import analogio
import usb_hid
#test
#Libraries for the OLED Display
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import terminalio
import displayio
import busio

import supervisor

import functions

from time import sleep

#Libraries for communicating as a Keyboard device.
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

#library for communicating as a gamepad
from hid_gamepad import Gamepad

from adafruit_hid.mouse import Mouse
mouse = Mouse(usb_hid.devices)

from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl

mediacontrol = ConsumerControl(usb_hid.devices)

keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)
gp = Gamepad(usb_hid.devices)

#Create a collection of GPIO pins that represent the buttons.
#This includes the digital pins for the Directional Pad
#They can be used as regular buttons if using the analog inputs instead
#gamepad buttons and their functions()by index for example, 0th element is

#board pin indexes in the gamepad_x array shown below
button_pins = (
#board.A1,board.A0,
board.D25,board.D24,    #A1 = 0, A2 = 1
board.MOSI,board.SCK,   #MOSI = 2, SCK = 3  
board.RX,board.TX,      #RX = 4, TX = 5
board.D4,board.D5,      #D4 = 6, D5 = 7
board.D6,board.D9,      #D6 = 8, D8 = 9
board.D10,board.D11,    #D10 = 10, D11 = 11
board.D12,board.D13,     #D12 = 12, D13 = 13
board.MISO
)

def update_oled(mode,joystickmode):
    splash = displayio.Group()
    display.show(splash)

    # Draw a label

    text = "Mode : " + str(mode)
    text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=3, y=3
    )
    splash.append(text_area)
    text = mode_names[int(mode)]
    text_area = label.Label(
        terminalio.FONT, text=text, color=0xFFFF0F, x=3, y=23
    )
    
    splash.append(text_area)
    text = joystickmode
    text_area = label.Label(
        terminalio.FONT, text=text, color=0xFFFFFF, x=3, y=43
    )
    splash.append(text_area)



def serial_read():
    if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        print("value", value)
        try:
          return int(value)
        except:
            #print("Value cant be turned into an int")
            return value


def range_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Map the buttons to button numbers on the Gamepad
# gamepad_buttons[i] will send that button number when buttons[i]
# x's mean i dont have 
# is pushed.                        #x  x 
gamepad_buttons0 =                  (2, 4, 3, 3, 6, 7, 13, 16, 13, 15, 8, 5, 10, 9, 8)
gamepad_buttons_for_demo =          (2, 4, 3, 3, 6, 7, 13, 16, 13, 15, 14, 5, 14, 15, 8)
gamepad_buttons_layout_default =    (1, 2, 3, 4, 5, 8, 13,9, 7,10,12, 6, 9, 11, 14, 15)
gamepad_buttons_layout2 =           (10, 9, 6, 5, 1, 2, 3, 4, 7, 8, 11, 12, 13, 14, 15)


#Keyboard Mode Button Definitions
keyboard_buttons = {0 : Keycode.UP_ARROW, 1 : Keycode.LEFT_ARROW, 2 : Keycode.DOWN_ARROW, 3 : Keycode.RIGHT_ARROW,
                  4 : Keycode.LEFT_CONTROL, 5 : Keycode.SPACE, 6 : Keycode.W, 7 : Keycode.ENTER, 8 : Keycode.LEFT_ALT
                    , 9 : Keycode.ENTER, 10 : Keycode.ENTER, 11 : Keycode.ENTER, 12 : Keycode.ENTER, 13 : Keycode.ENTER
                    , 14 : Keycode.ENTER, 15 : Keycode.ENTER}

#FPS Mode Button Definitions
fps_buttons = {0 : Keycode.W, 1 : Keycode.A, 2 : Keycode.S, 3 : Keycode.D,
                  4 : Keycode.LEFT_CONTROL, 5 : Keycode.SPACE, 6 : Keycode.LEFT_ALT, 7 : Keycode.ENTER,
               8 : Keycode.ENTER, 9 : Keycode.ENTER, 10 : Keycode.ENTER, 11 : Keycode.ENTER, 12 : Keycode.ENTER
               , 13 : Keycode.ENTER, 14 : Keycode.ENTER, 15 : Keycode.ENTER}

#List of defind mode names
mode_names = {1 : 'Gamepad', 2 : 'Keyboard', 3 : 'FPS', 4 : "Mouse", 5 : "Multimedia"}

#Set Default Mode To 1
mode = 1
#Define OLED Parameters
WIDTH = 128
HEIGHT = 64
BORDER = 5

buttons = [digitalio.DigitalInOut(pin) for pin in button_pins]

#modeChangeButton = digitalio.DigitalInOut(board.RX)
#modeChangeButton.direction = digitalio.Direction.INPUT
#modeChangeButton.pull = digitalio.Pull.UP

#layoutChangeButton = digitalio.DigitalInOut(board.TX)
#layoutChangeButton.direction = digitalio.Direction.INPUT
#layoutChangeButton.pull = digitalio.Pull.UP

#JoystickChangeButton = digitalio.DigitalInOut(board.MISO)
#JoystickChangeButton.direction = digitalio.Direction.INPUT
#JoystickChangeButton.pull = digitalio.Pull.UP

#Initialize The Buttons
for button in buttons:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    
# Setup for Analog Joystick as X and Y
ax = analogio.AnalogIn(board.A3)
ay = analogio.AnalogIn(board.A2)

displayio.release_displays()


# Use for I2C for display
i2c = busio.I2C(board.SCL, board.SDA)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

#Equivalent of Arduino's map() function
def range_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
  

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

#Make the display context.
splash = displayio.Group()
display.show(splash)

# Draw a label

text = "Mode : " + str(mode)
text_area = label.Label(
terminalio.FONT, text=text, color=0xFFFFFF, x=3, y=3
)
splash.append(text_area)
text = mode_names[mode]
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=3, y=23
)
splash.append(text_area)

def debounce():
    sleep(0.2)

#defaults
mode = 1
count = 0
serialRead = 1
oldmode = 6
oldLayoutButtonValue = True
layout_num = 1
joystickmode = "analog"
oldJoystickMode = "analog"
gamepad_buttons = gamepad_buttons0

update_oled(mode,joystickmode)

print("Hello! Universal Gaming Controller Now Active.")
print("Joystick Mode: ",joystickmode, ". Button Layout: Default.")

#AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH

while True:
    oldmode = mode
    #check to see if layout switch putton is pressed.
    
    if supervisor.runtime.serial_bytes_available: #if user typed a command and pressed enter...
        serialRead = serial_read()
        if type(serialRead) == type(2):
            if mode >= 1 and mode <= 5:
                mode = serialRead
                if mode != oldmode or joystickmode != oldJoystickMode:
                    update_oled(mode,joystickmode)
            else:
                mode = mode
        elif type(serialRead) == type("hi"): #if serial stuff is not a number:.
            if serialRead == "Print Mode":
                print(mode_names[mode])
            elif serialRead == "layout2":
                gamepad_buttons = "gamepad_buttons1"
                print("gamepad buttons changed  to buttons1 via uart... now they are:", gamepad_buttons)
            elif serialRead == "layout_default":
                gamepad_buttons = gamepad_buttons_layout_default
                print("gamepad buttons changed  to derfault via uart... now they are:", gamepad_buttons)
            elif serial_read == "switchAnalogMode":
                if joystickmode == "analog":
                    joystickmode = "digital"
                else:
                    joystickmode = "analog"
                debounce()
                print("joystick mode is now:", joystickmode)
                oldJoystickMode = joystickmode
                update_oled(mode,joystickmode)
        
    if (count >= 1000):
        count = 0
        #print("heartbeat")
    count = count +1
    
    
    if mode == 1: #when in gamepad mode...

        
        if joystickmode == "digital":
            setx = 0
            sety = 0
            #Not keyboard presses for directional
            #So check them seperately first
            if not buttons[11].value: #if button is pressed aka connected to ground aka 0
                sety = -127
            if not buttons[12].value:
                sety = 127
            if not buttons[13].value:
                setx = -127
            if not buttons[14].value:
                setx = 127
            #Set Joystick movements
            gp.move_joysticks(
                x=setx,
                y=sety,
            )
            
            # Go through all the button definitions, and
            # press or release as appropriate
            for i, button in enumerate(buttons):
                if i < 12: #Skip the last 4, since they're the directionals
                    gamepad_button_num = gamepad_buttons[i] # Minus 4 to ignore directionals
                    if button.value:
                        gp.release_buttons(gamepad_button_num)
                    else:
                        print("button",i,"=",button.value, "was pressed")
                        gp.press_buttons(gamepad_button_num)
        
        else:
            gp.move_joysticks(
                gp.move_joysticks(
            x=range_map(ax.value, 0, 65535, -127, 127),
            y=range_map(ay.value, 0, 65535, 127, -127),
        )
            )
            
            for i, button in enumerate(buttons):
                gamepad_button_num = gamepad_buttons[i]
                if button.value:
                    
                    gp.release_buttons(gamepad_button_num)
                else:
                    print("button",i,"=",button.value, "was pressed")
                    gp.press_buttons(gamepad_button_num)
        
    if mode == 2: # Keyboard Mode
            
        for i, button in enumerate(buttons):
            #print("button",i,"=",button.value) #optional print to show which game buttons are pushed
            if button.value:
                keyboard.release(keyboard_buttons[i])
            else:
                keyboard.press(keyboard_buttons[i]) 
    #FPS Mode
    if mode == 3:
        for i, button in enumerate(buttons):
            gamepad_button_num = gamepad_buttons[i]
            if button.value:
                keyboard.release(fps_buttons[i])
            else:
                keyboard.press(fps_buttons[i])
    #Mouse mode            
    if mode == 4:
        if not buttons[11].value:
            mouse.move(y=-4)
        if not buttons[12].value:
            mouse.move(y=4)
        if not buttons[13].value:
            mouse.move(x=-4)
        if not buttons[14].value:
            mouse.move(x=4)
        if not buttons[4].value:
            mouse.click(Mouse.LEFT_BUTTON)
            debounce()
        if not buttons[5].value:
            mouse.click(Mouse.RIGHT_BUTTON)
            debounce()

    if mode == 5: #replaced 5 bc i dont want it to be 5 rn. dont have enough buttos assigned for 5
        if not buttons[0].value:
            mediacontrol.send(ConsumerControlCode.VOLUME_INCREMENT)
            debounce()
        if not buttons[2].value:
            mediacontrol.send(ConsumerControlCode.VOLUME_DECREMENT)
            debounce()
        if not buttons[1].value:
            mediacontrol.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
            debounce()
        if not buttons[3].value:
            mediacontrol.send(ConsumerControlCode.SCAN_NEXT_TRACK)
            debounce()
        if not buttons[4].value:
            mediacontrol.send(ConsumerControlCode.PLAY_PAUSE)
            debounce()
        if not buttons[5].value:
            mediacontrol.send(ConsumerControlCode.STOP)
            debounce()
        if not buttons[9].value:
            mediacontrol.send(ConsumerControlCode.MUTE)
            debounce()