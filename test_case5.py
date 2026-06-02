from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from init_webdriver import *
import locators

driver = init_webdriver()
wait = WebDriverWait(driver, 5)

driver.find_element(*locators.USERNAME_FIELD).send_keys("standard_user")
driver.find_element(*locators.PASSWORD_FIELD).send_keys("secret_sauce")
driver.find_element(*locators.LOGIN_BUTTON).click()

driver.find_element(*locators.BURGER_BUTTON).click()
logout = driver.find_element(*locators.LOGOUT_BUTTON)
wait.until(EC.element_to_be_clickable(logout)).click()

driver.save_screenshot("./screenshots/TC-0004.png")