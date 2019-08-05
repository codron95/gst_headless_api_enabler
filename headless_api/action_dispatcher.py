import time

from collections import OrderedDict
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException


class ActionDispatcher(object):

    def __init__(self, driver):
        self.driver = driver

        self.DISPATCH_INFO = OrderedDict([
            ("DROPDOWN_ELEMENT", {
                "xpath": "/html/body/div[1]/ng-include[1]/header/div[2]/div/div/ul/li[1]/div/a",
                "action": self.click,
                "delay": 2,
            }),
            ("PROFILE_ELEMENT", {
                "xpath": "/html/body/div[1]/ng-include[1]/header/div[2]/div/div/ul/li[1]/div/ul/li[2]/a",
                "action": self.click,
                "delay": 0,
            }),
            ("API_ACCESS", {
                "xpath": "/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div[1]/ul/li[4]/a",
                "action": self.click,
                "delay": 2,
            }),
            ("ENABLE_RADIO", {
                "xpath": "//input[@type=\"radio\"][1]",
                "action": self.click,
                "delay": 2,
            }),
            ("SELECT_ELEMENT", {
                "xpath": "//select",
                "action": self.dropdown,
                "delay": 0,
            }),
            ("CONFIRM_BUTTON", {
                "xpath": "//button[@type=\"submit\"]",
                "action": self.click,
                "delay": 0,
            })
        ])

    def dispatch(self, key):
        action = self.DISPATCH_INFO[key]["action"]
        xpath = self.DISPATCH_INFO[key]["xpath"]
        delay = self.DISPATCH_INFO[key]["delay"]

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        xpath
                    )
                )
            )
        except TimeoutException as e:
            raise e

        time.sleep(delay)

        action(xpath)

    def dispatch_all(self):
        keys = self.DISPATCH_INFO.keys()
        for key in keys:
            try:
                self.dispatch(key)
            except TimeoutException as e:
                raise e

    def click(self, xpath):
        self.driver.find_element_by_xpath(xpath).click()

    def dropdown(self, xpath):
        select = Select(self.driver.find_element_by_xpath(xpath))
        no_of_elements = len(select.options)
        selection_index = no_of_elements - 1

        select.select_by_index(selection_index)
