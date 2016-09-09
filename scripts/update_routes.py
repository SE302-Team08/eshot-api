"""
A script updating routes.
"""

from django.conf import settings
from izmir import models

import logging, re, sys
from . import colorize
from datetime import datetime
from statistics import mean
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
from scripts import Timer

logger = logging.getLogger(__name__)

POLITENESS_LIMIT = 2
URL = "http://www.eshot.gov.tr/tr/UlasimSaatleri/288"

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

def run():
    profile = webdriver.FirefoxProfile()

    profile.add_extension("quickjava-2.0.8-fx.xpi")
    profile.set_preference("thatoneguydotnet.QuickJava.curVersion",
                           "2.0.8")  ## Prevents loading the 'thank you for installing screen'
    profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Images", 2)  ## Turns images off
    profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.AnimatedImage", 2)  ## Turns animated images off

    profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Flash", 2)  ## Flash
    profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Java", 2)  ## Java
    profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Silverlight", 2)

    profile.set_preference("network.http.pipelining", True)
    profile.set_preference("network.http.proxy.pipelining", True)
    profile.set_preference("network.http.pipelining.maxrequests", 8)
    profile.set_preference("content.notify.interval", 500000)
    profile.set_preference("content.notify.ontimer", True)
    profile.set_preference("content.switch.threshold", 250000)
    profile.set_preference("browser.cache.memory.capacity", 65536)  # Increase the cache capacity.
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("reader.parse-on-load.enabled", False)  # Disable reader, we won't need that.
    profile.set_preference("browser.pocket.enabled", False)  # Duck pocket too!
    profile.set_preference("loop.enabled", False)
    profile.set_preference("browser.chrome.toolbar_style", 1)  # Text on Toolbar instead of icons
    profile.set_preference("browser.display.show_image_placeholders",
                           False)  # Don't show thumbnails on not loaded images.
    profile.set_preference("browser.display.use_document_colors", False)  # Don't show document colors.
    profile.set_preference("browser.display.use_document_fonts", 0)  # Don't load document fonts.
    profile.set_preference("browser.display.use_system_colors", True)  # Use system colors.
    profile.set_preference("browser.formfill.enable", False)  # Autofill on forms disabled.
    profile.set_preference("browser.helperApps.deleteTempFileOnExit", True)  # Delete temprorary files.
    profile.set_preference("browser.shell.checkDefaultBrowser", False)
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("browser.startup.page", 0)  # blank
    profile.set_preference("browser.tabs.forceHide", True)  # Disable tabs, We won't need that.
    profile.set_preference("browser.urlbar.autoFill", False)  # Disable autofill on URL bar.
    profile.set_preference("browser.urlbar.autocomplete.enabled", False)  # Disable autocomplete on URL bar.
    profile.set_preference("browser.urlbar.showPopup", False)  # Disable list of URLs when typing on URL bar.
    profile.set_preference("browser.urlbar.showSearch", False)  # Disable search bar.
    profile.set_preference("extensions.checkCompatibility", False)  # Addon update disabled
    profile.set_preference("extensions.checkUpdateSecurity", False)
    profile.set_preference("extensions.update.autoUpdateEnabled", False)
    profile.set_preference("extensions.update.enabled", False)
    profile.set_preference("general.startup.browser", False)
    profile.set_preference("plugin.default_plugin_disabled", False)
    profile.set_preference("permissions.default.image", 2)  # Image load disabled again

    driver = webdriver.Firefox(profile)

    try:
        qc = 0 # Query Counter
        times = list()

        logger.info("Requesting main URL and parsing response data.")
        driver.get(URL)

        index = 0

        logger.debug("Locating route elements.")
        driver.find_element_by_css_selector(".chosen-single").click()
        total_r_elms = len(driver.find_elements_by_css_selector(".chosen-results li"))

        while index < total_r_elms:
            timer = Timer()
            timer.begin()

            logger.info("Operation Index: {}/{}".format(str(index), str(total_r_elms)))
            meta = dict()
            if index > 0:
                driver.find_element_by_css_selector(".chosen-single").click()
            # driver.find_element_by_css_selector(".chosen-single").click()
            r_elm = driver.find_element_by_css_selector(".chosen-results")
            r_elm = r_elm.find_elements_by_css_selector("li")[index]

            # Code and Terminals
            logger.info("Parsing code and terminals.")
            parser = re.findall("([0-9]+) : (.+)[ ]*-[ ]*(.+)", r_elm.text)[0]
            meta["code"] = int(parser[0])
            meta["terminals"] = [parser[1].strip(), parser[2].strip()]

            logger.info("Current element code is {}".format(str(meta["code"])))

            # Redirection
            logger.info("Redirecting to current element page.")
            r_elm.click()

            # logger.debug("Waiting body to load.")
            # WebDriverWait(driver, 15).until(
            #     expected_conditions.presence_of_element_located(
            #         driver.find_element_by_css_selector("body")
            #     )
            # )

            # Time Table
            logger.info("Parsing time table.")
            t_elms = driver.find_elements_by_css_selector(".timescape")
            table = list() # To insert time elements later.

            for i, t in enumerate(t_elms):
                logger.debug("Parsing timescape index {}".format(str(i)))

                col = list()
                rows = t.find_elements_by_css_selector("li")[1:]

                for r in rows:
                    d = datetime.strptime(r.text.strip(), "%H:%M") # Converting to datetime object each row
                    col.append(d)

                logger.debug("Pushing column to array.")
                table.append(col)

            table = equalizer(table)

            meta["departure_times"] = table


            # Relation Handler
            logger.info("Handling stop-route relations.")
            s_elms = driver.find_elements_by_css_selector(".transfer li")

            i = 0
            stops = list()
            for s in s_elms:
                code = int(s.get_attribute("id"))
                logger.info("Relation {}:{}".format(str(meta["code"]), str(code)))
                try:
                    models.Stop.objects.get(code=code)
                except models.Stop.DoesNotExist:
                    logger.error("Stop<{}> could not be found in database. Try updating stops first, then routes.")
                    sys.exit(1)
                stops.append([i, code])
                i+=1
                qc+=1
            meta["stops"] = stops
            # Updating Object
            logger.info("Updating Route<{}>".format(str(meta["code"])))

            try:
                obj = models.Route.objects.get(code=meta["code"])
                logger.warn("Route found, deleting to reinitialize...")
                obj.delete()
                qc += 2
            except models.Route.DoesNotExist:
                pass

            logger.info("Reinitializing Route<{}>".format(str(meta["code"])))
            obj = models.Route.objects.create(**meta)
            qc += 1

            timer.end()
            times.append(timer())

            index+=1

        logger.info("Update Routes Operation: {}/{}/{}/{}/{} | max/min/avr/ttl/qc".format(
            str(max(times)),
            str(min(times)),
            str(mean(times)),
            str(sum(times)),
            str(qc)
        ))
    except Exception as e:
        logger.error("{}@{}: {}".format(e.__class__.__name__, str(sys.exc_info()[-1].tb_lineno),str(e)))
        driver.quit()
