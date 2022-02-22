import urllib.request


PATT_DOMOTICZ_LIGHTS = "http://pi.home:8081/json.htm?type=command&param=switchlight&idx={}&switchcmd={}"
IDX_DOMOTICZ_LIGHTS = [87] # [89, 91]  # test: 87


def allLightsSet(status):
    """
    """
    errors = []
    for idx in IDX_DOMOTICZ_LIGHTS:
        url = PATT_DOMOTICZ_LIGHTS.format(idx, status)
        print("calling: {}".format(url))
        try:
            with urllib.request.urlopen(url) as response:
               response.read()
        except urllib.error.HTTPError as e:
            errors.append(e.code())
            print("...error: {} {}".format(e.code(), e.read()))
    return "error" if errors else "ok"


def cmdAllLightsOn(frame):
    """
    """
    frame.setDarkness(0x00)
    return allLightsSet("On")


def cmdAllLightsOff(frame):
    """
    """
    frame.setDarkness(0xe0)
    return allLightsSet("Off")


def cmdGetTriggers(frame):
    """
    A list of trigger regexes that will be matched against current time formatted as "YYYY-MM-DD hh:mm aaa"
    where aaa is the weekday as Mon, Tue, ...
    """
    return [
        "08:00",
        "22:00",
    ]

def cmdTrigger(frame, trigger, triggerTime):
    """
    If current time matches a trigger regex returned by cmdGetTriggers this method will be called.
    """
    if trigger == "08:00":
        frame.setDarkness(0x00)
    elif trigger == "22:00":
        frame.setDarkness(0xe0)
    return "ok"
