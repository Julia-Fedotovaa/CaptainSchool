from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.users.api_urls")),
    path("", include("apps.users.urls")),
    path("education/", include("apps.education.urls")),
    path("students/", include("apps.students.urls")),
    path("trajectories/", include("apps.trajectories.urls")),
    path("progress/", include("apps.progress.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
