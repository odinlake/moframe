import urllib.request


PATT_DOMOTICZ_LIGHTS = "http://pi.home:8081/json.htm?type=command&param=switchlight&idx={}&switchcmd={}"
IDX_DOMOTICZ_LIGHTS = {
    "alcoves": 89,
    "sofa": 91,
    "test": 87,
}


def cmdGetDevices(frame):
    """
    A list of device names that will be controllable.
    """
    return [
        "ALL",
        "alcoves",
        "sofa",
    ]

def cmdDeviceSet(frame, name, status):
    """
    """
    print(name, status)
    errors = []
    if name == "ALL":
        frame.setDarkness(0x00 if status == "On" else 0xe0)
        for name2 in cmdGetDevices(frame):
            if name2 != "ALL":
                res = cmdDeviceSet(frame, name2, status)
                if res == "error":
                    errors.append("unknown error")
    else:
        idx = IDX_DOMOTICZ_LIGHTS[name]
        url = PATT_DOMOTICZ_LIGHTS.format(idx, status)
        print("calling: {}".format(url))
        try:
            with urllib.request.urlopen(url) as response:
                response.read()
        except urllib.error.HTTPError as e:
            errors.append(e.code())
            print("...error: {} {}".format(e.code(), e.read()))
    return "error" if errors else "ok"


def cmdGetTriggers(frame):
    """
    A list of trigger regexes that will be matched against current time formatted as "YYYY-MM-DD hh:mm aaa"
    where aaa is the weekday as Mon, Tue, ...
    """
    return [
        "07:00",
        "09:00",
        "22:00",
        "00:00",
    ]

def cmdTrigger(frame, trigger, triggerTime):
    """
    If current time matches a trigger regex returned by cmdGetTriggers this method will be called.
    """
    if trigger == "07:00":
        frame.setDarkness(0x80)
    elif trigger == "09:00":
        return cmdDeviceSet(frame,  "ALL", "On")
    elif trigger == "22:00":
        frame.setDarkness(0x80)
    elif trigger == "00:00":
        return cmdDeviceSet(frame,  "ALL", "Off")
    return "ok"
