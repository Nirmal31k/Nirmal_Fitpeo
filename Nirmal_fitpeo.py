from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-javascript")  # Disable Javascript if necessary
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Set up WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.maximize_window()
driver.get('https://fitpeo.com/')

try:
    # Wait for the revenue calculator to load and click it
    try:
        revenue_calculator = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/header/div/div[3]/div[6]/a/div'))
        )
        revenue_calculator.click()
    except TimeoutException:
        print("Error: Revenue calculator button not found or not clickable.")
        driver.quit()
        exit()

    # Wait for the slider to load
    try:
        slider = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'MuiSlider-thumb'))
        )
    except TimeoutException:
        print("Error: Slider element not found.")
        driver.quit()
        exit()

    # Define max and target slider values
    max_value = 2000
    target_value = 1870
    percentage = (target_value / max_value) * 100

    # Move the slider based on the target value
    try:
        actions = ActionChains(driver)
        actions.click_and_hold(slider).move_by_offset(percentage, 0).release().perform()
    except ElementNotInteractableException:
        print("Error: Unable to interact with the slider.")
        driver.quit()
        exit()

    # Get and print the value after moving the slider
    try:
        slider_value = driver.find_element(By.XPATH, "//input[@type='range']").get_attribute("value")
        print(f"Slider value after movement: {slider_value}")
    except NoSuchElementException:
        print("Error: Slider value not found after movement.")
        driver.quit()
        exit()

    # Interact with the slider's text box directly
    try:
        slider_text_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@type="number"]'))
        )
        driver.execute_script("""
            var inputElement = arguments[0];
            inputElement.value = '560';
            var event = new Event('input', { bubbles: true });
            inputElement.dispatchEvent(event);
        """, slider_text_box)

        # Sync the slider value with the text box input
        driver.execute_script("""
            var sliderElement = arguments[0];
            sliderElement.value = '560';
            var event = new Event('input', { bubbles: true });
            sliderElement.dispatchEvent(event);
        """, driver.find_element(By.XPATH, "//input[@type='range']"))

        # Wait for the slider to reflect the value 560
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(By.XPATH, "//input[@type='range']").get_attribute("value") == "560"
        )
        slider_value_after = driver.find_element(By.XPATH, "//input[@type='range']").get_attribute("value")
        print(f"Slider value after typing in the text box: {slider_value_after}")
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error interacting with the slider text box or syncing values: {e}")
        driver.quit()
        exit()

    # Click checkboxes
    checkboxes = [
        '/html/body/div[position()=1 or position()=2]/div[1]/div[2]/div[1]/label/span[1]/input',
        '/html/body/div[position()=1 or position()=2]/div[1]/div[2]/div[2]/label/span[1]/input',
        '/html/body/div[position()=1 or position()=2]/div[1]/div[2]/div[3]/label/span[1]/input',
        '/html/body/div[position()=1 or position()=2]/div[1]/div[2]/div[8]/label/span[1]/input'
    ]
    for checkbox_xpath in checkboxes:
        try:
            checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, checkbox_xpath))
            )
            checkbox.click()
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error clicking checkbox at {checkbox_xpath}: {e}")
            driver.quit()
            exit()

    # Verify the total amount displayed
    try:
        total_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[position()=1 or position()=2]/div[1]/header/div/p[4]/p'))
        )
        element_text = total_header.text
        print(f"The text of the element is: {element_text}")

        # Assert the total value
        assert element_text == "$110295"
    except (TimeoutException, AssertionError) as e:
        print(f"Error verifying total amount: {e}")
        driver.quit()
        exit()

finally:
    driver.quit()
