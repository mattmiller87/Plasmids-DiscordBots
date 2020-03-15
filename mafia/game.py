import asyncio
import random
from typing import List

import discord
from redbot.core import commands

from .player import Player
from .role import Role, Town, Godfather

class Game:
    """
    Class to run a game of Rocket League Mafia
    """

    roles: List[Role]
    players: List[Player]
    join_queue: List[discord.Member]
    leave_queue: List[discord.Member]

    def __init__(self, guild: discord.Guild):
        self.guild = guild
        
        self.roles = []
        self.players = []
        self.join_queue = []
        self.leave_queue = []

        self.vote_totals = {}

        self.started = False
        self.game_over = False
        self.can_vote = False
        self.round_count = 0

        self.game_role = None
        self.channel_category = None
        self.village_channel = None

    async def start(self, ctx: commands.Context):
        """
        Setup
        1. Add New Players
        2. Assign Roles
        3. Create Channels
            a. Channel Permissions
        4. Start Game
        5. Remove Leaving Players
        7. Prompt new round
            a. yes - start new round
            b. no - clean up
        """
        self.started = True
        await asyncio.sleep(30)

        # Assign Players in join_queue
        if len(self.join_queue) > 0:
            for member in self.join_queue:
                await self._join(member, ctx.channel)
            self.join_queue = []
        
        # Assign Roles


    async def join(self, member: discord.Member, channel: discord.TextChannel):
        """
        Have a member join a game
        """
        player = await self.get_player_by_member(member)

        if player is not None:
            embed = discord.Embed(description=player.mention+" is already in the game!")
            await channel.send(embed=embed)
            return

        if self.started:
            embed = discord.Embed(description="Game has already started. "+member.mention+" will be added at the start of the next round")
            await channel.send(embed=embed)
            self.join_queue.append(member)
            return

        await self._join(member, channel)

    async def leave(self, member: discord.Member, channel: discord.TextChannel = None):
        """
        Have a member quit a game
        """
        player = await self.get_player_by_member(member)

        if player is None:
            embed = discord.Embed(description=member.mention+" isn't in the game")
            await channel.send(embed=embed)
            return

        if self.started:
            embed = discord.Embed(description="Game is in progress.\n"+player.mention+" will be removed at the end of the round")
            await channel.send(embed=embed)
            self.leave_queue.append(member)
            return
        
        await self._leave(member, channel)

        embed = discord.Embed(description=player.mention+" has left the game")
        await channel.send(embed=embed)
        
    async def _leave(self, member, channel):
        """
        Remove Roles and Permisions
        """
        player = await self.get_player_by_member(member)
        
        self.players = [player for player in self.players if player.member != member]

        if self.game_role is not None:
            await member.remove_roles(*[self.game_role])

    async def _join(self, member, channel):
        """
        Add Roles and add to game
        """
        self.players.append(Player(member))

        await self.give_game_role(member, channel) 
        
        embed = discord.Embed(description=member.mention+" has joined the game")
        await channel.send(embed=embed)

    async def give_game_role(self, member, channel):
        if self.game_role is not None:
            try:
                await member.add_roles(*[self.game_role])
            except discord.Forbidden:
                await channel.send(
                    "Unable to add role **{}**\nBot is missing `manage_roles` permissions".format(self.game_role.name))

    async def get_player_by_member(self, member):
        """
        Return Player by member
        """
        for player in self.players:
            if player.member == member:
                return player
        return None

    async def set_roles(self):
        """
        Creates the roles based on number of players
        """
        for player_index in range(len(self.players)):
            if player_index == len(self.players) - 1:
                self.roles.append(Godfather())
            else:
                self.roles.append(Town())

    async def assign_roles(self):
        random.shuffle(self.roles)
        self.players.sort(key=lambda player: player.member.display_name.lower())

        if len(self.roles) != len(self.players):
            await self.village_channel.send("Unhandled error - roles!=players")
            return False

        for index, player in enumerate(self.players):
            await self.players[index].assign_role(self.roles[index])

            await player.assign_id(index)