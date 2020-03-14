from redbot.core import commands, config
from redbot.core.utils import menus
import discord
import asyncio

class Mafia(commands.Cog):
    """My custom cog"""

    @commands.group()
    async def mafia(self, ctx):
        """This is Mafia"""

    @mafia.command()
    async def join(self, ctx):
        """Join Mafia Game"""
        guild = ctx.guild
        user = ctx.author
        role_mafia = self.get_mafia_role(ctx)

        if role_mafia is None: 
            role_mafia = await guild.create_role(name="Mafia")
        
        await user.add_roles(role_mafia)

        await ctx.send("You have joined the mafia game!")

    @mafia.command()
    async def leave(self, ctx):
        """Leave Mafia Game"""
        user = ctx.author
        await self.remove_mafia_role(ctx)

        embed = discord.Embed(description=user.mention+" has left the game")
        await ctx.send(embed=embed)

    @mafia.command()
    async def start(self, ctx, gamemode = "standard"):
        """Start Mafia Game"""
        
        if len(self.get_mafia_players(ctx)) == 0:
            await ctx.send("There are no players currently playing. Unable to start the round.")
            return

        await self.start_round(ctx, gamemode=gamemode)    

    @mafia.command()
    async def end(self, ctx):
        """End Mafia Game"""
        channel_mafia = self.get_mafia_channel(ctx)
        role_mafia = self.get_mafia_role(ctx)

        if channel_mafia is not None:
            await channel_mafia.delete()

        for user in self.get_mafia_players(ctx):
            await self.remove_mafia_role(ctx, user=user)

        await role_mafia.delete()

        embed = discord.Embed(description="The game has ended", color=0xF50202)
        await ctx.send(embed=embed)

    def get_mafia_role(self, ctx):
        guild = ctx.guild

        for role in guild.roles:
            if role.name == "Mafia":
                return role
        return None

    def get_mafia_channel(self, ctx):
        guild = ctx.guild

        for channel in guild.text_channels:
            if channel.name == "mafia":
                return channel
        return None

    async def remove_mafia_role(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        role = self.get_mafia_role(ctx)

        if role in user.roles:
            await user.remove_roles(role)

    def get_mafia_players(self, ctx):
        guild = ctx.guild
        role_mafia = self.get_mafia_role(ctx)
        current_players = []
        
        for user in guild.members:
            if role_mafia in user.roles:
                current_players.append(user)

        return current_players
        
    async def start_round(self, ctx, gamemode):
        guild = ctx.guild
        role_mafia = self.get_mafia_role(ctx)
        channel_mafia = self.get_mafia_channel(ctx)
        current_players = self.get_mafia_players(ctx)
        current_players_mention = " "
        emojis = ['✅','❎']
        if role_mafia is None:
            role_mafia = await guild.create_role(name="Mafia")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role_mafia: discord.PermissionOverwrite(read_messages=True),
            role_mafia: discord.PermissionOverwrite(send_messages=True)
        }

        if channel_mafia is None:
            channel_mafia = await guild.create_text_channel("mafia", overwrites=overwrites)

        for user in current_players:
            current_players_mention = current_players_mention + user.mention + " "

        embed = discord.Embed(title="Mafia Game", description="This is the start of your "+gamemode+" game", color=0xF50202)
        embed.add_field(name="Current Players: ", value=current_players_mention, inline=True)
        
        await channel_mafia.send("@Mafia", embed=embed)

        message = await channel_mafia.send("test")
        await start_adding_reactions(message, emojis)
        
        