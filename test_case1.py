import locators
from init_webdriver import *

driver = init_webdriver()

driver.find_element(*locators.USERNAME_FIELD).send_keys("standard_user")

driver.find_element(*locators.PASSWORD_FIELD).send_keys("secret_sauce")

driver.find_element(*locators.LOGIN_BUTTON).click()

driver.save_screenshot("./screenshots/TC-0001.png")