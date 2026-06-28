from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def test_s3(request):
    import urllib.request
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import traceback
    
    try:
        # Download a small test image
        url = 'https://httpbin.org/image/jpeg'
        with urllib.request.urlopen(url) as response:
            image_data = response.read()
        
        path = default_storage.save('products/test-real-image.jpeg', ContentFile(image_data))
        url = default_storage.url(path)
        return HttpResponse(f'SUCCESS: {url}')
    except Exception as e:
        return HttpResponse(f'FAILED: {type(e).__name__}: {e}\n\n{traceback.format_exc()}', content_type='text/plain')
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-s3/', test_s3),
    path('', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
