import time

from collections import OrderedDict
from selenium.webdriver.support.ui import Select


class ActionDispatcher(object):

    def __init__(self, driver):
        self.driver = driver

        self.DISPATCH_INFO = OrderedDict([
            ("DROPDOWN_ELEMENT", {
                "xpath": "/html/body/div[1]/ng-include[1]/header/div[2]/div/div/ul/li[1]/div/a",
                "action": self.click,
                "delay": 3
            }),
            ("PROFILE_ELEMENT", {
                "xpath": "/html/body/div[1]/ng-include[1]/header/div[2]/div/div/ul/li[1]/div/ul/li[2]/a",
                "action": self.click,
                "delay": 1
            }),
            ("API_ACCESS", {
                "xpath": "/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div[1]/ul/li[4]/a",
                "action": self.click,
                "delay": 3
            }),
            ("ENABLE_RADIO", {
                "xpath": "//input[@type=\"radio\"][1]",
                "action": self.click,
                "delay": 3
            }),
            ("SELECT_ELEMENT", {
                "xpath": "//select",
                "action": self.dropdown,
                "delay": 1
            }),
            ("CONFIRM_BUTTON", {
                "xpath": "//button[@type=\"submit\"]",
                "action": self.click,
                "delay": 0
            })
        ])

    def dispatch(self, key):
        action = self.DISPATCH_INFO[key]["action"]
        xpath = self.DISPATCH_INFO[key]["xpath"]
        delay = self.DISPATCH_INFO[key]["delay"]

        time.sleep(delay)
        action(xpath)

    def dispatch_all(self):
        keys = self.DISPATCH_INFO.keys()
        for key in keys:
            self.dispatch(key)

    def click(self, xpath):
        self.driver.find_element_by_xpath(xpath).click()

    def dropdown(self, xpath):
        select = Select(self.driver.find_element_by_xpath(xpath))
        no_of_elements = len(select.options)
        selection_index = no_of_elements - 1

        select.select_by_index(selection_index)
