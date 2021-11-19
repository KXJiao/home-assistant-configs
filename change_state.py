'''
Usage: python3 change_state.py \<Device,attribute,state\> ...
The script can take as input more than one tokens.

'''

import argparse
import sys
from requests import post, get

tokens = {"light_bulb": "light",
"refrigerator": "switch",
"air_cooler": "switch",
"beacon_device": "switch",
"blood_pressure_monitor": "switch",
"bread_maker": "switch",
"button": "switch",
"electric_blanket": "switch",
"garden_sprinkler": "switch",
"gas_stove": "switch",
"glass_break_detector": "switch",
"heater": "switch",
"humidifier": "switch",
"humidity_sensor": "switch",
"illuminance_sensor": "switch",
"induction_cooktop": "switch",
"microwave_oven": "switch",
"moisture_sensor": "switch",
"oil_warmer": "switch",
"presence_sensor": "switch",
"robot_vacuum": "switch",
"smart_mirror": "switch",
"water_heater": "switch",
"water_leak_detector": "switch",
"irrigation": "switch",
"projector": "switch",
"ph_sensor": "switch",
"audio_sensor": "switch",
"door_sensor": "switch",
"fan": "fan",
"garage_door_opener": "cover",
"blinds": "cover"}

def send_post_request(device, attribute, state, template):
    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI4OTM1NDZmNzMyYTk0NTM1OGM4MTNhNmU5ZjQwNjllNCIsImlhdCI6MTYzNjU3NDk5MywiZXhwIjoxOTUxOTM0OTkzfQ.rEkIpNyaG9SKxL1TrJi1MlRSpned4dl2ei0k7-hriIk",
        "content-type": "application/json",
    }
    if (template == "light" and attribute == "switch"):
        url = ""
        if (state == "on"):
            url = "http://localhost:8123/api/services/light/turn_on"
        else:
            url = "http://localhost:8123/api/services/light/turn_off"

        data = {"entity_id": "".join(["light.", device])}

        response = post(url, json=data, headers=headers)
    elif (template == "switch"):
        url = ""
        if (state == "on" or state == "present" or state == "greater" or state == "pushed" or state == "detected" or state == "wet"):
            url = "http://localhost:8123/api/services/switch/turn_on"
        else:
            url = "http://localhost:8123/api/services/switch/turn_off"

        data = {"entity_id": "".join(["switch.", device])}

        response = post(url, json=data, headers=headers)
    elif (template == "fan" and attribute == "switch"):
        url = ""
        if (state == "on"):
            url = "http://localhost:8123/api/services/fan/turn_on"
        else:
            url = "http://localhost:8123/api/services/fan/turn_off"

        data = {"entity_id": "".join(["fan.", device])}

        response = post(url, json=data, headers=headers)
    elif (template == "cover" and attribute == "contact"):
        url = ""
        if (state == "opened"):
            url = "http://localhost:8123/api/services/cover/open_cover"
        else:
            url = "http://localhost:8123/api/services/cover/close_cover"

        data = {"entity_id": "".join(["cover.", device])}

        response = post(url, json=data, headers=headers)

    print(get("http://localhost:8123/api/states", headers=headers).text)

def process_single_token(token):
    token_list = token.replace("<", "").replace(">", "").split(",")

    device = ""
    template = ""
    if (token_list[0] == "Shades/Blinds"):
        device = "blinds"
        template = "cover"
    else:
        device = token_list[0].lower()
        template = tokens[token_list[0].lower()]

    send_post_request(device, token_list[1], token_list[2], template)

if __name__ == "__main__":
    if (len(sys.argv) > 1):
        for i in range(1, len(sys.argv)):
            token = sys.argv[i]
            if "-" in token:
                token_list = token.replace("<", "").replace(">", "").split(",")
                token_lists = []
                for i in range(len(token_list)):
                    token_lists.append(token_list[i].split("-"))
                for i in range(len(token_lists[0])):
                    ind_token = "<"
                    for j in range(len(token_lists)-1):
                        ind_token += token_lists[j][i] + ","
                    ind_token += token_lists[len(token_lists)-1][i] + ">"
                    process_single_token(ind_token)
            else:
                process_single_token(token)

