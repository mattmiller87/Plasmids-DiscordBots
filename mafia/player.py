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

    async def assign_id(self, target_id):
        self.id = target_id

    async def send_dm(self, message):
        try:
            await self.member.send(message)
        except discord.Forbidden:
            await self.role.game.village_channel.send("Couldn't DM to {}".format(self.mention))