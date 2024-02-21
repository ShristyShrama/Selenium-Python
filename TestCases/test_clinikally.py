from selenium import webdriver
import time
import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from twilio.rest import Client
import re

# Initialize the driver variable
driver = None
# Pass browser name here
browser_name = "chrome"

# setup method to run once before all test method
def setup_module(module):
    global driver
    #condition to determine which driver to instantiate
    if browser_name == "chrome":
        # Start Chrome WebDriver service
        chrome_service = ChromeService(ChromeDriverManager().install())
        chrome_service.start()

        # Set Chrome options
        chrome_options = ChromeOptions()

        # Initialize Chrome WebDriver
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    elif browser_name == "firefox":
        # Start Firefox WebDriver service
        firefox_service = FirefoxService(GeckoDriverManager().install())
        firefox_service.start()

        # Set Firefox options
        firefox_options = FirefoxOptions()

        # Initialize Firefox WebDriver
        driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

    else:
        print("Please pass correct browser name")
        raise Exception("driver not found")

    # Set implicit wait
    driver.implicitly_wait(10)
    # Delete all cookies
    driver.delete_all_cookies()
    # Open the website
    driver.get("https://www.clinikally.com/")

# teardown method to run once after all test method
def teardown_module(module):
    # Quit the browser
    driver.quit()

# Test add to cart functionality
def test_addToCart():
    # Find the search input field and enter a product name
    search_icon = driver.find_element(By.XPATH, "//input[@name='qs']")
    search_icon.click()
    search_input = driver.find_element(By.XPATH, "//input[@id='boost-sd__search-widget-init-input-1'][1]")
    search_input.send_keys("Demelan Lite Lotion")

    # Wait for search results to load
    time.sleep(2)

    # Find the product in the search results and click on it
    product = driver.find_element(By.XPATH, "//p[normalize-space()='Demelan Lite Lotion']")
    product.click()

    # Wait for the product page to load
    time.sleep(2)

    # Get expected product details
    expected_product_name = driver.find_element(By.XPATH, "(//h1[@class='product-meta__title heading h3'])[2]").text
    expected_product_size = driver.find_element(By.XPATH, "//div/label[@class='block-swatch__item']").text
    expected_price = driver.find_element(By.XPATH, "//span[@class='price price--highlight price--large']").text.strip()
    expected_price_value = expected_price.split('₹ ')[1].replace('.00', '')

    # Find the "Add to Cart" button and click on it
    add_to_cart_button = driver.find_element(By.XPATH, "//button[@id='AddToCart']//span[@class='loader-button__text'][normalize-space()='Add to cart']")
    add_to_cart_button.click()

    # Wait for the cart modal to appear
    time.sleep(2)

    # Verify product details in the cart
    product_name = driver.find_element(By.XPATH, "//a[@class='rebuy-cart__flyout-item-product-title']").text
    assert product_name == expected_product_name

    product_size = driver.find_element(By.XPATH, "//div[@class='rebuy-cart__flyout-item-variant-title']").text
    assert product_size == expected_product_size

    price = driver.find_element(By.XPATH, "//div[@class='rebuy-cart__flyout-item-price']//span[@class='rebuy-money sale']").text.strip()
    price_value = price.split('₹ ')[1].replace('.00', '')
    assert price_value == expected_price_value

    subtotal = driver.find_element(By.XPATH, "//div[@class='rebuy-cart__flyout-subtotal-amount']").text.strip()
    subtotal_value = subtotal.split('₹ ')[1].replace('.00', '')
    assert subtotal_value == expected_price_value

    quantity = driver.find_element(By.XPATH, "//span[@class='rebuy-cart__flyout-item-quantity-widget-label'][1]").text.strip()
    quantity_value = quantity.split('\n')[-1]
    expected_quantity = "1"
    assert quantity_value == expected_quantity

    time.sleep(2)

# Test checkout process
def test_checkout():
    # After adding item in cart click on secure checkout btn
    checkout = driver.find_element(By.XPATH, "//button[@class='rebuy-button rebuy-cart__checkout-button block zecpe-btn']")
    checkout.click()

    time.sleep(2)

    # NOTE: To automate OTP login we need twilio paid version as I have free version so I'm not able to automate OTP login although I
    # have written the steps & code to automate OTP login for checkout process.
    # Install selenium twilio package with command -- pip install selenium twilio
    # Along with this, we need to setup twilio account by visiting the website https://www.twilio.com/en-us

    # Twilio Account SID and Auth Token from your Twilio account dashboard
    account_sid = "AC42ed9c32b1b3a491edb667a1dd570775"
    auth_token = "9f13af301d3d26bfd0bcf509a462005c"

    # Twilio phone number from which OTP is sent
    twilio_phone_number = "+18777804236"

    # Your phone number where OTP will be received
    your_phone_number = "+917983619893"

    # Function to get OTP from received SMS
    def get_otp():
        client = Client(account_sid, auth_token)
        messages = client.messages.list(to=your_phone_number)
        for message in messages:
            if message.direction == 'inbound':
                otp = re.search(r'\b\d{6}\b', message.body)
                if otp:
                    return otp.group(0)
        return None

    # Enter phone number and request OTP
    mobile_number = driver.find_element(By.XPATH, "//input[@placeholder='Mobile Number']")
    mobile_number.send_keys("8449482255")

    call_otp = driver.find_element(By.XPATH, "//button[@class='zecpe-button']")
    call_otp.click()

    # Wait for OTP to be received
    time.sleep(10)

    # Get OTP from received SMS
    otp = get_otp()

    # Enter OTP in the OTP input field
    if otp:
        driver.find_element(By.XPATH, "//div[@id='zecpe-otp-input__div']").send_keys(otp)
        print("OTP entered successfully")
    else:
        print("Failed to retrieve OTP")

    # Click on continue btn after entering OTP
    continue_btn = driver.find_element(By.XPATH, "//button[@class='zecpe-button']")
    continue_btn.click()

    # Enter Shipping details -- code will break at this point as test script will not able to go shipping details step
    name = driver.find_element(By.XPATH, "//input[@id='fullName']")
    name.send_keys("Test User")

    address = driver.find_element(By.XPATH, "//textarea[@id='addressLine1']")
    address.send_keys("Banasthali, Newai, Tonk")

    pincode = driver.find_element(By.XPATH, "//input[@id='zip']")
    pincode.send_keys("244001")

    # Verify autofilled city after entering pincode
    city = driver.find_element(By.XPATH, "//input[@id='city']")
    city_text = city.get_attribute("textContent")
    expected_city = "Moradabad"
    assert city_text == expected_city

    # Verify autofilled state after entering pincode
    state = driver.find_element(By.XPATH, "//input[@id='state']")
    state_text = state.get_attribute("textContent")
    expected_state = "Uttar Pradesh"
    assert state_text == expected_state

    email = driver.find_element(By.XPATH, "//input[@id='email']")
    email.send_keys("testuser@gmail.com")

    save_btn = driver.find_element(By.XPATH, "//button[@class='zecpe-button']")
    save_btn.click()

