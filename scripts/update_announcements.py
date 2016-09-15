import logging, requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from izmir.models import Announcement
from . import colorize

logger = logging.getLogger(__name__)

url = "http://www.eshot.gov.tr"

def run():
    logger.info("Initializing Update Notifications Script")

    logger.info("Requesting All Notifications Page")
    res = requests.get("http://www.eshot.gov.tr/tr/TumDuyurular/93")

    logger.debug("Crawling announcement links...")
    ann_href_list = list()

    ann_elm = BeautifulSoup(res.content, "html.parser")\
        .find_all("div", {"class": "announcements"})

    for elm in ann_elm:
        href = elm.a["href"]
        ann_href_list.append(url+href)

    logger.info("Requesting each announcements...")
    for href in ann_href_list:
        logger.debug("Requesting: {}".format(href))

        res = requests.get(href)
        soup = BeautifulSoup(res.content, "html.parser")

        title = soup.find("p", {"id": "duyuruBaslik"}).getText()
        content = soup.find("figure", {"id": "duyuruIcerik"}).getText().strip()
        if content == "":
            content = "Detaylar için eshot.gov.tr adresini ziyaret edin."

        today = date.today()

        ann_dict = {
            "title": title,
            "content": content,
            "is_eshot": True,
            "expiration": datetime(today.year, today.month, today.day, 23, 59, 59)
        }

        logger.debug("Initializing object...")

        try:
            ann_obj = Announcement.objects.get(title=title, content=content)
            logger.warn("Announcement already found in database, updating...")
            ann_obj.expiration = datetime(today.year, today.month, today.day, 23, 59, 59)
            ann_obj.save()
            continue
        except Announcement.DoesNotExist:
            logger.info("Initializing announcement...")
            ann_obj = Announcement.objects.create(**ann_dict)

    # Deleting expired announcements
    now = datetime.now()
    anns = Announcement.objects.filter(expiration__lte=now)
    anns.delete()