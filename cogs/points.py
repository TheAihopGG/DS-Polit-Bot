import disnake
from disnake.ext import commands
from services.interfaces import PointsCogAdminInterface, PointsCogMemberInterface

class AdminCog(commands.Cog, PointsCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

class MemberCog(commands.Cog, PointsCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(AdminCog())
    bot.add_cog(MemberCog())
