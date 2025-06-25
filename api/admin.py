# api/admin.py

from django.contrib import admin
from .models import Jugador, Noticia, HeroSlide, Partido, Sponsor # 1. Importa todos tus modelos

# 2. Registra cada modelo para que aparezca en el panel de administración
# La forma más simple es una línea por cada modelo:

admin.site.register(Jugador)
admin.site.register(Noticia)
admin.site.register(HeroSlide)
admin.site.register(Partido)
admin.site.register(Sponsor)