import discord

from redbot.core import Config, checks, commands

from typing import Any

from .game import Game


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
            "channel_id": None
        }

        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

        self.games = {}

    def __unload(self):
        print("Unload called")
        for game in self.games.values():
            del game
    
    @commands.group()
    async def mafia(self, ctx: commands.Context):
        """
        Base command for cog
        """
        if ctx.invoked_subcommand is None:
            pass

    @commands.guild_only()
    @mafia.command(name="new")
    async def mafia_new(self, ctx: commands.Context):
        """
        Create new game to join
        """
        game = await self._new_game(ctx)
        if game is None:
            await ctx.send("Failed to create a new game")
        else:
            await ctx.send("Game is ready to join! Use `[p]mafia join`")

    @commands.guild_only()
    @mafia.command(name="join")
    async def mafia_join(self, ctx: commands.Context):
        """
        Joins a game of Mafia
        """   
        game = await self._get_game(ctx)

        if game is None:
            await ctx.send("No game to join!\nCreate a new one with `[p]mafia new`")
            return

        await game.join(ctx.author, ctx.channel)

    @commands.guild_only()
    @mafia.command(name="leave")
    async def mafia_quit(self, ctx: commands.Context, member:discord.Member=None):
        """
        Quit a game of Mafia
        """
        game = await self._get_game(ctx)

        if game is None:
            await ctx.send("No game to quit!")
            return
        
        if member is None:
            await game.leave(ctx.author, ctx.channel)
        else:
            await game.leave(member, ctx.channel)

    @commands.guild_only()
    @mafia.command(name="start")
    async def mafia_start(self, ctx: commands.Context):
        """
        Attempts to start the game
        """
        game = await self._get_game(ctx)

        if game is None:
            await ctx.send("No game to start!\nCreate a new one with `[p]mafia new`")
            return

        await game.start(ctx)

    @commands.guild_only()
    @mafia.command(name="stop")
    async def mafia_stop(self, ctx: commands.Context):
        """
        Attempts to stop the game
        """
        game = await self._get_game(ctx)

        if game is None:
            await ctx.send("No game to stop!")
            return
        
        game.game_over = True
        await ctx.send("Game has been stopped")

    
    @commands.guild_only()
    @mafia.command(name="players")
    async def mafia_players(self, ctx: commands.Context):
        """
        Get Players of current game
        """
        string_mention = " "
        game = self._get_game(ctx)

        for player in game.players:
            string_mention = string_mention + player.mention + " "

        embed = discord.Embed(title="Players in the game", description=string_mention)
        await ctx.send(embed=embed)

    async def _get_game(self, ctx: commands.Context):
        """
        Get game from current guild
        """
        guild: discord.Guild = ctx.guild

        if guild is None:
            await ctx.send("Cannot do this command from PM!")
            return None
        if guild.id not in self.games or self.games[guild.id].game_over:
            return None
        
        return self.games[guild.id]

    async def _new_game(self, ctx: commands.Context):
        """
        New game for current guild
        """
        guild: discord.Guild = ctx.guild

        if guild is None:
            await ctx.send("Cannot create new game from PM!")
            return None
        if guild.id not in self.games or self.games[guild.id].game_over:
            await ctx.send("Creating a new game...")
            self.games[guild.id] = Game(guild)
        
        return self.games[guild.id]

    