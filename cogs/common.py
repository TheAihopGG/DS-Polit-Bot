import disnake
import aiosqlite
from data.settings import *
from disnake.ext import commands
from services.embeds import *
from services.interfaces import CommonCogAdminInterface, CommonCogMemberInterface


class CommonAdminCog(commands.Cog, CommonCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name='setup')
    @commands.has_permissions(administrator=True)
    async def setup(self, inter: disnake.ApplicationCommandInteraction):  
        async with aiosqlite.connect(DB_PATH) as db:
            check = await (await db.execute('''
                SELECT * FROM towns                  
                WHERE guild_id = ?;
            ''', (inter.guild_id,))).fetchone()

            if check is not None:
                await inter.response.send_message(embed=Error(description='Вы уже использовали эту команду!' ), ephemeral=True)
            else:
                await db.execute('''
                    INSERT INTO towns (guild_id, town_role_id, town_name, town_description)
                    VALUES (?, ?, ?, ?);
                ''', (inter.guild_id, None , inter.guild.name, None))

                await db.commit()
                await inter.response.send_message(embed=Success('Сервер занесён в базу данных!'))
            
    @commands.slash_command(name='set-member-role')
    @commands.has_permissions(administrator=True)
    async def set_member_role(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role
    ):
        async with aiosqlite.connect(DB_PATH) as db:
            # Пытаемся обновить роль города
            async with db.execute(''' 
                UPDATE towns 
                SET town_role_id = ? 
                WHERE guild_id = ? 
            ''', (role.id, inter.guild_id)) as cursor:
                if cursor.rowcount > 0:
                    # Если запись была успешно обновлена
                    await inter.response.send_message(embed=Success(description=f'Роль успешно обновлена на: {role.mention}', footer_text="квилтон гей"), ephemeral=True)
                else:
                    # Если запись о городе не найдена, отправляем сообщение об ошибке
                    await inter.response.send_message(embed=Error(description='Город не найден. Пожалуйста, вызовите команду /setup для настройки.'), ephemeral=True)

            await db.commit()
    
    @commands.slash_command(name='remove_member')
    @commands.has_permissions(administrator=True)
    async def remove_member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        async with aiosqlite.connect(DB_PATH) as db:
            result = await db.execute('''
                DELETE FROM users 
                WHERE user_id = ? AND town_id = ?;
            ''', (member.id, inter.guild_id))
            await db.commit()

        if result.rowcount > 0:
            await inter.response.send_message(embed=Success(f'Пользователь <@&{member.id}> удален из базы данных!'), ephemeral=True)
        else:
            await inter.response.send_message(embed=Error(f'Пользователь <@&{member.id}> не найден в базе данных.'), ephemeral=True)

    @commands.slash_command(name='add_member')
    @commands.has_permissions(administrator=True)
    async def add_member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        async with aiosqlite.connect(DB_PATH) as db:
            existing_user = await (await db.execute('''
                SELECT * FROM users
                WHERE user_id = ? AND town_id = ?;
            ''', (member.id, inter.guild_id))).fetchone()

            if existing_user:
                await inter.response.send_message(f'Пользователь @{member.name} уже существует в базе данных!')
                return

            await db.execute('''
                INSERT INTO users
                VALUES (?, ?, ?, ?, ?);
            ''', (member.id, 0, inter.guild_id, 0, 0)) 
            await db.commit()

        await inter.response.send_message(f'Пользователь {member.name} добавлен в базу данных!')

    @commands.slash_command(name='edit_town_description')
    @commands.has_permissions(administrator=True)
    async def edit_town_description(self, inter: disnake.ApplicationCommandInteraction, description: str): 
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''
                SELECT town_name FROM towns
                WHERE guild_id = ?;
            ''', (inter.guild_id,)) as cursor:
                town = await cursor.fetchone()

            if town:
                town_name = town[0]  
                await db.execute('''
                    UPDATE towns SET town_description = ?
                    WHERE guild_id = ?;
                ''', (description, inter.guild_id))
                await inter.response.send_message(f"Топик для города '{town_name}' обновлен на: '{description}'.", ephemeral=True)
            else:
                await inter.response.send_message(f'Город не найден в базе данных для этой гильдии. Используйте /setup', ephemeral=True)
            await db.commit()


class CommonMemberCog(commands.Cog, CommonCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name='members_list')
    async def members_list(self, inter: disnake.ApplicationCommandInteraction):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(''' 
                SELECT town_role_id FROM towns WHERE guild_id = ?; 
            ''', (inter.guild_id,)) as cursor:
                if role := await cursor.fetchone():
                    role_id = role[0]
                else:
                    await inter.response.send_message('Роль города не найдена.', ephemeral=True)
                    return

            if members := await (await db.execute('''
                SELECT user_id FROM users
                WHERE town_id = ? 
            ''', (inter.guild_id,))).fetchall():
                member_names = [f'<@{user_id}>' if any(role.id == role_id for role in (await inter.guild.fetch_member(user_id)).roles) else None for user_id in [member[0] for member in members]]
                await inter.response.send_message('Список пользователей:\n' + '\n'.join(member_names))
            else:
                await inter.response.send_message('В базе данных нет пользователей для этой гильдии.')

    @commands.slash_command(name='town_description')
    async def town_description(self, inter: disnake.ApplicationCommandInteraction):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''
                SELECT town_description FROM towns
                WHERE guild_id = ?
            ''', (inter.guild_id,)) as cursor:
                if town_description := await cursor.fetchone():
                    await inter.response.send_message(f'Описание вашего города:\n{town_description[0]}')
                else:
                    await inter.send('ГОЙДАААА', ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(CommonAdminCog(bot))
    bot.add_cog(CommonMemberCog(bot))
