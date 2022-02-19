import urllib.request


PATT_DOMOTICZ_LIGHTS = "http://pi.home:8081/json.htm?type=command&param=switchlight&idx={}&switchcmd={}"
IDX_DOMOTICZ_LIGHTS = [89, 91]  # test: 87


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


def cmdAllLightsOn():
    """
    """
    return allLightsSet("On")


def cmdAllLightsOff():
    """
    """
    return allLightsSet("Off")


