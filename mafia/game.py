import asyncio
import random
from typing import List, Set

import discord
from redbot.core import commands

from .player import Player
from .role import Role

class Game:
    """
    Class to run a game of Rocket League Mafia
    """

    roles: List[Role]
    players: List[Player]

    def __init__(self, guild: discord.Guild, role: discord.Role = None,
                category: discord.CategoryChannel = None, village: discord.TextChannel = None):
        self.guild = guild
        
        self.roles = []
        self.players = []

        self.vote_totals = {}

        self.started = False

        self.vote_time = False
        self.round_count = 0

        self.game_role = role
        self.channel_category = category
        self.village_channel = village

        self.to_delete = Set()

    async def setup(self, ctx: commands.Context):
        """
        Setup

        1. Assign Roles
        2. Create Channels
          a. Channel Permissions
        3. Start Game
        """
        self.get_roles(ctx)

        if self.game_role is None:
            try:
                self.game_role = await ctx.guild.create_role(name="Mafia Players", 
                                                            mentionable=True,  
                                                            reason="(BOT) Mafia game role")
                self.to_delete.add(self.game_role)
            except (discord.Forbidden, discord.HTTPException):
                await ctx.send("Issue creating game role, cannot start the game")
            return False

    def get_roles(self, ctx):
        game_size = len(self.players)

        await ctx.send("Test")
        