
import pprint as pp
import time
import spidev
from   gpiozero import LED
#############################################################################
def cmds():
    """List of Table 1 commands for ST7789V chip."""

    commands = [
    # (ID, NAME,        W, R, "DESC")
    (0x01, 'SWRESET',   0, 0, 'Software Reset'),
    (0x04, 'RDDID',     0, 4, 'Read Display ID'),
    (0x05, 'RDDST',     0, 5, 'Read Display Status'),
    (0x0A, 'RDDPM',     0, 2, 'Read Display Power Mode'),
    (0x0B, 'RDDMADCTL', 0, 2, 'Read Display MADCTL'),
    (0x0C, 'RDDCOLMOD', 0, 2, 'Read Display Pixel Format'),
    (0x0D, 'RDDIM',     0, 2, 'Read Display Image Mode'),
    (0x0E, 'RDDSM',     0, 2, 'Read Display Signal Mode'),
    (0x0F, 'RDDSDR',    0, 2, 'Read Display Self-Diagnostic Result'),
    (0x10, 'SLPIN',     0, 0, 'Sleep in'),                       # Default
    (0x11, 'SLPOUT',    0, 0, 'Sleep out'),
    (0x12, 'PTLON',     0, 0, 'Partial Display Mode On'),        # See 30h
    (0x13, 'NORON',     0, 0, 'Normal Display Mode On'),         # Default
    (0x20, 'INVOFF',    0, 0, 'Display Inversion Off'),          # Default
    (0x21, 'INVON',     0, 0, 'Display Inversion On'),
    (0x26, 'GAMSET',    1, 0, 'Gamma Set'),
    (0x28, 'DISPOFF',   0, 0, 'Display Off'),                    # Default
    (0x29, 'DISPON',    0, 0, 'Display On'),
    (0x2A, 'CASET',     4, 0, 'Column Address Set'),             # uint16 * 2
    (0x2B, 'RASET',     4, 0, 'Row Address Set'),                # uint16 * 2
    (0x2C, 'RAMWR',    -1, 0, 'Memory Write'),                   # Not cleared on SW/HW reset, resets col/row
    (0x2E, 'RAWRD',     0,-1, 'Memory Read'),                    # Resets col/row registers, fixed 18-bit
    (0x30, 'PTLAR',     4, 0, 'Partial Area'),                   # uint16 * 2
    (0x33, 'VSCRDEF',   6, 0, 'Vertical Scrolling Definition'),  # uint16 * 3
    (0x34, 'TEOFF',     0, 0, 'Tearing Effect Line OFF'),        # Default
    (0x35, 'TEON',      1, 0, 'Tearing Effect Line On'),
    (0x36, 'MADCTL',    1, 0, 'Memory Data Access Control'),
    (0x37, 'VSCSAD',    2, 0, 'Vertical Scroll Start Address of RAM'),
    (0x38, 'IDMOFF',    0, 0, 'Idle Mode OFF'),                  # Default
    (0x39, 'IDMON',     0, 0, 'Idle Mode ON'),                   # Reduced to 8 colors (RGB-111)
    (0x3A, 'COLMOD',    1, 0, 'Interface Pixel Format'),         # Default 66h (RGB-666)
    (0x3C, 'WRMEMC',   -1, 0, 'Write Memory Continue'),          # After 2Ch
    (0x3E, 'RDMEMC',    0,-1, 'Read Memory Continue'),           # After 2Eh
    (0x44, 'STE',       2, 0, 'Set Tear Scanline'),
    (0x45, 'GSCAN',     0, 3, 'Get Scanline'),
    (0x51, 'WRDISBV',   1, 0, 'Write Display Brightness'),
    (0x52, 'RDDISBV',   0, 2, 'Read Display Brightness Value'),
    (0x53, 'WRCTRLD',   1, 0, 'Write CTRL Display'),
    (0x54, 'RDCTRLD',   0, 2, 'Read CTRL Value Display'),
    (0x55, 'WRCACE',    1, 0, 'Write Content Adaptive Bright Ctrl and Color Enhance'),
    (0x56, 'RDCABC',    0, 2, 'Read Content Adaptive Brightness Control'),
    (0x5E, 'WRCACBCMB', 1, 0, 'Write CABC Minimum Brightness'),
    (0x5F, 'RDCABCMB',  0, 2, 'Read CABC Minimum Brightness'),
    (0x68, 'RDABCSDR',  0, 2, 'Read Automatic Bright Ctrl Self-Diagnotstic Result'),
    (0xDA, 'RDID1',     0, 2, 'Read ID1'),
    (0xDB, 'RDID2',     0, 2, 'Read ID2'),
    (0xDC, 'RDID3',     0, 2, 'Read ID3'),
    ]
    
    by_name = {
        name: {'id': id, 'wrx': wrx, 'rdx': rdx, 'desc': desc}
        for id, name, wrx, rdx, desc in commands
    }
    
    by_id = {
        id: {'name': name, 'wrx': wrx, 'rdx': rdx, 'desc': desc}
        for id, name, wrx, rdx, desc in commands
    }
    
    print()
    print('{:>10} {:>4} {:>4} {:>4}  {}'.format('name', 'id', 'wrx', 'rdx', 'description'))
    print('{:>10} {:>4} {:>4} {:>4}  {}'.format('----', '--', '---', '---', '-----------'))
    for k,v in by_name.items():
        if 'Read' not in v['desc'] and 'Get' not in v['desc']:
            print('{:>10} {:>4} {:>4} {:>4}  {}'.format(k,v['id'],v['wrx'],v['rdx'],v['desc']))
    print()
    return ['done1']
#############################################################################

