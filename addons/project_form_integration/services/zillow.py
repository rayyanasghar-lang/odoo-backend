from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time
import random
import json
import shutil
import tempfile
import os

_logger = logging.getLogger(__name__)

def scrape_zillow(address: str, base_url: str = "https://www.zillow.com/homes/"):
    """
    Scrape lot size and parcel number from Zillow by address.
    """
    if "http" not in address:
        formatted_address = address.replace(" ", "-").replace(",", "")
        url = f"{base_url}{formatted_address}_rb/"
    else:
        url = address

    # Create a temporary user data directory
    user_data_dir = tempfile.mkdtemp()

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless=new') 
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # Critical for Docker
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--remote-debugging-port=9222")

    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    data = {
        "lot_size": None,
        "parcel_number": None
    }
    
    driver = None
    try:
        # Use webdriver-manager to get the correct ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        
        _logger.info("Navigating to Zillow URL: %s", url)
        driver.get(url)
        
        time.sleep(random.uniform(5, 8))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
        time.sleep(random.uniform(2, 4))

        # --- Extraction Logic ---
        json_success = False
        try:
            script_content = None
            try:
                elem = driver.find_element(By.ID, "hdpApolloPreloadedData")
                script_content = elem.get_attribute("innerText")
            except: pass
            
            if not script_content:
                try:
                    elem = driver.find_element(By.ID, "__NEXT_DATA__")
                    script_content = elem.get_attribute("innerText")
                except: pass

            if script_content:
                json_data = json.loads(script_content)
                def find_key(obj, key):
                     if isinstance(obj, dict):
                         if key in obj: return obj[key]
                         for k, v in obj.items():
                             res = find_key(v, key)
                             if res: return res
                     elif isinstance(obj, list):
                         for i in obj:
                             res = find_key(i, key)
                             if res: return res
                     return None

                lot_val = find_key(json_data, "lotSize")
                lot_area = find_key(json_data, "lotAreaValue")
                parcel_id = find_key(json_data, "parcelId")
                parcel_num = find_key(json_data, "parcelNumber")
                apn = find_key(json_data, "apn")

                if lot_val or lot_area:
                    data["lot_size"] = str(lot_val or lot_area)
                if parcel_id or parcel_num or apn:
                    data["parcel_number"] = str(parcel_id or parcel_num or apn)
                
                if data["lot_size"] or data["parcel_number"]:
                    json_success = True
                    if data["lot_size"] and "sqft" not in str(data["lot_size"]) and "acre" not in str(data["lot_size"]).lower():
                         try:
                             val = float(str(data["lot_size"]).replace(",",""))
                             if val < 500:
                                 data["lot_size"] = f"{val} Acres"
                             else:
                                 data["lot_size"] = f"{val} sqft"
                         except: pass

        except Exception as e:
            _logger.warning("JSON extraction failed: %s", e)

        if not json_success or (not data["lot_size"] and not data["parcel_number"]):
            try:
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if "See more" in btn.text or "See all facts" in btn.text:
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(2)
                            break
                except: pass
                
                all_list_items = driver.find_elements(By.TAG_NAME, "li")
                for item in all_list_items:
                    txt = item.text.strip()
                    if "Lot size:" in txt or "Lot:" in txt:
                        parts = txt.split(":")
                        if len(parts) > 1:
                            data["lot_size"] = parts[-1].strip()
                    if "Size:" in txt and ("Acres" in txt or "sqft" in txt):
                        parts = txt.split(":")
                        if len(parts) > 1:
                             data["lot_size"] = parts[-1].strip()
                    if "Parcel number:" in txt or "APN:" in txt:
                        parts = txt.split(":")
                        if len(parts) > 1:
                            data["parcel_number"] = parts[-1].strip()
            except Exception: pass

        _logger.info("Final scraped data: %s", data)
        return data

    except Exception as e:
        _logger.error("Error scraping Zillow: %s", str(e))
        raise Exception(f"Failed to scrape Zillow page: {str(e)}")
    
    finally:
        if driver:
            try:
                driver.quit()
            except: pass
        
        # Clean up temp user data dir
        try:
            shutil.rmtree(user_data_dir, ignore_errors=True)
        except: pass


if __name__ == "__main__":
    test_address = "1745 SE 4101, ANDREWS, TX 79714-5998"
    result = scrape_zillow(test_address)
    print(result)
