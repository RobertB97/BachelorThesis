from django.conf      import settings
from django.shortcuts import redirect


class AngemeldetMiddleware:
    # muss überschrieben werden, damit Middleware funktioniert
    def __init__(self, get_response):
        self.get_response = get_response
        
    # muss überschrieben werden, damit Middleware funktioniert
    def __call__(self, request):
        response = self.get_response(request)
        return response

    """
    Die Funktion wird vor jedem Ausführen einer beliebigen View-Funktion ausgeführt
    - view_func ist die View die aufgerufen werden soll
    - view_args und view_kwargs sind die view parameter
    """
    def process_view(self, request, view_func, view_args, view_kwargs): 
        """
        Wenn kein nutzername in den session daten enthalten ist und der 
        Nutzer auf eine Seite möchte, welche nicht in settings.AUTH_EXEMPT_ROUTES 
        enthalten ist, dann wird er User auf die Seite AUTH_LOGIN_ROUTE redirected 
        """ 
        
        if not request.user.is_authenticated:
            exempts = settings.AUTH_EXEMPT_ROUTES
            path    = request.path_info.strip("/")
            
            if(path not in str(exempts) or path == ""): 
                return redirect("/login/")
        else:
            # Wenn kein Pfad angegeben wurde, auf home weiterleiten
            if(request.path_info.strip("/") == ""):
                return redirect("/home/")
            # Wenn Zugriff auf Admin Panel versucht wird, nur erlaubt wenn Admin oder Supernutzer, sonst auf Home weiterleiten
            if(request.path_info.strip("/") == "admin"):
                if(not request.user.is_admin or not request.user.is_superuser):
                   return redirect("/home/") 
        