"""
write a python script to write a single pixel to the waveshare 
320 x 240 spi display that uses the st7789v controller using 
gpiozero on a raspberry pi 4 using spidev writebytes function


Required Libraries:

spidev: For SPI communication.
gpiozero: For controlling GPIO pins such as backlight (if applicable).

Hardware Setup:

CS   (Chip Select):         GPIO 8 (CE0)
SCLK (Clock):               GPIO 11 (SCK)
MOSI (Master Out Slave In): GPIO 10 (MOSI)
Backlight (optional):       GPIO 18 (for controlling the backlight)

Steps:

Set Up SPI: 
Configure SPI settings using spidev.

Send Commands and Data:
Use writebytes() to send commands and pixel data to the display.

Pixel Format:
Send the pixel data in the RGB565 format (16-bit color) to set a single pixel.


Explanation:

SPI Setup:
The script opens the SPI interface using spidev.SpiDev(). spi.open(0, 0)
opens SPI bus 0, device 0 (CE0). You can adjust the speed and mode based on
your requirements. spi.max_speed_hz = 20000000 sets the SPI speed to 20 MHz,
and spi.mode = 0b00 sets SPI mode 0 (CPOL = 0, CPHA = 0).

Sending Commands and Data:

The send_command(command) function sends a command to the display using
spi.writebytes([0x00, command]), where 0x00 indicates command mode. A small
delay (time.sleep(0.001)) is added after each command/data transmission to
ensure correct timing.

The send_data(data) function sends the data to the display using
spi.writebytes([0x01, data]), where 0x01 indicates data mode.

Display Initialization:

The init_display() function sends a series of initialization commands to the
display. These include commands for setting the memory access control, pixel
format (RGB565), and enabling the display. The reset and sleep-out commands
ensure that the display is properly initialized.

Setting a Pixel:

The set_pixel(x, y, color) function sets a single pixel at the coordinates
(x, y) with the specified color. The color is provided in the RGB888 format
(24-bit), and the function converts it to the RGB565 format (16-bit).
The RGB565 value is then split into two bytes (high and low) and sent to
the display.

The column and row addresses are set using commands 0x2A and 0x2B,
and the pixel data is written with the 0x2C command.

Backlight Control:

The backlight is controlled using the gpiozero.LED object. You can turn it on
or off as needed, depending on your hardware setup.

Notes:

The spi.writebytes() function is used to send both commands and data to the
display, making the communication more efficient than manually toggling the GPIO pins.
The display uses the RGB565 color format, so the input color is converted from
RGB888 (24-bit) to RGB565 (16-bit) before being sent to the display.
If you're working with higher-performance applications, consider optimizing your
approach by using more advanced libraries like luma.lcd or Pillow for handling graphics.

"""
# Function to send a command to the display
def send_command(command):
    spi.writebytes([0x00, command])  # Command mode
    time.sleep(0.001)  # Small delay to ensure proper timing

# Function to send data to the display
def send_data(data):
    spi.writebytes([0x01, data])  # Data mode
    time.sleep(0.001)  # Small delay to ensure proper timing

# Function to initialize the display
def init_display():
    # Reset sequence (this can be done via GPIO if needed, otherwise assume manual reset)
    send_command(0x01)  # Software reset
    time.sleep(0.1)

    send_command(0x11)  # Sleep out
    time.sleep(0.1)

    send_command(0x36)  # Memory Data Access Control
    send_data(0x00)  # Set orientation (0x00 = normal orientation)

    send_command(0x3A)  # Interface Pixel Format
    send_data(0x05)  # RGB565 format (16-bit)

    send_command(0x29)  # Display on

    print("Display initialized")

# Function to set a single pixel at (x, y) with a specified color
def set_pixel(x, y, color):
    # Set column address (X-axis)
    send_command(0x2A)  # Column address set
    send_data(x >> 8)  # High byte of X
    send_data(x & 0xFF)  # Low byte of X

    # Set row address (Y-axis)
    send_command(0x2B)  # Row address set
    send_data(y >> 8)  # High byte of Y
    send_data(y & 0xFF)  # Low byte of Y

    # Memory write command (to write the pixel data)
    send_command(0x2C)

    # Convert the RGB color to RGB565 format (16-bit color)
    r = (color >> 16) & 0xF8
    g = (color >> 8) & 0xFC
    b = color & 0xF8
    rgb565 = (r << 8) | (g << 3) | (b >> 3)

    # Send the RGB565 data (high byte and low byte)
    send_data(rgb565 >> 8)  # High byte
    send_data(rgb565 & 0xFF)  # Low byte

    print(f"Pixel set at ({x}, {y}) with color {color:#06x}")

spi = spidev.SpiDev()
def sr():

    # SPI setup using spidev
    spi.open(0, 0)  # Open SPI bus 0, device 0 (CE0)
    spi.max_speed_hz = 20000000  # 20 MHz (adjust as needed)
    spi.mode = 0b00 # SPI mode 0

    # Optional backlight control using gpiozero
    backlight = LED(18)  # Assuming backlight is controlled via GPIO 18

    backlight.on()  # Turn on the backlight (optional)
    init_display()  # Initialize the display

    # Set a single pixel at (50, 50) to red (0xFF0000)
    set_pixel(50, 50, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 51, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 52, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 53, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 54, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 55, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 56, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 57, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 58, 0xFF0000)  # Red color (RGB format)
    set_pixel(50, 59, 0xFF0000)  # Red color (RGB format)

    time.sleep(1)  # Wait for 1 second to observe the pixel change

    # Optionally, you can turn off the backlight here if needed
    # backlight.off()

    return ['done2']

