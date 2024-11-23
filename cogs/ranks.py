import disnake
import aiosqlite
from data.settings import *
from disnake.ext import commands
from services.embeds import *
from services.interfaces import RanksCogAdminInterface, RanksCogMemberInterface


class RanksAdminCog(commands.Cog, RanksCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name='add-rank')
    async def add_rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role,
        points: int
    ):
        if inter.author.guild_permissions.administrator:
            if role != inter.guild.roles[0]:
                points = abs(points)
                async with aiosqlite.connect(DB_PATH) as db:
                    async with await db.execute('''
                        INSERT OR REPLACE INTO ranks (rank_id, town_id, points_required)
                        VALUES (?, ?, ?)
                    ''', (role.id, inter.guild_id, abs(points))) as cursor:
                        if cursor.rowcount > 0:
                            embed = Success(description='Добавлен новый ранг')
                            [embed.add_field(str(opt_name), str(opt_value), inline=False) for [opt_name, opt_value] in zip(
                                ['Роль', 'Очков необходимо'],
                                [f'<@&{role.id}>', points]
                            )]
                            await inter.response.send_message(embed=embed, ephemeral=True)
                        else:
                            await inter.response.send_message(embed=Error(description=f'Ранг <@&{role.id}> уже существует'), ephemeral=True)
                        await db.commit()
            else:
                await inter.response.send_message(embed=Error(description=f'Нельзя указать {inter.guild.roles[0].mention} как роль'), ephemeral=True)
        else:
            await inter.response.send_message(embed=AdminPerError())

    @commands.slash_command(name='remove-rank')
    async def remove_rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role
    ):
        if inter.author.guild_permissions.administrator:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute('''
                    DELETE FROM ranks
                    WHERE rank_id=? AND town_id=?
                ''', (role.id, inter.guild_id)) as cursor:
                    if cursor.rowcount:
                        await inter.response.send_message(embed=Success(description=f'Удалён ранг <@&{role.id}>'), ephemeral=True)
                    else:
                        await inter.response.send_message(embed=Error(description=f'Ранг <@&{role.id}> не существует'), ephemeral=True)
                await db.commit()
        else:
            await inter.response.send_message(embed=AdminPerError())
    
    @commands.slash_command(name='edit-rank')
    async def edit_rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role,
        new_role: disnake.Role | None = None,
        new_points: int | None = None
    ):
        if inter.author.guild_permissions.administrator:
            new_role = new_role or role
            if new_role != inter.guild.roles[0]:
                async with aiosqlite.connect(DB_PATH) as db:
                    if result := await (await db.execute('''
                        SELECT points_required FROM ranks
                        WHERE rank_id=? AND town_id=?
                    ''', (role.id, inter.guild_id))).fetchone():
                        [points] = result
                        new_points = new_points or points
                    async with db.execute('''
                        UPDATE ranks
                        SET rank_id=?, points_required=?
                        WHERE rank_id=? AND town_id=?
                    ''', (new_role.id, new_points, role.id, inter.guild_id)) as cursor:
                        if cursor.rowcount:
                            if result := await (await db.execute('''
                                SELECT user_id FROM users
                                WHERE rank_id = ? AND town_id = ?
                            ''', (role.id, inter.guild_id))).fetchall():
                                for user_id in (row[0] for row in result):
                                    await db.execute('''
                                        UPDATE users
                                        SET rank_id=?
                                        WHERE user_id=?
                                    ''', (new_role.id, user_id))
                                embed = Success(description=f'Отредактирован ранг {role.name}. Новые значения:')
                                [embed.add_field(opt_name, 'Без изменений' if opt_value == old_opt_value else opt_value) for [opt_name, opt_value, old_opt_value] in zip(
                                    ['Роль', 'Очков необходимо'],
                                    [new_role.name, new_points],
                                    [role.name, points]
                                )]
                                await inter.response.send_message(embed=embed, ephemeral=True)
                        else:
                            await inter.response.send_message(embed=Error(description=f'Ранг <@&{role.id}> не существует'), ephemeral=True)
                    await db.commit()
            else:
                await inter.response.send_message(embed=Error(description=f'Нельзя указать {inter.guild.roles[0].mention} как роль'), ephemeral=True)
        else:
            await inter.response.send_message(embed=AdminPerError())


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
                await inter.response.send_message(embed=Info(description=f'**Ранг <@{member.id}>:** <@&{rank_id}>' if rank_id else f'У <@{member.id}> нету ранга'), ephemeral=True)
            else:
                await inter.response.send_message(Error(description='Вы не являетесь участником города'), ephemeral=True)

    @commands.slash_command(name='ranks-list')
    async def ranks_list(self, inter: disnake.ApplicationCommandInteraction):

        async with aiosqlite.connect(DB_PATH) as db:
            if ranks := await (await db.execute('''
                SELECT rank_id, points_required FROM ranks
                WHERE town_id=?
                ''', (inter.guild_id,)
            )).fetchall():
                embed = Info(description='Доступные ранги:')
                [embed.add_field(inter.guild.get_role(rank_id).name, f'Очков необходимо: {points_required}', inline=False) for [rank_id, points_required] in ranks]
                await inter.response.send_message(embed=embed, ephemeral=True)
            else:
                await inter.response.send_message(embed=Error(description='В этом городе нету рангов'), ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(RanksAdminCog(bot))
    bot.add_cog(RanksMemberCog(bot))
