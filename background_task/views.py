
from rest_framework.decorators import api_view
from .background_worker import BackgroundWorker
from rest_framework.response import Response


# To start a background worker
@api_view(["Get"])
def startWorker(request):
    try:
        if request.method == "GET":
            background_worker = BackgroundWorker()
            background_worker.start()
            return Response({"message": "Background worker started"}, status=200)
        else:
            return Response({"message": "Invalid request method"}, status=405)
    except Exception as e:
        return Response({"message": str(e)}, status=500)
