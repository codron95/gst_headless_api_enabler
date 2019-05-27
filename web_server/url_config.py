from web_server.controllers import ping, captcha
from web_server.entities import URL


URL_CONFIG = {
    "/": URL(ping, allowed_methods=["GET", "POST", "PUT"]),
    "/captcha/": URL(captcha, allowed_methods=["GET"]),
}
