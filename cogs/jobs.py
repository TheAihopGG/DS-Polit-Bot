import disnake
from disnake.ext import commands
from services.interfaces import JobsCogAdminInterface, JobsCogMemberInterface

class JobsAdminCog(commands.Cog, JobsCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

class JobsMemberCog(commands.Cog, JobsCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(JobsAdminCog(bot))
    bot.add_cog(JobsMemberCog(bot))
