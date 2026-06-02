from init_webdriver import *
import locators

driver = init_webdriver()

driver.find_element(*locators.USERNAME_FIELD).send_keys("locked_out_user")

driver.find_element(*locators.PASSWORD_FIELD).send_keys("secret_sauce")

driver.find_element(*locators.LOGIN_BUTTON).click()

driver.save_screenshot("./screenshots/TC-0003.png")