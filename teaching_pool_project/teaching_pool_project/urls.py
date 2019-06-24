from django.conf.urls import url
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django_tequila.urls import urlpatterns as django_tequila_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('', include('web.urls')),
    path('api/', include('api.urls')),
]
urlpatterns += django_tequila_urlpatterns

if settings.DEBUG:
    print("importing debug_toolbar")
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns
