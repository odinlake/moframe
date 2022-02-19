import urllib.request


LIGHTS_URLS = []


def allLightsSet(status):
    """
    """
    errors = []
    for url in LIGHTS_URLS:
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
    frame.setDarkness(0xcc)
    return allLightsSet("Off")


