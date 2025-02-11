from django.urls import re_path
from core.consumers import DataPipelineConsumer

websocket_urlpatterns = [
    re_path(r'^ws/data_pipeline/$', DataPipelineConsumer.as_asgi()),
]
