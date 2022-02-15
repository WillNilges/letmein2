import time, gc, os
import adafruit_dotstar
import board
import feathers2
import digitalio
import wifi
import socketpool
import ssl # TODO (willnilges): use SSL

from secrets import secrets

# Make sure the 2nd LDO is turned on
feathers2.enable_LDO2(True)

# Create a DotStar instance
dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5, auto_write=True)

# Say hello
print("\nLigma")

# Turn on the internal blue LED
feathers2.led_set(True)

# Connect to wifi
network = secrets['ssid'] # TODO (willnilges): HIDE THIS!
pword = secrets['password']
print("Connecting to %s" % network)
print("mac address:", "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))
wifi.radio.connect(network, pword)
print("Connected to %s!" % network)

# Set up gpio
s_stairs = digitalio.DigitalInOut(board.IO10)
level_1 = digitalio.DigitalInOut(board.IO7)
level_a = digitalio.DigitalInOut(board.IO3)
n_stairs = digitalio.DigitalInOut(board.IO1)
s_stairs.direction = digitalio.Direction.OUTPUT
level_1.direction = digitalio.Direction.OUTPUT
level_a.direction = digitalio.Direction.OUTPUT
n_stairs.direction = digitalio.Direction.OUTPUT

ack = digitalio.DigitalInOut(board.IO5)
ack.direction = digitalio.Direction.INPUT

sleep_len = 0.2

# == EM QUEUE TEE TEE ==

### Code ###

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to Adafruit IO! Listening for topic changes on %s" % onoff_feed)
    # Subscribe to all changes on the onoff_feed.
    client.subscribe(onoff_feed)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Adafruit IO!")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=secrets["port"],
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...")
mqtt_client.connect()

photocell_val = 0
while True:
    # Poll the message queue
    mqtt_client.loop()

    # Send a new message
    print("Sending photocell value: %d..." % photocell_val)
    mqtt_client.publish(photocell_feed, photocell_val)
    print("Sent!")
    photocell_val += 1
    time.sleep(5)

while True:

#    s_stairs.value = ack.value
    if ack.value:
        s_stairs.value = 1
        time.sleep(sleep_len)
        s_stairs.value = 0
        time.sleep(sleep_len)

        level_1.value = 1
        time.sleep(sleep_len)
        level_1.value = 0
        time.sleep(sleep_len)

        level_a.value = 1
        time.sleep(sleep_len)
        level_a.value = 0
        time.sleep(sleep_len)

        n_stairs.value = 1
        time.sleep(sleep_len)
        n_stairs.value = 0
        time.sleep(sleep_len)

'''
# Show available memory
print("Memory Info - gc.mem_free()")
print("---------------------------")
print("{} Bytes\n".format(gc.mem_free()))

flash = os.statvfs('/')
flash_size = flash[0] * flash[2]
flash_free = flash[0] * flash[3]
# Show flash size
print("Flash - os.statvfs('/')")
print("---------------------------")
print("Size: {} Bytes\nFree: {} Bytes\n".format(flash_size, flash_free))

print("Dotstar Time!\n")

# Create a colour wheel index int
color_index = 0

# Rainbow colours on the Dotstar
while True:
    # Get the R,G,B values of the next colour
    r,g,b = feathers2.dotstar_color_wheel( color_index )
    # Set the colour on the dotstar
    dotstar[0] = ( r, g, b, 0.1)
    # Increase the wheel index
    color_index += 1

    # If the index == 255, loop it
    if color_index == 255:
        color_index = 0
        # Invert the internal LED state every half colour cycle
        feathers2.led_blink()

    # Sleep for 15ms so the colour cycle isn't too fast
    time.sleep(0.015)
'''
