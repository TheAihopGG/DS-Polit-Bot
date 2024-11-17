import disnake
from disnake.ext import commands
from services.interfaces import PointsCogAdminInterface, PointsCogMemberInterface

class PointsAdminCog(commands.Cog, PointsCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

class PointsMemberCog(commands.Cog, PointsCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(PointsAdminCog(bot))
    bot.add_cog(PointsMemberCog(bot))
