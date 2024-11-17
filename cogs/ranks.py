import disnake
from disnake.ext import commands
from services.interfaces import RanksCogAdminInterface, RanksCogMemberInterface

class RanksAdminCog(commands.Cog, RanksCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

class RanksMemberCog(commands.Cog, RanksCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(RanksAdminCog(bot))
    bot.add_cog(RanksMemberCog(bot))
