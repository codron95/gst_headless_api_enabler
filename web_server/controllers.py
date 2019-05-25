from web_server.entities import Response, JsonResponse


def ping(request):
    if request.method == "GET":
        return JsonResponse(200, "PING OK", request.data)

    if request.method == "POST":
        return JsonResponse(200, "PING OK", request.data)

    if request.method == "PUT":
        message = "PING OK: {update_entity_id}".format(
            update_entity_id=request.meta["update_entity_id"]
        )
        return JsonResponse(200, message, request.data)
