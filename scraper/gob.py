import sys
import os
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

sys.path.append(os.getcwd())

from preparation.data_manager import DataManager
from processing.clean import Cleaning

os.environ["WDM_SSL_VERIFY"] = "0"


class GobTranscripts:

    SLEEP = 1
    DEEP_SLEEP = 3
    WEB_PAGE = "https://www.congreso.es/busqueda-de-intervenciones"

    def __init__(self, out_dir: str, name: str):
        """_summary_
        :param out_dir: _description_
        :type out_dir: str
        :param name: _description_
        :type name: str
        """
        options = webdriver.ChromeOptions()
        options.add_argument("ignore-certificate-errors")
        options.add_argument("log-level=3")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("disable-infobars")
        options.add_experimental_option(
            "prefs", {"profile.default_content_settings.cookies": 2}
        )
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.transcripts = {}
        self.out_dir = out_dir
        self.name = name

    def extract_pdf_transcripts(self):
        """_summary_"""
        try:
            self._driver.get(GobTranscripts.WEB_PAGE)
            self._search(self.name)
            self.transcripts[self.name] = self._get_transcripts()
            while not self._check_last_page():
                self._next_page()
                self.transcripts[self.name] += self._get_transcripts()
            self._write_json()
            self._driver.close()
            self._driver.quit()

        except Exception:
            self._driver.close()
            self._driver.quit()
            raise

    def _search(self, name: str):
        """_summary_
        :param name: _description_
        :type name: str
        """
        try:
            input = WebDriverWait(self._driver, GobTranscripts.SLEEP).until(
                EC.presence_of_element_located((By.ID, "_intervenciones_orador"))
            )
            input.send_keys(name)
            WebDriverWait(self._driver, GobTranscripts.SLEEP).until(
                EC.element_to_be_clickable(
                    (By.ID, "_intervenciones_resultsShowedIntervenciones")
                )
            ).click()
            WebDriverWait(self._driver, GobTranscripts.SLEEP).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'Buscar')]")
                )
            ).click()
            time.sleep(GobTranscripts.DEEP_SLEEP)
        except Exception:
            raise

    def _check_last_page(self):
        """_summary_"""
        results = (
            WebDriverWait(self._driver, GobTranscripts.SLEEP)
            .until(
                EC.presence_of_element_located(
                    (By.ID, "_intervenciones_resultsShowedIntervenciones")
                )
            )
            .text
        )
        results = results.split(" ")
        pages = [word for word in results if word.isnumeric()]
        pages = np.unique(pages)
        if len(pages) == 2:
            return True
        else:
            return False

    def _next_page(self):
        """_summary_"""
        WebDriverWait(self._driver, GobTranscripts.SLEEP).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '>')]"))
        ).click()
        time.sleep(GobTranscripts.DEEP_SLEEP)

    def _get_transcripts(self):
        """_summary_"""
        transcripts = WebDriverWait(self._driver, GobTranscripts.SLEEP).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//a[contains(@href,'.PDF')]",
                )
            )
        )
        transcripts = [trans.get_attribute("href") for trans in transcripts]
        return transcripts

    def _write_json(self):
        """_summary_
        :param name: _description_
        :type name: str
        """
        out_file = Cleaning.create_name_file(self.name)
        out_file = self.out_dir + out_file + ".json"
        DataManager.write_json(out_file, self.transcripts)
