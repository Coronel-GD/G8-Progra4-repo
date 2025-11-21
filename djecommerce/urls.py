from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    # Redirección temporal de /checkout a /order-summary
    path('checkout/', RedirectView.as_view(url='/order-summary/', permanent=False)),

    # Incluye todas las rutas de la app core
    path('', include(('core.urls', 'core'), namespace='core')),
]

# Debug Toolbar solo si DEBUG=True
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
