from web_server.controllers import ping, captcha, enable_api
from web_server.entities import URL


URL_CONFIG = {
    "/": URL(ping, allowed_methods=["GET", "POST", "PUT"]),
    "/captcha/": URL(captcha, allowed_methods=["GET"]),
    "/enable_api/": URL(enable_api, allowed_methods=["PUT"])
}
