import uuid
from web_server.entities import Response, JsonResponse
from headless_api.gst_portal_mapper import GSTPortalMapper


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

    token = uuid.uuid4().hex

    gpm = GSTPortalMapper()
    base64 = gpm.get_captcha_base64()

    ps[token] = {
        "token": token,
        "gpm": gpm
    }

    response_data = {
        "token": token,
        "captcha_base64": base64
    }

    return JsonResponse(200, "Token generated", response_data)
