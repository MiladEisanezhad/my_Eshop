from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def test_s3(request):
    import boto3
    from botocore.client import Config
    import os
    
    try:
        s3 = boto3.client(
            's3',
            endpoint_url=os.environ.get('SUPABASE_ENDPOINT_URL'),
            aws_access_key_id=os.environ.get('SUPABASE_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('SUPABASE_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('SUPABASE_REGION'),
            config=Config(signature_version='s3v4')
        )
        s3.put_object(Bucket='media', Key='railway-test.txt', Body=b'hello from railway')
        return HttpResponse('SUCCESS')
    except Exception as e:
        return HttpResponse(f'FAILED: {e}')
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-s3/', test_s3),
    path('', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
