from web_server.controllers import ping, captcha

URL_CONFIG = {
    "/": ping,
    "/captcha/": captcha,
}
