import digitalio
import time
import board
if board.board_id in ("wiznet_w55rp20_evb_pico", "wiznet_w6300_evb_pico2"):
    import wiznet
else:
    import busio

from adafruit_wiznet5k.adafruit_wiznet5k import *
import adafruit_wiznet5k.adafruit_wiznet5k_socketpool as socketpool

import adafruit_minimqtt.adafruit_minimqtt as MQTT


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



# setup for the MQTT
try:
    from secrets import secrets
except ImportError:
    print("MQTT secrets are kept in secrets.py, please add them there!")
    raise

aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]
# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    is_ssl=False,
)

# set up the feed
led_feed = secrets["aio_username"] + "/feeds/led"


# Connect to the MQTT broker
print("Connecting to MQTT broker...")
# mqtt_client.connect()
print("Connected to MQTT broker!")

led = digitalio.DigitalInOut(board.GP2)
led.direction = digitalio.Direction.OUTPUT

while True:
    ##mqtt_client.loop()  # Handle MQTT tasks
    led.value = not led.value
#    mqtt_client.publish(led_feed, int(led.value))
    print("{0} topic send {1} to broker".format(led_feed, int(led.value)))
    
    time.sleep(1)


