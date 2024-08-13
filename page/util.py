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
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--auto-open-devtools-for-tabs")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    options.add_argument("--user-data-dir=" + str(CHROME_PROFILE_PATH.parent))
    options.add_argument("--profile-directory=" + str(CHROME_PROFILE_PATH.name))

    return options


def browser(headless=False):
    options = browser_options(headless)
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def local_file(path: Path):
    return f"file:///{path.absolute()}"


def html_to_pdf(path: Path, timeout=2):
    # Validate and prepare file paths
    if not path.is_file():
        raise FileNotFoundError(f"The specified file does not exist: {path}")

    driver = browser(headless=True)
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

    finally:
        # Ensure the driver is closed
        driver.quit()


def is_scrollable(element):
    scroll_height = element.get_attribute("scrollHeight")
    client_height = element.get_attribute("clientHeight")
    return int(scroll_height) > int(client_height)


def scroll_slow(driver, scrollable_element, start=0, end=3600, step=100, reverse=False):
    if reverse:
        start, end = end, start
        step = -step
    if step == 0:
        raise ValueError("Step cannot be zero.")
    script_scroll_to = "arguments[0].scrollTop = arguments[1];"
    try:
        if scrollable_element.is_displayed():
            if not is_scrollable(scrollable_element):
                print("The element is not scrollable.")
                return
            if (step > 0 and start >= end) or (step < 0 and start <= end):
                print("No scrolling will occur due to incorrect start/end values.")
                return
            for position in range(start, end, step):
                try:
                    driver.execute_script(
                        script_scroll_to, scrollable_element, position
                    )
                except Exception as e:
                    print(f"Error during scrolling: {e}")
                time.sleep(random.uniform(1.0, 2.6))
            driver.execute_script(script_scroll_to, scrollable_element, end)
            time.sleep(1)
        else:
            print("The element is not visible.")
    except Exception as e:
        print(f"Exception occurred: {e}")
