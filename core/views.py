# core/views.py

from django.http import JsonResponse

def health_check(request):
    """
    Una vista simple que devuelve un estado 'ok'.
    Render la usará para comprobar que el servicio está vivo.
    """
    return JsonResponse({"status": "ok", "message": "Service is healthy"})