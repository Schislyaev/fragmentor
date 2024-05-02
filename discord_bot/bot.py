from functools import lru_cache

import discord
from aiohttp import web

from core.settings import settings

intents = discord.Intents.all()


class DiscordClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.app = web.Application()
        self.app.add_routes([web.post('/discord/create_channel', self.handle_create_channel)])

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, settings.discord_host, 8888)
        await site.start()

    async def handle_create_channel(self, request):
        data = await request.json()
        guild_id = data['guild_id']
        channel_name = data['channel_name']
        invite1, invite2 = await self.create_channel(guild_id, channel_name)

        return web.json_response({'link1': invite1, 'link2': invite2})

    async def on_message(self, message):

        # Не реагируйте на сообщения от самого бота
        if message.author == self.user:
            return

        ...

    async def create_channel(self, guild_id: int, channel_name):
        # await self.wait_until_ready()
        guild = self.get_guild(guild_id)
        # Получаем роль администратора на сервере
        admin_role = discord.utils.get(guild.roles, name="Админ")

        # Настройка разрешений
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            admin_role: discord.PermissionOverwrite(view_channel=True, connect=True)
        }

        # Создание канала
        voice_channel = await guild.create_voice_channel(name=channel_name, overwrites=overwrites)
        print(f'Created a private voice channel: {voice_channel.name}')

        # Создание и вывод ссылки-приглашения в консоль (или отправка куда-либо ещё)
        invite1 = await voice_channel.create_invite(max_uses=0, unique=True)
        invite2 = await voice_channel.create_invite(max_uses=0, unique=True)

        return invite1.url, invite2.url


@lru_cache()
def get_discord() -> DiscordClient:
    return DiscordClient()


if __name__ == '__main__':
    client = get_discord()
    client.run(settings.discord_token)
