import json
import logging
from locust import HttpLocust, TaskSequence, task, seq_task

logger = logging.getLogger(__name__)


class MyTaskSet(TaskSequence):

    def __init__(self, *args, **kwargs):
        super(MyTaskSet, self).__init__(*args, **kwargs)

        self.tokens = []

    def on_start(self):

        logger.setLevel(logging.INFO)
        logger.addHandler(logging.FileHandler("load_test.log"))

    @seq_task(1)
    @task
    def captcha(self):
        response = self.client.get("/captcha/")
        try:
            self.tokens.insert(0, response.json()['data']['token'])
        except KeyError:
            pass

        logger.info(response.text)

    @seq_task(2)
    @task
    def enable_api(self):
        try:
            response = self.client.put(
                "/enable_api/{}".format(self.tokens.pop()),
                json.dumps({
                    "username": "dummy",
                    "password": "dummy",
                    "captcha": "209201"
                })
            )
        except KeyError:
            pass

        logger.info(response.text)


class MyLocust(HttpLocust):

    task_set = MyTaskSet
    min_wait = 10000
    max_wait = 10000
