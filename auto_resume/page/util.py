from contextlib import contextmanager
import os
import random
import time
import base64
from pathlib import Path
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.utils import free_port

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROME_PROFILE_PATH = Path(Path.cwd(), "chrome_profile", "linkedin_profile")
CHROME_PROFILE_PATH.mkdir(parents=True, exist_ok=True)


def browser_options(headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--auto-open-devtools-for-tabs")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # options.add_argument("--user-data-dir=" + str(CHROME_PROFILE_PATH.parent))
    # options.add_argument("--profile-directory=" + str(CHROME_PROFILE_PATH.name))

    return options


def init_browser(headless=False):
    options = browser_options(headless)
    driver_path = ChromeDriverManager().install()
    service = ChromeService(port=free_port(), executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


@contextmanager
def browser(**kwargs):
    try:
        print("entering browser")
        browser = init_browser(**kwargs)
        yield browser
    finally:
        print("leaving browser")
        # browser.close()


def local_file(path: Path):
    return f"file:///{path.absolute()}"


def html_to_pdf(path: Path, timeout=2):
    # Validate and prepare file paths
    if not path.is_file():
        raise FileNotFoundError(f"The specified file does not exist: {path}")

    with browser(headless=True) as driver:
        driver.get(local_file(path))

        try:
            WebDriverWait(driver, timeout).until(
                EC.staleness_of(driver.find_element(by=By.TAG_NAME, value="html"))
            )
        except TimeoutException:
            pdf_base64 = driver.execute_cdp_cmd(
                "Page.printToPDF",
                {
                    "printBackground": True,
                    "landscape": False,
                    "paperWidth": 10,
                    "paperHeight": 11,
                    "marginTop": 0,
                    "marginBottom": 0,
                    "marginLeft": 0,
                    "marginRight": 0,
                    "displayHeaderFooter": False,
                    "preferCSSPageSize": True,
                    "generateDocumentOutline": False,
                    "generateTaggedPDF": False,
                    "transferMode": "ReturnAsBase64",
                },
            )

            return base64.b64decode(pdf_base64["data"])
