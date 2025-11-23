from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    # Redirección temporal de /checkout a /order-summary
    path('checkout/', RedirectView.as_view(url='/order-summary/', permanent=False)),

    # Incluye todas las rutas de la app core
    path('', include(('core.urls', 'core'), namespace='core')),

    # API Token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Endpoints
    path('api/', include('core.api.urls')),
]

# Debug Toolbar solo si DEBUG=True
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
