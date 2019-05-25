from web_server.entities import Response, JsonResponse


def ping(request):
    if request.method == "GET":
        return Response(200, "PING OK")

    if request.method == "POST":
        return JsonResponse(200, "PING OK", request.data)
