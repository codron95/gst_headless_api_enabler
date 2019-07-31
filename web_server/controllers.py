from datetime import datetime

from selenium.common.exceptions import TimeoutException

from headless_api.gst_portal_mapper import GSTPortalMapper
from headless_api.exceptions import LoginException
from headless_api.entities import BrowserSession

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
    ps = kwargs['persistent_store']

    gpm = GSTPortalMapper()
    base64 = gpm.get_captcha_base64()
    ts = datetime.now()

    ps[gpm.driver.session_id] = {
        "session_url": gpm.driver.command_executor._url,
        "ts": ts
    }

    response_data = {
        "token": gpm.driver.session_id,
        "captcha_base64": base64,
        "ts": ts.strftime("%Y-%m-%d %H:%M")
    }

    return JsonResponse(200, "Token generated", response_data)


def enable_api(request, **kwargs):
    token = request.meta['update_entity_id']
    ps = kwargs['persistent_store']

    username = request.data['username']
    password = request.data['password']
    captcha = request.data['captcha']
    try:
        browser_session = BrowserSession(ps[token]['session_url'], token)
    except KeyError as e:
        return JsonResponse(
            404,
            "Token not found",
            {"token": token},
            ["Token not found"]
        )

    gpm = GSTPortalMapper(browser_session)

    try:
        gpm.login(username, password, captcha)
    except LoginException as e:
        # cleanup the gpm object
        gpm.cleanup()

        # Delete reference to it from our persistent_store to clear memory
        del ps[token]

        if e.code == -1:
            return JsonResponse(
                500,
                "Login Unsuccessful",
                {"token": token},
                ["Login Unsuccessful"]
            )

        return JsonResponse(
            400,
            "Login Unsuccessful",
            {"token": token},
            [str(e)]
        )

    try:
        gpm.enable_api_access()
    except TimeoutException as e:
        # cleanup the gpm object
        gpm.cleanup()

        # Delete reference to it from our persistent_store to clear memory
        del ps[token]

        return JsonResponse(
            500,
            "Error. Timed Out.",
            {"token": token},
            ["Error. Timed Out."]
        )

    # cleanup the gpm object
    gpm.cleanup()

    # Delete reference to it from our persistent_store to clear memory
    del ps[token]

    return JsonResponse(
        200,
        "API access enabled",
        {"token": token}
    )
