import disnake, aiosqlite
from data.settings import *
from disnake.ext import commands
from services.interfaces import RanksCogAdminInterface, RanksCogMemberInterface

class RanksAdminCog(commands.Cog, RanksCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name='add-rank')
    @commands.has_permissions(administrator=True)
    async def add_rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role,
        points: int
    ):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT OR REPLACE INTO ranks
                VALUES (?, ?, ?)
            ''', (role.id, inter.guild_id, points))
            await db.commit()
            await inter.response.send_message('Successfully')

    @commands.slash_command(name='remove-rank')
    @commands.has_permissions(administrator=True)
    async def remove_rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role
    ):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                DELETE FROM ranks
                WHERE rank_id=? AND town_id=?
            ''', (role.id, inter.guild_id))
            await db.commit()
            await inter.response.send_message('Successfully')
    
    @commands.slash_command(name='edit-rank')
    @commands.has_permissions(administrator=True)
    async def edit_rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role,
        new_role: disnake.Role,
        points: int
    ):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                UPDATE ranks
                SET rank_id=?, points_required=?
                WHERE rank_id=? AND town_id=?
            ''', (new_role.id, points, role.id, inter.guild_id))
            await db.commit()
            await inter.response.send_message('Successfully')

class RanksMemberCog(commands.Cog, RanksCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
    
    @commands.slash_command(name='rank')
    async def rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member | None = None
    ):
        member = member or inter.author
        async with aiosqlite.connect(DB_PATH) as db:
            if result := await (await db.execute('''
                SELECT rank_id FROM users
                WHERE town_id=? AND user_id=?
            ''', (inter.guild_id, member.id))).fetchone():
                [rank_id] = result
                await inter.response.send_message(f"<@{member.id}>'s rank: {rank_id}" if rank_id else f'<@{member.id}> has not rank')
            else:
                await inter.response.send_message('You are not a member of town')

    @commands.slash_command(name='ranks-list')
    async def ranks(self, inter: disnake.ApplicationCommandInteraction):
        async with aiosqlite.connect(DB_PATH) as db:
            if ranks := await (await db.execute('''
                SELECT * FROM ranks
                WHERE town_id=?
                ''', (inter.guild_id,)
            )).fetchall():
                msg = ''
                for [rank_id, town_id, points_required] in ranks:
                    msg += f'{rank_id}, {town_id}, {points_required}\n'
                await inter.response.send_message(msg)
            else:
                await inter.response.send_message('No ranks')

def setup(bot: commands.Bot):
    bot.add_cog(RanksAdminCog(bot))
    bot.add_cog(RanksMemberCog(bot))
