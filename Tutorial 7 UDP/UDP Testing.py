import digitalio
import time
import board
if board.board_id in ("wiznet_w55rp20_evb_pico", "wiznet_w6300_evb_pico2"):
    import wiznet
else:
    import busio
    
from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K
import adafruit_wiznet5k.adafruit_wiznet5k_socketpool as socketpool

print("Wiznet5k SimpleServer Test (DHCP)")

# Setup your network configuration below
# random MAC, later should change this value on your vendor ID
MY_MAC = "00:01:02:03:04:05"
IP_ADDRESS = (10, 0, 1, 200)       
SUBNET_MASK = (255, 255, 255, 0)   
GATEWAY_ADDRESS = (10, 0, 1, 254)  
DNS_SERVER = (8, 8, 8, 8) 

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

ethernetRst = digitalio.DigitalInOut(board.W5K_RST)
ethernetRst.direction = digitalio.Direction.OUTPUT

# For Adafruit Ethernet FeatherWing
cs = digitalio.DigitalInOut(board.W5K_CS)
# For Particle Ethernet FeatherWing
# cs = digitalio.DigitalInOut(board.D5)

spi_bus = wiznet.PIO_SPI(board.W5K_SCK, quad_io0=board.W5K_MOSI, quad_io1=board.W5K_MISO, quad_io2=board.W5K_IO2, quad_io3=board.W5K_IO3)

ethernetRst.value = False
time.sleep(1)
ethernetRst.value = True

# # Initialize ethernet interface without DHCP
# eth = WIZNET5K(spi_bus, cs, is_dhcp=False, mac=MY_MAC, debug=True)
# # Set network configuration
# eth.ifconfig = (IP_ADDRESS, SUBNET_MASK, GATEWAY_ADDRESS, DNS_SERVER)

# Initialize ethernet interface with DHCP
eth = WIZNET5K(spi_bus, cs, is_dhcp=False, mac=MY_MAC, debug=False)
eth.ifconfig = (IP_ADDRESS, SUBNET_MASK, GATEWAY_ADDRESS, DNS_SERVER)
print("Chip Version:", eth.chip)
print("MAC Address:", [hex(i) for i in eth.mac_address])
print("My IP address is:", eth.pretty_ip(eth.ip_address))

# # Initialize a socket for our server
pool = socketpool.SocketPool(eth)
server = socketpool.Socket(pool, pool.AF_INET, pool.SOCK_DGRAM)  # Allocate socket for the server

server_ip = eth.pretty_ip(eth.ip_address)  # IP address of server
port = 5000
server.bind((eth.pretty_ip(eth.ip_address),port))
print("socket connected")


while True:
    led.value = not led.value
    time.sleep(1)

    data, addr = server.recvfrom(10)
    print("data from IP:",addr[0])
    print("data from Port:",addr[1])
    if data:
        print(data.decode('utf-8'))
        server.sendto("ok".encode(),addr)  # Echo message back to client
        print("Replied with: ok")
        break


print("Done!")

