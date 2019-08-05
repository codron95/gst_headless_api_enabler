from datetime import datetime

from selenium.common.exceptions import TimeoutException

from headless_api.gst_portal_mapper import GSTPortalMapper
from headless_api.exceptions import LoginException

from web_server.entities import JsonResponse


def ping(request, **kwargs):
    if request.method == "GET":
        return JsonResponse(200, "PING OK", request.data)

    if request.method == "POST":
        return JsonResponse(200, "PING OK", request.data)

    if request.method == "PUT":
        message = "PING OK: {update_entity_id}".format(
            update_entity_id=request.meta["update_entity_id"]
        )
        return JsonResponse(200, message, request.data)


def captcha(request, **kwargs):
    drivers = kwargs['drivers']

    ts = datetime.now()

    gpm = GSTPortalMapper()

    drivers[gpm.driver.session_id] = {
        "driver": gpm.driver,
        "lock": False,
        "ts": ts
    }

    try:
        base64 = gpm.get_captcha_base64()
    except TimeoutException:
        return JsonResponse(
            500,
            "Error occured while generating token.",
            errors=['Error occured while generating token.']
        )

    response_data = {
        "token": gpm.driver.session_id,
        "captcha_base64": base64,
        "ts": ts.strftime("%Y-%m-%d %H-%M")
    }

    return JsonResponse(200, "Token generated", response_data)


def enable_api(request, **kwargs):

    token = request.meta['update_entity_id']
    drivers = kwargs['drivers']

    username = request.data['username']
    password = request.data['password']
    captcha = request.data['captcha']

    try:
        drivers[token]['lock'] = True
    except KeyError:
        return JsonResponse(
            404,
            "Token not found",
            {"token": token},
            ["Token not found"]
        )

    gpm = GSTPortalMapper(drivers[token]['driver'])

    try:
        gpm.login(username, password, captcha)
    except LoginException as e:

        if e.code == -1:

            gpm.cleanup()
            del drivers[token]

            return JsonResponse(
                500,
                "Login Unsuccessful",
                {"token": token},
                ["Login Unsuccessful"]
            )

        ts = datetime.now()
        captcha_base64 = gpm.get_captcha_base64()
        drivers[token]['ts'] = ts
        drivers[token]['lock'] = False

        return JsonResponse(
            400,
            "Login Unsuccessful",
            {
                "token": token,
                "captcha_base64": captcha_base64,
                "ts": ts.strftime("%Y-%m-%d %H:%M")
            },
            [str(e)]
        )

    try:
        gpm.enable_api_access()
    except TimeoutException as e:
        gpm.cleanup()
        del drivers[token]

        return JsonResponse(
            500,
            "Error. Timed Out.",
            {"token": token},
            ["Error. Timed Out."]
        )

    gpm.cleanup()
    del drivers[token]

    return JsonResponse(
        200,
        "API access enabled",
        {"token": token}
    )
