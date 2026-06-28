from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def test_s3(request):
    import boto3
    from botocore.client import Config
    from botocore import exceptions
    import os
    
    try:
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        path = default_storage.save('test-django-storage.txt', ContentFile(b'hello from django storage'))
        url = default_storage.url(path)
        return HttpResponse(f'SUCCESS: {url}')
    except Exception as e:
        import traceback
        return HttpResponse(f'FAILED: {type(e).__name__}: {e}\n\n{traceback.format_exc()}', content_type='text/plain')
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-s3/', test_s3),
    path('', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
