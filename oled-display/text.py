import time
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont

# Initialize the OLED screen
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

# Clear the display
device.clear()

# Display text
text = "Hey, I am K9!"

# Create a function to display text on the OLED screen
def display_text1(text):
    with canvas(device) as draw:
        # Set the font size to be twice as large
        font_size = 34
        font = ImageFont.truetype("/home/pi/K9/font2.ttf", font_size)
        
        # Calculate the position to center the text
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        x = (device.width - text_width) // 2
        y = (device.height - text_height) // 2
        
        draw.text((x, y), text, font=font, fill="white")
def display_text2(text):
    with canvas(device) as draw:
        # Set the font size to be twice as large
        font_size = 20
        font = ImageFont.truetype("/home/pi/K9/font.ttf", font_size)
        
        # Calculate the position to center the text
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        x = (device.width - text_width) // 2
        y = (device.height - text_height) // 2
        
        draw.text((x, y), text, font=font, fill="white")
# Call the function to display the text
display_text1(text)
time.sleep(3)
display_text1("OR ...")
time.sleep(2)
display_text2(text)
time.sleep(3)


# Update the display
device.show()

# Wait for 5 seconds

# Clear the display
device.clear()
