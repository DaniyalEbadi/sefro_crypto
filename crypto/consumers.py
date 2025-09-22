import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
import jwt

User = get_user_model()


class CryptoPriceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Expect token via query ?token=<JWT>
        query = parse_qs(self.scope['query_string'].decode())
        raw_token = (query.get('token') or [None])[0]
        if not raw_token:
            await self.close(code=4001)
            return
        try:
            UntypedToken(raw_token)
            payload = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=['HS256'])
            self.user_id = payload.get('user_id') or payload.get('user')
            self.user = await self.get_user(self.user_id)
            if not self.user:
                await self.close(code=4003)
                return
        except (InvalidToken, TokenError, jwt.PyJWTError):
            await self.close(code=4002)
            return
        self.symbols = set()
        await self.accept()

    @staticmethod
    async def get_user(user_id):
        try:
            return await User.objects.aget(pk=user_id)
        except Exception:
            return None

    async def receive_json(self, content, **kwargs):
        action = content.get('action')
        symbols = content.get('symbols') or []
        if action == 'subscribe':
            for s in symbols:
                sym = s.upper()
                if sym not in self.symbols:
                    self.symbols.add(sym)
                    await self.channel_layer.group_add(f'crypto_{sym}', self.channel_name)
            await self.send_json({'status': 'subscribed', 'symbols': sorted(self.symbols)})
        elif action == 'unsubscribe':
            for s in symbols:
                sym = s.upper()
                if sym in self.symbols:
                    self.symbols.remove(sym)
                    await self.channel_layer.group_discard(f'crypto_{sym}', self.channel_name)
            await self.send_json({'status': 'unsubscribed', 'symbols': sorted(self.symbols)})
        else:
            await self.send_json({'error': 'unknown_action'})

    async def disconnect(self, close_code):
        for sym in list(self.symbols):
            await self.channel_layer.group_discard(f'crypto_{sym}', self.channel_name)

    async def price_update(self, event):
        data = event.get('data')
        await self.send_json({'type': 'price', 'data': data}) 