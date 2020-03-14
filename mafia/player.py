import discord

class Player:
    """
    Base Player class for Mafia game
    """

    def __init__(self, member: discord.Member):
        self.member = member
        self.mention = member.mention
        self.role = None
        self.id = None

    async def assign_role(self, role):
        """
        Give this player a role
        """
        role.player = self
        self.role = role

    async def send_dm(self, message):
        try:
            await self.member.send(message)  # Lets do embeds later
        except discord.Forbidden:
            await self.role.game.village_channel.send("Couldn't DM to {}".format(self.mention))