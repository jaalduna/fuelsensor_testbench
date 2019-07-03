import paho.mqtt.client as mqtt
import random
import time
from Fuelsensor_interface import Fuelsensor_interface


class FuelMqtt(mqtt.Client):
    def __init__(self,cname):
        super(FuelMqtt, self).__init__(cname)
        #super(FuelMqtt, self).__init__()
        #self.client = mqtt.Client(client_id='seba-pub', clean_session=False)
        self.fs_interface = Fuelsensor_interface(TCP_IP='192.168.0.10',TCP_PORT=5000)
        self.connect(host='127.0.0.1', port=1883)

    def on_connect(self, mqttc, obj, flags, rc):
        print "subscribing"
        print('connected (%s)' % self.client_id)
        self.subscribe(topic='camion/sensor', qos=2)
 
    def on_message(self,client, userdata, message):
        print "msg received"
        print('------------------------------')
        print('topic: %s' % message.topic)
        print('payload: %s' % message.payload)
        print('qos: %d' % message.qos)


# client = mqtt.Client()
# client.connect('127.0.0.1',1883,60)
# client.loop_start()
# client.subscribe(topic='camion/sensor', qos=2)
# client.publish('camion/sensor','hola mundo!')
# time.sleep(1)
# client.loop_stop()
fs_mqtt = FuelMqtt(cname='seba-pub')
print 'subscribing'
#fs_mqtt.client.connect(host='127.0.0.1', port=1883)
print 'publishing'
fs_mqtt.publish("camion/sensor",'hola mundo!')
altura=(random.randint(10, 20))
while True:
    print 'publishing'
    altura=(random.randint(10, 20))
    fs_mqtt.publish("camion/sensor",altura)
    time.sleep(0.5)





# esto es un comentario para hace una prueba en git
# este es otro comentario 


