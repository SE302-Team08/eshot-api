"""
A script updating stops.
"""

import requests, logging, json, time
from izmir import models

logger = logging.getLogger(__name__)

def run():
    timer = dict()
    timer["main"] = dict()
    timer["main"]["start"] = time.time()

    logger.debug("Updating Bus Stops, Script Started")
    res = requests.get("http://www.eshot.gov.tr/tr/DuraktanGecenHatlar/KritereGoreDurakGetir?durak=")

    if res.status_code != 200:
        logger.error("Eshot Stop List request has returned an invalid status code: {}".format(str(res.status_code)))
    else:
        logger.debug("Eshot Stop List request has responsed.")

    stops = json.loads(res.text)
    logger.debug("JSON to Python")

    timer["dbpush"] = dict()
    timer["dbpush"]["start"] = time.time()
    query_length = 0
    logger.debug("Starting database push...")
    for stop in stops:
        try:
            models.Stop.objects.get(code=stop["DurakId"])
            query_length+=1
            logger.debug("Stop<{}> found in database, passing...".format(str(stop["DurakId"])))
            continue
        except models.Stop.DoesNotExist:
            pass

        info = {
            "code": stop["DurakId"],
            "label": stop["Adi"],
            "coor": [
                stop["KoorX"],
                stop["KoorY"]
            ]
        }

        query_length += 1
        obj = models.Stop.objects.create(**info)
        logger.info("New Stop<{}> added in database.".format(str(info["code"])))
        obj.save()

    timer["dbpush"]["end"] = time.time()
    timer["dbpush"]["total"] = timer["dbpush"]["start"] - timer["dbpush"]["end"]
    logger.debug("Database push finished in {} seconds with total {} querying.".format(str(timer["dbpush"]["total"]), str(query_length)))

    timer["main"]["end"] = time.time()
    timer["main"]["total"] = timer["main"]["start"] - timer["main"]["end"]
    logger.debug("Updating Bus Stops, Script Finished in {} seconds".format(str(timer["main"]["total"])))