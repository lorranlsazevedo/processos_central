from django.utils.deprecation import MiddlewareMixin
import threading


class ProcessoMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.endswith('/admin/extracao_pdf/processo/add/'):
            numero_processo = request.GET.get('numero_processo')
            if numero_processo:
                request.session['numero_processo_temp'] = numero_processo

# middleware.py

_user = threading.local()

def get_current_user():
    return getattr(_user, 'value', None)

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user
        response = self.get_response(request)
        return response

