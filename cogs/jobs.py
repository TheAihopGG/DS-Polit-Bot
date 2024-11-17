import disnake
from disnake.ext import commands
from services.interfaces import JobsCogAdminInterface, JobsCogMemberInterface

class AdminCog(commands.Cog, JobsCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

class MemberCog(commands.Cog, JobsCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(AdminCog())
    bot.add_cog(MemberCog())
