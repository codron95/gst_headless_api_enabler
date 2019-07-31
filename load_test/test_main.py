import logging
from locust import HttpLocust, TaskSet, task

logger = logging.getLogger(__name__)


class MyTaskSet(TaskSet):

    def on_start(self):

        logger.setLevel(logging.INFO)
        logger.addHandler(logging.FileHandler("load_test.log"))

    @task
    def captcha(self):
        response = self.client.get("/captcha/")

        logger.info(response.text)


class MyLocust(HttpLocust):

    task_set = MyTaskSet
    min_wait = 900000
    max_wait = 900000
