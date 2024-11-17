import disnake
from disnake.ext import commands
from services.interfaces import RanksCogAdminInterface, RanksCogMemberInterface

class AdminCog(commands.Cog, RanksCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

class MemberCog(commands.Cog, RanksCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(AdminCog())
    bot.add_cog(MemberCog())
