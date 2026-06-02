import time
from itertools import count

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from locators import *

EXPECTED_ITEMS = [
    "Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Fleece Jacket", "Sauce Labs Onesie", "Test.allTheThings() T-Shirt (Red)"
]
EXPECTED_PRICES = [29.99, 9.99, 15.99, 49.99, 7.99, 15.99]


def init_webdriver():

    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False  # вимикає перевірку витоку паролів
    })
    options.add_argument("--disable-save-password-bubble")
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


driver = init_webdriver()
wait = WebDriverWait(driver, 5)


def login(username, password):

    driver.get("https://www.saucedemo.com/")
    driver.find_element(*USERNAME_FIELD).send_keys(username)
    driver.find_element(*PASSWORD_FIELD).send_keys(password)
    driver.find_element(*LOGIN_BUTTON).click()


def get_sorted_expected(name_sorted):
    pairs = list(zip(EXPECTED_PRICES, EXPECTED_ITEMS))
    if name_sorted == 'az':
        return sorted(EXPECTED_ITEMS)
    elif name_sorted == 'za':
        return sorted(EXPECTED_ITEMS, reverse=True)
    elif name_sorted == 'lohi':
        return [item for _, item in sorted(pairs, key=lambda x: (x[0], x[1]))]
    elif name_sorted == 'hilo':
        return [item for _, item in sorted(pairs, key=lambda x: (-x[0], x[1]))]


def sorted_items(name_sorted):

    dropdown_element = driver.find_element(*SELECT_SORTING)
    select = Select(dropdown_element)
    select.select_by_value(name_sorted)

    items = driver.find_elements(*INVENTORY_ITEM_NAME_LOCATOR)
    items_name = [element.text for element in items]

    expected = get_sorted_expected(name_sorted)
    return expected, items_name


def test_valid_login():

    login("standard_user", "secret_sauce")
    assert "/inventory" in driver.current_url, "Login failed — inventory page not opened"


def test_login_with_invalid_password():

    login("standard_user", "qwerty123")
    error = driver.find_element(*ERROR_MESSAGE)
    assert error.is_displayed(), "Error message not shown for wrong password"


def test_login_with_locked_out_user():

    login("locked_out_user", "secret_sauce")
    error = driver.find_element(*ERROR_MESSAGE)
    assert "Epic sadface: Sorry, this user has been locked out." in error.text, "Locked out error not shown"


def test_logout():

    login("standard_user", "secret_sauce")
    driver.find_element(*BURGER_BUTTON).click()
    count_items = len(driver.find_elements(*BURGER_MENU))
    assert count_items == 4, "Burger menu does not have 4 items"
    logout = driver.find_element(*LOGOUT_BUTTON)
    wait.until(EC.element_to_be_clickable(logout)).click()
    assert "/inventory" not in driver.current_url, "Logout failed"


def test_saving_the_cart_after_logout():

    login("standard_user", "secret_sauce")
    wait.until(EC.element_to_be_clickable(ADD_TO_CART_BUTTON)).click()
    assert driver.find_element(*SHOPPING_CART_BADGE).text == "1", "Item not added to cart"

    driver.find_element(*BURGER_BUTTON).click()
    count_items = len(driver.find_elements(*BURGER_MENU))
    assert count_items == 4, "Burger menu does not have 4 items"

    logout = driver.find_element(*LOGOUT_BUTTON)
    wait.until(EC.element_to_be_clickable(logout)).click()

    login("standard_user", "secret_sauce")
    driver.find_element(*CART_BUTTON).click()
    cart_items = driver.find_element(*SHOPPING_CART_BADGE).text
    assert cart_items != 0, "Cart should be empty after logout"


def test_sorting():

    login("standard_user", "secret_sauce")
    for sort_value in ['az', 'za', 'lohi', 'hilo']:
        expected, actual = sorted_items(sort_value)
        assert actual == expected, (
            f"Sorting '{sort_value}' failed\n"
            f"Expected: {expected}\n"
            f"Actual:   {actual}"
        )


def test_footer_links():

    login("standard_user", "secret_sauce")

    twitter = driver.find_element(*TWITTER_LOCATOR)
    facebook = driver.find_element(*FACEBOOK_LOCATOR)
    linkedin = driver.find_element(*LINKEDIN_LOCATOR)

    twitter.click()
    tabs = driver.window_handles
    driver.switch_to.window(tabs[1])
    assert driver.current_url == "https://x.com/saucelabs", "Link is not corrected"
    driver.close()

    driver.switch_to.window(tabs[0])
    facebook.click()
    tabs = driver.window_handles
    driver.switch_to.window(tabs[1])
    assert driver.current_url == "https://www.facebook.com/saucelabs", "Link is not corrected"
    driver.close()

    driver.switch_to.window(tabs[0])
    linkedin.click()
    tabs = driver.window_handles
    driver.switch_to.window(tabs[1])
    assert driver.current_url == "https://www.linkedin.com/company/sauce-labs/", "Link is not corrected"
    driver.close()
    driver.switch_to.window(tabs[0])


def test_valid_checkout():

    login("standard_user", "secret_sauce") # Cart not empty
    assert driver.find_element(*SHOPPING_CART_BADGE).text == '1', 'Item not added to cart'

    driver.find_element(*CART_BUTTON).click()
    assert len(driver.find_elements(*CART_ITEM)) == 1, "Item not added to cart"

    driver.find_element(*CHECKOUT_BUTTON).click()
    driver.find_element(*FIRST_NAME_FIELD).send_keys("username")
    driver.find_element(*LAST_NAME_FIELD).send_keys("user")
    driver.find_element(*POSTAL_CODE_FIELD).send_keys("123456")
    driver.find_element(*CONTINUE_BUTTON).click()
    driver.find_element(*FINISH_BUTTON).click()
    assert "Thank you for your order!" == driver.find_element(*COMPLETE_HEADER).text, "Order not completed"

    driver.find_element(*BACK_TO_HOME_BUTTON).click()
    assert "https://www.saucedemo.com/inventory.html" == driver.current_url, "User not back to home page"


def test_checkout_without_products():

    login("standard_user", "secret_sauce")

    driver.find_element(*CART_BUTTON).click()
    assert len(driver.find_elements(*CART_ITEM)) == 0, "Cart should be empty"

    driver.find_element(*CHECKOUT_BUTTON).click()
    assert driver.current_url == "https://www.saucedemo.com/cart.html", "User not located on the \"Cart\" page and error is not visible"