import disnake
import aiosqlite
from disnake.ext import commands
from data.settings import DB_PATH
from services.embeds import Success, Error, AdminPerError, Info
from services.interfaces import PointsCogAdminInterface, PointsCogMemberInterface

class PointsAdminCog(commands.Cog, PointsCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name='give_points')
    async def give_points(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description='Пользователь'),
        amount: int = commands.Param(description='Количество очков')
    ):  
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message(embed=AdminPerError, ephemeral=True)
            return

        if amount <= 0:
            await inter.response.send_message(
                embed=Error(description="Ошибка: Количество очков должно быть больше нуля."),
                ephemeral=True
            )
            return

        amount = abs(amount)

        try:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute('BEGIN TRANSACTION'):
                    cursor = await db.execute('''
                        SELECT points FROM users WHERE user_id = ?
                    ''', (member.id,))
                    user = await cursor.fetchone()

                    if user is not None:
                        await db.execute('''
                            UPDATE users
                            SET points = points + ?
                            WHERE user_id = ?
                        ''', (amount, member.id))

                    else:
                        await db.execute('''
                            INSERT INTO users (user_id, points)
                            VALUES (?, ?)
                        ''', (member.id, amount))
                    await db.commit()
                await inter.response.send_message(
                    embed=Success(f"Успешно добавлены {amount} очков пользователю {member.name}."),
                    ephemeral=True
                )
        except Exception as e:
            await inter.response.send_message(
                embed=Error(f"Произошла ошибка при обновлении очков: {str(e)}"),
                ephemeral=True
            )
    
    @commands.slash_command(name='take_points')
    async def take_points(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description='Пользователь'),
        amount: int = commands.Param(description='Количество очков для изъятия')
    ):
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message(embed=AdminPerError, ephemeral=True)
            return

        if amount <= 0:
            await inter.response.send_message(
                embed=Error("Ошибка: Количество очков должно быть больше нуля."),
                ephemeral=True
            )
            return

        amount = abs(amount)

        try:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute('BEGIN TRANSACTION'):
                    cursor = await db.execute('''
                        SELECT points FROM users WHERE user_id = ?
                    ''', (member.id,))
                    user = await cursor.fetchone()

                    if user is not None:
                        current_points = user[0]
                        new_points = current_points - amount

                        if new_points < 0:
                            new_points = 0
                        await db.execute('''
                            UPDATE users
                            SET points = ?
                            WHERE user_id = ?
                        ''', (new_points, member.id))
                    else:
                        await inter.response.send_message(
                            embed=Error(f"Ошибка: Пользователь {member.name} не найден в базе данных."),
                            ephemeral=True
                        )
                        return

                    await db.commit()
                await inter.response.send_message(
                    embed=Success(f"Успешно забрано {amount} очков у пользователя {member.name}."),
                    ephemeral=True
                )
        except Exception as e:
            await inter.response.send_message(
                embed=Error(f"Произошла ошибка при обновлении очков: {str(e)}"),
                ephemeral=True
            )

    @commands.slash_command(name='zero_points')
    async def zero_points(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member
    ):
        if inter.author.guild_permissions.administrator:
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    cursor = await db.execute('''
                        SELECT points FROM users WHERE user_id = ?
                    ''', (member.id,))
                    user = await cursor.fetchone()

                    if user is not None:
                        await db.execute('''
                            UPDATE users
                            SET points = 0
                            WHERE user_id = ?
                        ''', (member.id,))
                        await db.commit()
                        await inter.response.send_message(
                            embed=Success(f"Очки пользователя {member.name} были успешно обнулены."),
                            ephemeral=True
                        )
                    else:
                        await inter.response.send_message(
                            embed=Error(f"Ошибка: Пользователь {member.name} не найден в базе данных."),
                            ephemeral=True
                        )
            except Exception as e:
                await inter.response.send_message(
                    embed=Error(f"Произошла ошибка при обнулении очков: {str(e)}"),
                    ephemeral=True
                )
        else:
            await inter.response.send_message(embed=AdminPerError, ephemeral=True)

    @commands.slash_command(name='reset_all_points')
    async def reset_all_points(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        if inter.author.guild_permissions.administrator:
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute('''
                        UPDATE users
                        SET points = 0
                    ''')
                    await db.commit()
                    await inter.response.send_message(
                        embed=Success("Очки всех пользователей были успешно обнулены."),
                        ephemeral=True
                    )
            except Exception as e:
                await inter.response.send_message(
                    embed=Error(f"Произошла ошибка при обнулении очков: {str(e)}"),
                    ephemeral=True
                )
        else:
            await inter.response.send_message(
                embed=AdminPerError,
                ephemeral=True
            )

class PointsMemberCog(commands.Cog, PointsCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
    
    @commands.slash_command(name='top_points')
    async def top_points(
        self,
        inter: disnake.ApplicationCommandInteraction
    ):
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute('''
                    SELECT COUNT(*) FROM users WHERE points > 0
                ''')
                result = await cursor.fetchone()
                if result[0] < 5:
                    await inter.response.send_message(
                        embed=Error("Недостаточно пользователей для отображения таблицы"), ephemeral=True)
                    return
                
                cursor = await db.execute('''
                    SELECT user_id, points FROM users
                    WHERE points > 0 ORDER BY points DESC LIMIT 5
                ''')
                users = await cursor.fetchall()

                if users:
                    leaderboard_message = "Топ 5 пользователей по очкам:\n"
                    for rank, user in enumerate(users, 1):
                        user_id, points = user
                        user_obj = await inter.guild.fetch_member(user_id)
                        leaderboard_message += f"{rank}. {user_obj.display_name} - {points} очков\n"
                    
                    await inter.response.send_message(embed=Info(description=leaderboard_message), ephemeral=True)
                else:
                    await inter.response.send_message(embed=Info("Нет пользователей с очками больше 1"), ephemeral=True)

        except Exception as e:
            await inter.response.send_message(embed=Error(f"Произошла ошибка: {str(e)}"), ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(PointsAdminCog(bot))
    bot.add_cog(PointsMemberCog(bot))