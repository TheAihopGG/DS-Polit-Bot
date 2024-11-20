import disnake
import aiosqlite
from data.settings import *
from disnake.ext import commands
from services.interfaces import CommonCogAdminInterface, CommonCogMemberInterface


class CommonAdminCog(commands.Cog, CommonCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot


    
    async def get_town_role_id(self, inter: disnake.ApplicationCommandInteraction):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''
                SELECT town_role_id FROM towns WHERE guild_id = ?;
            ''', (inter.guild.id,)) as cursor:
                role = await cursor.fetchone()  
                if role:
                    return role[0]  
                return None
    @commands.slash_command(name='setup')
    async def setup(self, inter: disnake.ApplicationCommandInteraction):

        guild_id = inter.guild.id
        
        async with aiosqlite.connect(DB_PATH) as db:

            check = await db.execute('''
                SELECT * FROM towns                  
                WHERE guild_id = ?;
            ''', (guild_id,))
            check = await check.fetchone()

            if check is not None:
                await inter.response.send_message("Сервер уже установлен", ephemeral=True)
                return

            guild_name = inter.guild.name
            await db.execute('''
                INSERT INTO towns (guild_id, town_role_id, town_name, town_topic)
                VALUES (?, ?, ?, ?);
            ''', (guild_id, None , guild_name, "-"))

            await db.commit()
            await inter.response.send_message("Сервер успешно установлен в базу данных!\n\n Также используйте /setup_member_role и /edit_town_topic")
            db.close()
            
    @commands.slash_command(name='setup_member_role')
    async def setup_member_role(self, inter: disnake.ApplicationCommandInteraction, role: disnake.Role):
        guild_id = inter.guild.id
        
        async with aiosqlite.connect(DB_PATH) as db:
            member_role = await db.execute('''
            SELECT town_role_id FROM towns WHERE guild_id = ?
            ''', (guild_id,))
            member_role = await member_role.fetchone()
            
            if member_role is not None:
                current_role_id = member_role[0]
                current_role = inter.guild.get_role(current_role_id)
                new_role = inter.guild.get_role(role.id) 
                await db.execute('''UPDATE towns SET town_role_id = ? WHERE guild_id = ?''', (role.id, guild_id))
                await inter.response.send_message(f"Роль успешно заменена на {new_role.mention}", ephemeral=True)
            else: 
                await db.execute('''INSERT INTO towns(guild_id, town_role_id) 
                VALUES (?, ?)''', (guild_id, role.id)) 
                await inter.response.send_message(f"Роль <@{role.id}> установлена", ephemeral=True)

            await db.commit()
    @commands.slash_command(name='remove_member')
    async def remove_member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):

        guild_id = inter.guild.id
        user_id = member.id  

        async with aiosqlite.connect(DB_PATH) as db:

            result = await db.execute('''
                DELETE FROM users 
                WHERE user_id = ? AND town_id = ?;
            ''', (user_id, guild_id))
            await db.commit()

        if result.rowcount > 0:
            await inter.response.send_message(f'Пользователь @{member.name} удален из базы данных!')
        else:
            await inter.response.send_message(f'Пользователь @{member.name} не найден в базе данных.')

    @commands.slash_command(name='add_member')
    async def add_member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):

        guild_id = inter.guild.id

        user = member
        for guild_member in inter.guild.members:
            if guild_member.name == member or guild_member.display_name == member:
                user = guild_member
                break

        if user is None:
            await inter.response.send_message(f'Пользователь @{member} не найден.')
            return

        user_id = user.id  
        username_string = user.name  

        async with aiosqlite.connect(DB_PATH) as db:
            existing_user = await db.execute('''
                SELECT * FROM users WHERE user_id = ? AND town_id = ?;
            ''', (user_id, guild_id))
            existing_user = await existing_user.fetchone()

            if existing_user:
                await inter.response.send_message(f'Пользователь @{username_string} уже существует в базе данных!')
                return


            await db.execute('''
                INSERT INTO users (user_id, town_id)
                VALUES (?, ?);
            ''', (user_id, guild_id)) 
            await db.commit()

        await inter.response.send_message(f'Пользователь {username_string} добавлен в базу данных!')


    @commands.slash_command(name='edit_town_topic')
    async def edit_town_topic(self, inter: disnake.ApplicationCommandInteraction, description: str): 

        guild_id = inter.guild.id

        async with aiosqlite.connect(DB_PATH) as db:

            async with db.execute('''
                SELECT town_name FROM towns WHERE guild_id = ?;
            ''', (guild_id,)) as cursor:
                town = await cursor.fetchone()

            if town:
                town_name = town[0]  
                await db.execute('''
                    UPDATE towns SET town_topic = ? WHERE guild_id = ?;
                ''', (description, guild_id))
                await inter.response.send_message(f'Топик для города "{town_name}" обновлен на: "{description}".', ephemeral=True)
            else:
                await inter.response.send_message(f'Город не найден в базе данных для этой гильдии. Используйте /setup', ephemeral=True)
            await db.commit()

        
    @commands.slash_command(name='member_list')
    async def members_list(self, inter: disnake.ApplicationCommandInteraction):

        
        role_id = await self.get_town_role_id(inter)  # Получаем ID роли города
        if role_id is None:
            await inter.response.send_message("Роль города не найдена.", ephemeral=True)
            return
        
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''
                SELECT user_id FROM users WHERE town_id = ?;
            ''', (inter.guild.id,)) as cursor:
                members = await cursor.fetchall()
        
        if members:
            member_names = []
            for member in members:
                user_id = member[0]
                guild_member = await inter.guild.fetch_member(user_id)
                if guild_member:
                    if any(role.id == role_id for role in guild_member.roles):
                        member_names.append(f'<@{user_id}>')
                else:
                    pass

            if member_names:
                await inter.response.send_message("Список пользователей:\n" + "\n".join(member_names))
            else:
                pass
        else:
            await inter.response.send_message("В базе данных нет пользователей для этой гильдии.")

class CommonMemberCog(commands.Cog, CommonCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(CommonAdminCog(bot))
    bot.add_cog(CommonMemberCog(bot))
