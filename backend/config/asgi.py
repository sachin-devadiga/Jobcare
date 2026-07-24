import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns as chat_ws
from notifications.routing import websocket_urlpatterns as notification_ws

import os
from django.conf import settings

if os.environ.get('DJANGO_SETTINGS_MODULE', '') == 'config.test_settings':
    application = ProtocolTypeRouter({
        'http': django_asgi_app,
        'websocket': AuthMiddlewareStack(
            URLRouter(
                chat_ws + notification_ws,
            )
        ),
    })
else:
    application = ProtocolTypeRouter({
        'http': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    chat_ws + notification_ws,
                )
            )
        ),
    })
