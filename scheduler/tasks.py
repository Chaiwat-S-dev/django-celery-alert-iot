from datetime import datetime
from celery import shared_task
from scheduler.models import Device
from scheduler.mqtt import MQTT, CONTROL_TOPIC
# from apps.settings import SSL_MODE
import json
# from uuid import uuid4
from scheduler.device_query_tools import InfluxClient

@shared_task
def send_control_command_start(**kwargs):
    mqtt_client = MQTT()
    devices = list(Device.objects.all())
    for device in devices:
        for location, control_settings in device.control_parameters.items():
            for setting in control_settings:
                if time_sets := setting.get("time_set", []):
                    for i, time in enumerate(time_sets):
                        start_time = datetime.strptime(time["start"], "%H:%M")
                        current_time = datetime.now()
                        if not time["started"] and current_time.hour >= start_time.hour and current_time.minute >= start_time.minute:
                            # data = {
                            #     "method": "setValue",
                            #     "TagName": setting.get("TagName", ""),
                            #     "TagValue": setting.get("TagValue", 1),
                            #     "timeStamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                            # }
                            data = {
                                "control_led": 1,
                                "timeStamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                            }
                            topic = CONTROL_TOPIC + device.mac_address
                            mqtt_client.loop_start()
                            message_info = mqtt_client.publish(topic, payload=json.dumps(data), qos=1)
                            mqtt_client.loop_stop()
                            print(f'[command start]: {message_info}')
                            time["started"] = True
                            device.save(update_fields=['control_parameters'])
                            print(f'start control command: {time["start"]}')
                            #TODO: prepare payload to check control mqtt
                            organization = "SWD"
                            payload = {
                                "org": organization,
                                "bucket": device.bucket,
                                "measurement": device.measurement,
                                "mac_address": device.mac_address,
                                "location": location,
                                "reg_field": setting['reg_check'],
                                "field": setting['reg_check']
                            }
                            # payload = {
                            #     "org": organization,
                            #     "bucket": "demo",
                            #     "measurement": "modbus",
                            #     "mac_address": "00180525FC4B",
                            #     "location": "greenhouse1",
                            #     "reg_field": "coil003",
                            #     "field": "raw_data"
                            # }
                            # check_status_control_mqtt.delay(**payload)
                            check_status_control_mqtt.apply_async(kwargs=payload, countdown=60)
                            # return "send command start to device on mqtt"
                        else:
                            continue
                            # return datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                            # return f'{start_time.hour} >= {current_time.hour} and {start_time.minute} >= {current_time.minute}'

@shared_task
def send_control_command_stop(**kwargs):
    mqtt_client = MQTT()
    devices = list(Device.objects.all())
    for device in devices:
        for location, control_settings in device.control_parameters.items():
            for setting in control_settings:
                if time_sets := setting.get("time_set", []):
                    for i, time in enumerate(time_sets):
                        stop_time = datetime.strptime(time["stop"], "%H:%M")
                        current_time = datetime.now()
                        if not time["stoped"] and current_time.hour >= stop_time.hour and current_time.minute >= stop_time.minute:
                            # data = {
                            #     "method": "setValue",
                            #     "TagName": setting.get("TagName", ""),
                            #     "TagValue": setting.get("TagValue", 0),
                            #     "timeStamp": datetime.now().strftime(""timeStamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                            data = {
                                "control_led": 0,
                                "timeStamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                            }
                            topic = CONTROL_TOPIC + device.mac_address
                            mqtt_client.loop_start()
                            message_info = mqtt_client.publish(topic, payload=json.dumps(data), qos=1)
                            mqtt_client.loop_stop()
                            print(f'[command stop]: {message_info}')
                            time["stoped"] = True
                            device.save(update_fields=['control_parameters'])
                            print(f'stop control command: {time["stop"]}')
                            #TODO: prepare payload to check control mqtt
                            organization = "SWD"
                            payload = {
                                "control_info": {
                                    "type_control": "stop",
                                    "time": time["stop"],
                                    "index_time_set": i
                                },
                                "org": organization,
                                "bucket": device.bucket,
                                "measurement": device.measurement,
                                "mac_address": device.mac_address,
                                "location": location,
                                "reg_field": setting['reg_check'],
                                "field": setting['reg_check']
                            }
                            # payload = {
                            #     "org": organization,
                            #     "bucket": "demo",
                            #     "measurement": "modbus",
                            #     "mac_address": "00180525FC4B",
                            #     "location": "greenhouse1",
                            #     "reg_field": "coil003",
                            #     "field": "raw_data"
                            # }
                            # check_status_control_mqtt.delay(**payload)
                            check_status_control_mqtt.apply_async(kwargs=payload, countdown=60)
                            # return "send command stop to device on mqtt"
                        else:
                            continue

@shared_task
def send_control_command_value(**kwargs):
    mqtt_client = MQTT()
    devices = list(Device.objects.all())
    for device in devices:
        for control_settings in device.control_parameters.values():
            for setting in control_settings:
                if (value_control := setting.get("TagValue", None)) and value_control is not None and not setting["send_value"]:
                    if offset_control := setting.get("offset_control", None):
                        equation_param = {"TagValue": value_control}
                        value_control = eval(offset_control, equation_param)
                    data = {
                        "method": "setValue",
                        "TagName": setting.get("TagName", ""),
                        "TagValue": value_control,
                        "timeStamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    }
                    topic = CONTROL_TOPIC + device.mac_address
                    mqtt_client.loop_start()
                    mqtt_client.publish(topic, payload=json.dumps(data), qos=1)
                    mqtt_client.loop_stop()
                    setting["send_value"] = True
                    device.save(update_fields=['control_parameters'])
                    print(f'task control command value: {value_control}')
                    # return "send command stop to device on mqtt"

@shared_task
def check_status_control_mqtt(**kwargs):
    # print(f'start check status control mqtt')
    control_info, org, bucket, measurement, mac_address, location, reg_field, field = kwargs.values()
    
    influx_client = InfluxClient(org=org)
    
    filter_tag = influx_client.gen_filter_tag({
        "mac_address": mac_address,
        # "group_name": location,
        # "reg_field": reg_field,
    }, "and")

    query_list = [
        f'from(bucket:"{bucket}")',
        f'range(start: -1m)',
        f'filter(fn: (r) => r._measurement == "{measurement}")',
        filter_tag,
        f'filter(fn: (r) => r._field == "{field}")',
        f'last()',
        f'drop(columns: ["_start", "_stop", "_measurement", "slave", "mac_address", "reg_field", "group_name"])'
    ]

    query = f'{" |> ".join(query_list)}'
    print(f'{query=}')
    result = influx_client.get_measurements(query)
    if not result:
        return "check state no value query"
    
    value = result.to_values(columns=['_time', '_value', '_field'])[0]
    
    type_control, time, index_time_set = control_info.values()

    if device := Device.objects.filter(mac_address=mac_address).last():
        for control_settings in device.control_parameters.values():
            for setting in control_settings:
                if time_sets := setting.get("time_set", []):
                    time = time_sets[index_time_set]
                    if type_control == "start":
                        time["started"] = True if int(value[1]) == 1 else False
                    else:
                        time["stoped"] = True if int(value[1]) == 0 else False
                    
                    device.save(update_fields=['control_parameters'])
                            
    return f'data query influx latest: {value[0].strftime("%m/%d/%Y, %H:%M:%S")}, {value[1]}, {value[2]}'
    

    
