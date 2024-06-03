#!/usr/bin/env python3

"""
# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

Description: This module scrapes all the data elements in FITBIR and saves them to a CSV file.

"""
import os
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


def scrape_all():
    profile = FirefoxProfile()
    profile.set_preference("browser.download.panel.shown", False)
    profile.set_preference("browser.helperApps.neverAsk.openFile","text/csv,application/vnd.ms-excel")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/vnd.ms-excel")
    profile.set_preference("browser.download.folderList", 2);
    profile.set_preference("browser.download.dir", "c:\\firefox_downloads\\")

    driver = webdriver.Firefox(firefox_profile=profile)
    driver.get("https://fitbir.nih.gov/content/data-dictionary")

    time.sleep(30)

    driver.switch_to.frame(driver.find_element_by_id("dataElementIFrame"))

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "downloadResultsLink"))).click()
    link = driver.find_element_by_link_text('CSV')
    link.click()
    alert = driver.switch_to.alert
    alert.accept()

    while not os.path.exists(os.path.expanduser('~{0}Downloads{0}dataElementExport_REDCap.csv'.format(os.sep))):
        time.sleep(1)

    os.rename(os.path.expanduser('~{0}Downloads{0}}dataElementExport_REDCap.csv'.format(os.sep)), 'Outputs{}all_fitbir_data_dictionaries.csv'.format(os.sep))

    driver.close()

#if __name__ == '__main__':

#    scrape_all()
