from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time
import random
import re
import shutil
import tempfile
import os

_logger = logging.getLogger(__name__)


def scrape_asce_hazard(address: str, standard: str = "ASCE/SEI 7-22", risk_category: str = "II"):
    """
    Scrape wind speed and snow load data from ASCE Hazard Tool.
    
    Args:
        address: Full address string to search for
        standard: ASCE standard to use (default: "ASCE/SEI 7-22")
        risk_category: Risk category (default: "II")
    
    Returns:
        dict with wind_speed and snow_load values
    """
    url = "https://ascehazardtool.org/"
    
    # Create a temporary user data directory
    user_data_dir = tempfile.mkdtemp()
    
    # Configure Chrome options for headless execution
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
    chrome_options.add_argument("--remote-debugging-port=9223")
    
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    data = {
        "wind_speed": None,
        "snow_load": None
    }
    
    driver = None
    try:
        # Use webdriver-manager to get the correct ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        # Apply stealth settings
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        
        _logger.info("Navigating to ASCE Hazard Tool: %s", url)
        driver.get(url)
        
        # Wait for page to load
        time.sleep(random.uniform(3, 5))
        
        # --- Close Welcome/Splash Dialog ---
        _logger.info("Attempting to close welcome dialog...")
        close_selectors = [
            (By.CSS_SELECTOR, "#welcomePopup .details-popup-close-icon"),
            (By.CSS_SELECTOR, ".details-popup-close-icon"),
            (By.CSS_SELECTOR, ".splash-container .close"),
            (By.CSS_SELECTOR, ".jimu-btn-close"),
            (By.XPATH, "//button[contains(@class, 'close') and contains(@class, 'jimu')]"),
            (By.XPATH, "//div[contains(@class, 'splash')]//div[contains(@class, 'close')]"),
            (By.CSS_SELECTOR, ".popup-close"),
            (By.CSS_SELECTOR, "[class*='close-icon']"),
        ]
        
        dialog_closed = False
        for by, val in close_selectors:
            try:
                element = wait.until(EC.presence_of_element_located((by, val)))
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                try:
                    wait.until(EC.element_to_be_clickable((by, val))).click()
                except Exception:
                    driver.execute_script("arguments[0].click();", element)
                _logger.info("Welcome dialog closed with selector: %s", val)
                dialog_closed = True
                break
            except TimeoutException:
                continue
            except Exception as e:
                _logger.debug("Failed selector %s: %s", val, e)
        
        if not dialog_closed:
            _logger.warning("Could not close welcome dialog - may not exist or already closed")
        
        time.sleep(random.uniform(1, 2))
        
        # --- Search for Address ---
        _logger.info("Searching for address: %s", address)
        try:
            search_input = wait.until(EC.element_to_be_clickable((By.ID, "geocoder_input")))
            search_input.clear()
            search_input.send_keys(address)
            time.sleep(1.5)  # Wait for suggestions
            
            # Try clicking search button or press Enter
            try:
                search_btn = driver.find_element(By.CSS_SELECTOR, ".geocoder-search-icon")
                search_btn.click()
            except Exception:
                search_input.send_keys(Keys.ENTER)
            
            _logger.info("Address search submitted")
        except Exception as e:
            _logger.error("Failed to search for address: %s", e)
            raise Exception(f"Address search failed: {e}")
        
        # Wait for map to zoom and results to load
        time.sleep(random.uniform(4, 6))
        
        # --- Configure Standard ---
        _logger.info("Configuring standard: %s", standard)
        try:
            std_select_elem = wait.until(EC.presence_of_element_located((By.ID, "standards-selector")))
            Select(std_select_elem).select_by_visible_text(standard)
            time.sleep(2)
        except Exception as e:
            _logger.warning("Failed to set standard: %s", e)
        
        # --- Configure Risk Category ---
        _logger.info("Configuring risk category: %s", risk_category)
        try:
            risk_select_elem = wait.until(EC.presence_of_element_located((By.ID, "risk-level-selector")))
            Select(risk_select_elem).select_by_visible_text(risk_category)
            time.sleep(2)
        except Exception as e:
            _logger.warning("Failed to set risk category: %s", e)
        
        # --- Select Data Types (Wind & Snow) ---
        _logger.info("Selecting data types: Wind and Snow")
        try:
            wind_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Wind')]")))
            wind_label.click()
            time.sleep(0.5)
        except Exception as e:
            _logger.warning("Failed to select Wind: %s", e)
        
        try:
            snow_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Snow')]")))
            snow_label.click()
            time.sleep(0.5)
        except Exception as e:
            _logger.warning("Failed to select Snow: %s", e)
        
        # --- Click View Results ---
        _logger.info("Clicking View Results...")
        try:
            view_results_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'View Results')]")))
            view_results_btn.click()
            time.sleep(5)  # Wait for report generation
        except Exception as e:
            _logger.warning("View Results button issue: %s", e)
        
        # --- Extract Data from Report ---
        _logger.info("Extracting data from report...")
        try:
            report_div = wait.until(EC.presence_of_element_located((By.ID, "report")))
            # Wait for content to be non-empty
            wait.until(lambda d: len(d.find_element(By.ID, "report").text.strip()) > 10)
            report_text = report_div.text
            _logger.debug("Report text: %s", report_text[:500])
            
            # Extract wind speed using regex
            wind_patterns = [
                r"Wind.*?([\d\.]+)\s*(?:V|mph|Vmph)",
                r"V\s*=?\s*([\d\.]+)\s*mph",
                r"([\d\.]+)\s*Vmph",
                r"Wind Speed.*?([\d\.]+)",
            ]
            
            for pattern in wind_patterns:
                wind_match = re.search(pattern, report_text, re.DOTALL | re.IGNORECASE)
                if wind_match:
                    data["wind_speed"] = f"{wind_match.group(1)} mph"
                    break
            
            # Extract snow load using regex
            snow_patterns = [
                r"Ground Snow Load.*?([\d\.]+)\s*(?:lb/ft|psf)",
                r"Snow.*?([\d\.]+)\s*(?:lb/ft|psf)",
                r"pg\s*=?\s*([\d\.]+)",
                r"([\d\.]+)\s*lb/ft",
            ]
            
            for pattern in snow_patterns:
                snow_match = re.search(pattern, report_text, re.DOTALL | re.IGNORECASE)
                if snow_match:
                    data["snow_load"] = f"{snow_match.group(1)} lb/ft²"
                    break
            
        except TimeoutException:
            _logger.warning("Report div not found or empty after waiting")
        except Exception as e:
            _logger.error("Error extracting report data: %s", e)
        
        _logger.info("Final ASCE scraped data: %s", data)
        return data
        
    except Exception as e:
        _logger.error("Error scraping ASCE Hazard Tool: %s", str(e))
        raise Exception(f"Failed to scrape ASCE Hazard Tool: {str(e)}")
    
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        
        # Clean up temp user data dir
        try:
            shutil.rmtree(user_data_dir, ignore_errors=True)
        except Exception:
            pass


if __name__ == "__main__":
    # Test
    test_address = "615 N SHIRK RD, NEW HOLLAND, PA 17557"
    result = scrape_asce_hazard(test_address)
    print(result)
