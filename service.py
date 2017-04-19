import paho.mqtt.client as mqtt
import unicornhat as unicorn
import simplejson as json

class Light:

    def __init__(self):
        self.brightness = 0
        unicorn.set_layout(unicorn.AUTO)
        unicorn.rotation(0)
        unicorn.brightness(self.brightness)
        self.width, self.height=unicorn.get_shape()
        self.r, self.g, self.b = 0, 0, 0

    def turn_off(self):
        self.r, self.g, self.b = 0, 0, 0
        self.set_brightness(0)

    def turn_on(self):
        self.r, self.g, self.b = 255, 255, 255
        self.set_brightness(1.0)

    def set_brightness(self, brightness):
        self.brightness = brightness
        unicorn.brightness(self.brightness)
        self.set_rgb_color(self.r, self.g, self.b)

    def set_rgb_color(self, r, g, b):
        self.r, self.g, self.b = r, g, b
        for y in range(self.height):
            for x in range(self.width):
                unicorn.set_pixel(x,y, r, g, b)
        unicorn.show()

light = Light()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("home/moodlight/set")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    command = json.loads(msg.payload)
    print(command)
    if command['state'] == 'ON':
        if 'brightness' in command.keys():
            light.set_brightness(command['brightness']/255)
        elif 'color' in command:
            light.set_rgb_color(command['color']['r'], command['color']['g'], command['color']['b'])
        else:
            light.turn_on()
    else:
        light.turn_off()

    # Send feedback
    client.publish("home/moodlight", msg.payload);


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("hydra.local", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
