import digitalio
import time
import board
import ssl
if board.board_id in ("wiznet_w55rp20_evb_pico", "wiznet_w6300_evb_pico2"):
    import wiznet
else:
    import busio

from adafruit_wiznet5k.adafruit_wiznet5k import *
import adafruit_wiznet5k.adafruit_wiznet5k_socketpool as socketpool

import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP

import adafruit_dht

MY_MAC = "00:01:02:03:04:05"
IP_ADDRESS = (192, 168, 1, 100)
SUBNET_MASK = (255, 255, 255, 0)
GATEWAY_ADDRESS = (192, 168, 1, 1)
DNS_SERVER = (8, 8, 8, 8)

ethernetRst = digitalio.DigitalInOut(board.W5K_RST)
ethernetRst.direction = digitalio.Direction.OUTPUT
 
cs = digitalio.DigitalInOut(board.W5K_CS)

if board.board_id == "wiznet_w55rp20_evb_pico":
    spi_bus = wiznet.PIO_SPI(board.W5K_SCK, MOSI=board.W5K_MOSI, MISO=board.W5K_MISO)
elif board.board_id == "wiznet_w6300_evb_pico2":
    spi_bus = wiznet.PIO_SPI(board.W5K_SCK, quad_io0=board.W5K_MOSI, quad_io1=board.W5K_MISO, quad_io2=board.W5K_IO2, quad_io3=board.W5K_IO3)
else:
    spi_bus = busio.SPI(board.W5K_SCK, MOSI=board.W5K_MOSI, MISO=board.W5K_MISO)

# Reset W5x00 first
print("reset")
ethernetRst.value = False
time.sleep(1)
ethernetRst.value = True

eth = WIZNET5K(spi_bus, cs, is_dhcp=True, mac=MY_MAC, debug=False)


pool = socketpool.SocketPool(eth)


print("Chip Version:", eth.chip)
print("MAC Address:", [hex(i) for i in eth.mac_address])
print("My IP address is:", eth.pretty_ip(eth.ip_address))



ssl_context = ssl.SSLContext()
# Initialize HTTP requests session
requests = adafruit_requests.Session(pool, ssl_context)

try:
    from secrets import secrets
except ImportError:
    print("MQTT secrets are kept in secrets.py, please add them there!")
    raise

aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]


# Initialize Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
dhtDevice = adafruit_dht.DHT22(board.GP2)
detect = True
try:
    io.send_data("detect", str(detect))
except Exception as e:
    print("Error:", e)
while True:
    if detect:
        led.value = True
        temp = dhtDevice.temperature
        print("\n\nTemperature:",temp, "°C")
        io.send_data("temperature", str(temp)+"°C")
    
    else:
        led.value = False
        print("Stop detecting temperature!")
        io.send_data("temperature", "0°C")
        
    data = io.receive_data("detect")
    detect = eval(data["value"])



    time.sleep(2)








