import discord

from redbot.core import Config, checks, commands

from typing import Any

Cog: Any = getattr(commands, "Cog", object)

class Mafia(Cog):
    """
    Main to host Rocket Leauge Mafia on guild
    """

    def __init__(self):
        self.config = Config.get_conf(self, identifier=926792766, force_registration=True)
        default_global = {}
        default_guild = {
            "role_id": None,
            "category_id": None,
            "channel_id": None,
            "log_channel_id": None
        }

        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

        self.games = {}

    def __unload(self):
        print("Unload called")
        for game in self.games.values():
            del game
    
    