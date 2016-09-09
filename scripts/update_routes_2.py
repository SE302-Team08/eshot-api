import logging, requests, re

from bs4 import BeautifulSoup
from random import choice
from django.conf import settings

from . import colorize
from izmir import models

logger = logging.getLogger(__name__)

# My Solution: http://stackoverflow.com/a/38362458/2926992
def equalizer(data):
    largest_length = 0 # To define the largest length

    for l in data:
        if len(l) > largest_length:
            largest_length = len(l) # Will define the largest length in data.

    for i, l in enumerate(data):
        if len(l) < largest_length:
            remainder = largest_length - len(l) # Difference of length of particular list and largest length
            data[i].extend([None for i in range(remainder)]) # Add None through the largest length limit

    return data

def midnight_formatter(time_str):
    """
    Used for formatting 24 to 00 as hours.
    Will be used with map.
    :param time_str:
    :return:
    """

    if time_str == None:
        return None

    if time_str[:2] == "24":
        time_str_list = list(time_str)
        time_str_list[0] = "0"
        time_str_list[1] = "0"
        time_str = "".join(time_str_list)

    return time_str

def run():
    logger.info("Initializing Route Updating Script")
    qc = 0

    logger.info("Requestion main URL to get route list.")
    res = requests.get("http://www.eshot.gov.tr/tr/UlasimSaatleri/288")
    r_elms = BeautifulSoup(res.content, "html.parser")\
        .find("select", {"class":"chosen-select"})\
        .find_all("option")

    # Requesting All Routes
    logger.info("Starting to request individual route elements.")
    for i, elm in enumerate(r_elms):
        # Initial Information
        r_dict = {
            "code": int(elm["value"])
        }

        term_find = re.findall(": (.+)[ ]*-[ ]*(.+)", elm.getText())
        terminals = [i.strip() for i in term_find[0]] # Formatting Terminal Strings, Might Have White-Space
        r_dict["terminals"] = terminals

        logger.info("[{}/{}]: {}".format(
            str(i),
            str(len(r_elms) - 1),
            elm["value"]
        ))

        stops_forwards = list()
        stops_backwards = list()

        # Forward Information
        logger.debug("Getting forward information for {}".format(str(r_dict["code"])))

        res = requests.post(
            "http://www.eshot.gov.tr/tr/UlasimSaatleri/288",
            data={
                "hatId": str(r_dict["code"]),
                "hatYon": "0"
            },
            headers={
                "Connection": "keep-alive",
                "Cache-Contol": "max-age=0",
                "Origin": "http://www.eshot.gov.tr",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": choice(settings.USER_AGENTS),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "http://www.eshot.gov.tr/tr/OtobusumNerede/290",
                "Accept-Encoding": "gzip, deflate, lzma",
                "Accept-Language": "en-US,en;q=0.8",
                "Cookie": "AspxAutoDetectCookieSupport=1; ASP.NET_SessionId=ur114gdsk4mg2l3fy5lqvga5"
            }
        )

        ## Stops
        logger.debug("Handling stops.")
        s_elms = BeautifulSoup(res.content, "html.parser")\
            .find("ul", {"class":"transfer"})\
            .find_all("li")


        for i, s in enumerate(s_elms):
            logger.debug("Found relation of {} to {}.".format(
                str(r_dict["code"]),
                s["id"]
            ))

            stops_forwards.append([i, int(s["id"])])

        ## Departure Times
        logger.debug("Handling departure times.")
        dt_elms = BeautifulSoup(res.content, "html.parser")\
            .find_all("ul", {"class":"timescape"})
        times = list() # Created to organize and equalize soon

        for i, dt in enumerate(dt_elms):
            table = [j.getText().strip() for j in dt.find_all("li")[1:]] # Getting Times
            times.append(table)

        times = equalizer(times) # Equalizes length

        for i in range(len(times)): # Changing 24 to 00 in hours.
            times[i] = list(map(midnight_formatter, times[i]))

        departure_times_forwards = times[:] # Copies

        # Backward Information
        logger.debug("Getting backwards information for {}".format(str(r_dict["code"])))

        res = requests.post(
            "http://www.eshot.gov.tr/tr/UlasimSaatleri/288",
            data={
                "hatId": str(r_dict["code"]),
                "hatYon": "1"
            },
            headers={
                "Connection": "keep-alive",
                "Cache-Contol": "max-age=0",
                "Origin": "http://www.eshot.gov.tr",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": choice(settings.USER_AGENTS),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "http://www.eshot.gov.tr/tr/OtobusumNerede/290",
                "Accept-Encoding": "gzip, deflate, lzma",
                "Accept-Language": "en-US,en;q=0.8",
                "Cookie": "AspxAutoDetectCookieSupport=1; ASP.NET_SessionId=ur114gdsk4mg2l3fy5lqvga5"
            }
        )

        soup = BeautifulSoup(res.content, "html.parser")

        ## Stops
        logger.debug("Handling stops.")
        s_elms = soup\
            .find("ul", {"class": "transfer"}) \
            .find_all("li")

        for i, s in enumerate(s_elms):
            logger.debug("Found relation of {} to {}.".format(
                str(r_dict["code"]),
                s["id"]
            ))

            stops_backwards.append([i, int(s["id"])])

        ## Departure Times
        logger.debug("Handling departure times.")
        dt_elms = soup\
            .find_all("ul", {"class": "timescape"})
        print(len(dt_elms))
        times = list()  # Created to organize and equalize soon

        for i, dt in enumerate(dt_elms):
            table = [j.getText().strip() for j in dt.find_all("li")[1:]]  # Getting Times
            times.append(table)

        times = equalizer(times)  # Equalizes length
        departure_times_backwards = times[:]  # Copies

        r_dict["stops_forwards"] = stops_forwards
        r_dict["stops_backwards"] = stops_backwards
        r_dict["departure_times_forwards"] = departure_times_forwards
        r_dict["departure_times_backwards"] = departure_times_backwards

        logger.info("Reinitializing Route<{}>".format(str(r_dict["code"])))
        try:
            logger.debug("Getting route object.")
            r_obj = models.Route.objects.get(code=r_dict["code"])
            logger.debug("Found route object. Deleting.")
            r_obj.delete()
        except models.Route.DoesNotExist:
            logger.debug("Route object could not be found.")

        logger.debug("Initializing route object.")

        try:
            r_obj = models.Route.objects.create(**r_dict)
        except Exception as e:
            logger.error("{code} initialization caused an error as... {name}: {msg}".format(
                code=r_dict["code"],
                name=e.__class__.__name__,
                msg=str(e)
            ))
            pass