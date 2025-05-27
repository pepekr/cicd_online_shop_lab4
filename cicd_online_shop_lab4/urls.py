from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users.views import register_view, login_view, logout_view
from store import views
from store import views_separated

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('registration/', register_view, name='registration'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
