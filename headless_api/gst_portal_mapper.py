import time
import base64
from selenium import webdriver
from PIL import Image
from io import BytesIO

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

from .exceptions import LoginException
from .action_dispatcher import ActionDispatcher


class GSTPortalMapper(object):

    LOGIN_CONDITION_ELEMENT_XPATH = "//*[text()=\"Annual Return\"]"
    USERNAME_FIELD_XPATH = "//*[@id=\"username\"]"
    CAPTCHA_ERROR = "Enter valid Letters shown"
    USER_PASS_ERROR = "Invalid Username or Password. Please try again."

    def __init__(self, browser_session=None):

        self.captcha_image = None
        self.login_url = "https://services.gst.gov.in/services/login"

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--window-size=1200,1100")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")

        if not browser_session:
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
            self.driver.implicitly_wait(2)
        else:
            self.driver = browser_session

    def login(self, username, password, captcha):

        self.username = username,
        self.password = password
        self.captcha = captcha

        self._fill_inputs({
            "username": self.username,
            "captcha": self.captcha,
            "user_pass": self.password
        })

        self.driver.find_element_by_xpath("//button[@type=\"submit\"]").click()

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        GSTPortalMapper.LOGIN_CONDITION_ELEMENT_XPATH
                    )
                )
            )
        except TimeoutException as e:
            page_source = self.driver.page_source
            if GSTPortalMapper.CAPTCHA_ERROR in page_source:
                raise LoginException("Invalid Captcha", -2)

            if GSTPortalMapper.USER_PASS_ERROR in page_source:
                raise LoginException("Invalid Username or password", -3)

            raise LoginException(e, -1)

    def _fill_inputs(self, input_field_mappings):

        for field, value in input_field_mappings.items():
            xpath = "//*[@id=\"{field}\"]".format(field=field)
            element = self.driver.find_element_by_xpath(xpath)
            element.clear()
            element.send_keys(value)

    def get_captcha_base64(self):
        self._get_captcha_image()
        buffer = BytesIO()
        self.captcha_image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue())

    def save_captcha_image(self, path):
        self._get_captcha_image()
        self.captcha_image.save(path)

    def _get_captcha_image(self):

        self.driver.get(self.login_url)

        username_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    GSTPortalMapper.USERNAME_FIELD_XPATH
                )
            )
        )

        self._reveal_captcha(username_element)

        time.sleep(1)

        captcha_element = self.driver.find_element_by_xpath('//*[@id="imgCaptcha"]')
        captcha_location = captcha_element.location
        captcha_size = captcha_element.size

        complete_screenshot = self.driver.get_screenshot_as_png()

        captcha_im = Image.open(BytesIO(complete_screenshot))
        cropped_im = self._crop(captcha_im, captcha_location, captcha_size)

        self.captcha_image = cropped_im

    def _crop(self, image, location, size):

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']

        cropped_image = image.crop((left, top, right, bottom))
        return cropped_image

    def _reveal_captcha(self, username_element):

        # fill something in username field to reveal captcha
        username_element.send_keys("dummy")

    def cleanup(self):
        self.driver.quit()

    def enable_api_access(self):

        action_dispatcher = ActionDispatcher(self.driver)
        action_dispatcher.dispatch_all()
