import disnake
import aiosqlite
from data.settings import *
from disnake.ext import commands
from services.interfaces import CommonCogAdminInterface, CommonCogMemberInterface

class CommonAdminCog(commands.Cog, CommonCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    async def check_admin(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.user.guild_permissions.administrator:
            await inter.response.send_message("У вас нет прав администратора для выполнения этой команды.", ephemeral=True)
            return False
        return True

    @commands.slash_command(name='remove_member')
    async def remove_member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        if not await self.check_admin(inter):
            return
        guild_id = inter.guild.id
        user_id = member.id  

        async with aiosqlite.connect(DB_PATH) as db:

            result = await db.execute('''
                DELETE FROM users 
                WHERE user_id = ? AND guild_id = ?;
            ''', (user_id, guild_id))
            await db.commit()

        if result.rowcount > 0:
            await inter.response.send_message(f'Пользователь @{member.name} удален из базы данных!')
        else:
            await inter.response.send_message(f'Пользователь @{member.name} не найден в базе данных.')

    @commands.slash_command(name='add_member')
    async def add_member(self, inter: disnake.ApplicationCommandInteraction, username: disnake.Member):
        if not await self.check_admin(inter):
            return
        guild_id = inter.guild.id

        user = username
        for guild_member in inter.guild.members:
            if guild_member.name == username or guild_member.display_name == username:
                user = guild_member
                break

        if user is None:
            await inter.response.send_message(f'Пользователь с именем @{username} не найден.')
            return

        user_id = user.id  
        username_string = user.name  

        async with aiosqlite.connect(DB_PATH) as db:
            existing_user = await db.execute('''
                SELECT * FROM users WHERE user_id = ? AND guild_id = ?;
            ''', (user_id, guild_id))
            existing_user = await existing_user.fetchone()

            if existing_user:
                await inter.response.send_message(f'Пользователь @{username_string} уже существует в базе данных!')
                return


            await db.execute('''
                INSERT INTO users (user_id, guild_id, username, town_id)
                VALUES (?, ?, ?, ?);
            ''', (user_id, guild_id, username_string, guild_id)) 
            await db.commit()

        await inter.response.send_message(f'Пользователь {username_string} добавлен в базу данных!')


    @commands.slash_command(name='edit_town_topic')
    async def edit_town_topic(self, inter: disnake.ApplicationCommandInteraction, topic: str): 
        if not await self.check_admin(inter):
            return

        guild_id = inter.guild.id

        async with aiosqlite.connect(DB_PATH) as db:

            async with db.execute('''
                SELECT town_name FROM towns WHERE guild_id = ?;
            ''', (guild_id,)) as cursor:
                town = await cursor.fetchone()

            if town:
                town_name = town[0]  
                await db.execute('''
                    UPDATE towns SET topic = ? WHERE town_name = ? AND guild_id = ?;
                ''', (topic, town_name, guild_id))
                await inter.response.send_message(f'Топик для города "{town_name}" обновлен на: "{topic}".')
            else:
                await inter.response.send_message(f'Город не найден в базе данных для этой гильдии. Топик не обновлен.')
            await db.commit()

        
    @commands.slash_command(name='member_list')
    async def members_list(self, inter: disnake.ApplicationCommandInteraction):
        if not await self.check_admin(inter):
            return
        async with aiosqlite.connect(DB_PATH) as db:

            async with db.execute('''
                SELECT username FROM users WHERE guild_id = ?;
            ''', (inter.guild_id,)) as cursor:
                members = await cursor.fetchall()

        if members:
            member_names = [f'{member[0]}' for member in members]
            await inter.response.send_message("Список пользователей:\n" + "\n".join(member_names))
        else:
            await inter.response.send_message("В базе данных нет пользователей для этой гильдии.")
    @commands.slash_command(name='set_member_job')
    async def set_member_job(self, inter: disnake.ApplicationCommandInteraction):
        if not await self.check_admin(inter):
            return
class CommonMemberCog(commands.Cog, CommonCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(CommonAdminCog(bot))
    bot.add_cog(CommonMemberCog(bot))
