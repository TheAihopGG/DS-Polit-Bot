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
                await inter.response.send_message(embed=Success(description='Сервер занесён в базу данных!'))
            
    @commands.slash_command(name='set-member-role')
    @commands.has_permissions(administrator=True)
    async def set_member_role(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role
    ):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(''' 
                UPDATE towns 
                SET town_role_id = ? 
                WHERE guild_id = ? 
            ''', (role.id, inter.guild_id)) as cursor:
                if cursor.rowcount > 0:
                    await inter.response.send_message(embed=Success(description=f'Роль успешно обновлена на: {role.mention}', footer_text="квилтон гей"), ephemeral=True)
                else:
                    await inter.response.send_message(embed=Error(description='Город не найден. Пожалуйста, вызовите команду /setup для настройки.'), ephemeral=True)

            await db.commit()
    
    @commands.slash_command(name='remove-member')
    @commands.has_permissions(administrator=True)
    async def remove_member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        async with aiosqlite.connect(DB_PATH) as db:
            if result := await (await db.execute('''
                SELECT town_role_id FROM towns
                WHERE guild_id = ?;
            ''', (inter.guild_id,))).fetchone():
                [town_role_id] = result
                result = await db.execute('''
                    DELETE FROM users 
                    WHERE user_id = ? AND town_id = ?;
                ''', (member.id, inter.guild_id))
                await db.commit()
                if result.rowcount > 0:
                    await member.remove_roles(inter.guild.get_role(town_role_id))
                    await inter.response.send_message(embed=Success(description=f'Пользователь <@&{member.id}> удален из базы данных!'), ephemeral=True)
                else:
                    await inter.response.send_message(embed=Error(description=f'Пользователь <@&{member.id}> не найден в базе данных.'), ephemeral=True)

    @commands.slash_command(name='add-member')
    @commands.has_permissions(administrator=True)
    async def add_member(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        async with aiosqlite.connect(DB_PATH) as db:
            if result := await (await db.execute('''
                SELECT town_role_id FROM towns
                WHERE guild_id = ?;
            ''', (inter.guild_id,))).fetchone():
                [town_role_id] = result
                
                existing_user = await (await db.execute('''
                    SELECT * FROM users
                    WHERE user_id = ? AND town_id = ?;
                ''', (member.id, inter.guild_id))).fetchone()

                if existing_user:
                    await inter.response.send_message(embed=Error(description=f'Пользователь <@{member.id}> уже существует в базе данных!'))
                else:
                    await db.execute('''
                        INSERT INTO users
                        VALUES (?, ?, ?, ?, ?);
                    ''', (member.id, 0, inter.guild_id, 0, 0)) 
                    await db.commit()
                    await member.add_roles(inter.guild.get_role(town_role_id))
                    await inter.response.send_message(embed=Success(description=f'Пользователь <@&{member.id}> добавлен в базу данных!'))
            else:
                await inter.response.send_message(embed=Error(description='Такого города не существует в базе данных'))

    @commands.slash_command(name='edit-town-description')
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
                await inter.response.send_message(embed=Success(description=f'Описание обновлено на {description}'))
            else:
                await inter.response.send_message(embed=Error(description='Такого города не существует в базе данных'))
            await db.commit()


class CommonMemberCog(commands.Cog, CommonCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name='members-list')
    async def members_list(self, inter: disnake.ApplicationCommandInteraction):
        async with aiosqlite.connect(DB_PATH) as db:
            if result := await (await db.execute('''
                SELECT * FROM users
                WHERE town_id = ? 
            ''', (inter.guild_id,))).fetchall():
                embed_description = 'Список пользователей:\n'
                print(result)

                embed_description = 'Список пользователей:\n' + '\n'.join([f'<@{user_id}>, <@&{rank_id}>, <@&{job_id}>, очков: {points}\n' for [user_id, rank_id, town_id, job_id, points] in result])
                print(embed_description)
                embed = Info(description=embed_description)
                
                await inter.response.send_message(embed=embed)
            else:
                await inter.response.send_message(embed=Error(description='В этом городе нету участников'))

    @commands.slash_command(name='town-description')
    async def town_description(self, inter: disnake.ApplicationCommandInteraction):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''
                SELECT town_description FROM towns
                WHERE guild_id = ?
            ''', (inter.guild_id,)) as cursor:
                if result := await cursor.fetchone():
                    [town_description] = result
                    await inter.response.send_message(embed=Info(description=f'Описание вашего города:\n{town_description}'))
                else:
                    await inter.response.send_message(embed=Error(description='Описание города не найдено'))


def setup(bot: commands.Bot):
    bot.add_cog(CommonAdminCog(bot))
    bot.add_cog(CommonMemberCog(bot))
