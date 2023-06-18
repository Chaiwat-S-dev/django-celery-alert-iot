# ---------- Python's Libraries ---------------------------------------------------------------------------------------
import ssl
from paho.mqtt import client as mqtt_client

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------

# ---------- Created Tools --------------------------------------------------------------------------------------------
from apps.settings import MQTT_BROKER_HOST, BROKER_PORT, SSL_MODE, \
MQTT_CA_PATH, MQTT_CERT_PATH, MQTT_KEY_PATH, MQTT_AWS_HOST, MQTT_AWS_PORT

DEVICE_TOPIC = "iot/device"
ALERT_TOPIC = "iot/alert_setting"
CONTROL_TOPIC = "control/"


class MQTT(mqtt_client.Client):
    host = MQTT_AWS_HOST if SSL_MODE else MQTT_BROKER_HOST
    port = MQTT_AWS_PORT if SSL_MODE else BROKER_PORT
    topic = [(DEVICE_TOPIC, 0), ]
    client_id = "iot_serivce"
    username = ""
    password = ""
    keepalive=120
    
    def __init__(self, host=host, port=port, listen_topic=[], ssl_connect=SSL_MODE,
                client_id=client_id, username="", password="", keepalive=keepalive, setups=''):

        self.host, self.port, self.client_id = host, port, client_id
        self.client_id, self.username, self.password = client_id, username, password
        self.listen_topic = listen_topic
        self.keepalive=keepalive

        if setups:
            self.host = MQTT_BROKER_HOST
            self.port = BROKER_PORT

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQ Broker")
                self.subscribe(self.listen_topic)
            else:
                print("Fail to connect mq")
        
        super().__init__(client_id)
        self.username_pw_set(username, password)
        self.on_connect = on_connect
        
        if ssl_connect and not setups:
            self.tls_set(ca_certs=MQTT_CA_PATH, certfile=MQTT_CERT_PATH, keyfile=MQTT_KEY_PATH, 
                        cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, 
                        ciphers=None)

        self.connect(self.host, self.port, self.keepalive)

