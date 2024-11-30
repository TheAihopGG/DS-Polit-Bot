import disnake
import aiosqlite
from data.settings import *
from disnake.ext import commands
from services.embeds import *
from services.interfaces import JobsCogAdminInterface, JobsCogMemberInterface

class JobsAdminCog(commands.Cog, JobsCogAdminInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
    
    @commands.slash_command(name='give-job')
    async def give_job(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        role: disnake.Role
    ):
        if inter.author.guild_permissions.administrator:
            async with aiosqlite.connect(DB_PATH) as db:
                jobs_ids = [r[0] for r in await (await db.execute('''
                    SELECT * FROM jobs
                    WHERE town_id=?
                ''', (inter.guild_id,))).fetchall()]
                if role.id in jobs_ids:
                    async with db.execute('''
                        UPDATE users
                        SET job_id=?
                        WHERE user_id=?
                    ''', (role.id, member.id)) as cursor:
                        if cursor.rowcount > 0:
                            await member.add_roles(role)
                            await inter.response.send_message(embed=Success(description=f'Вы выдали должность участнику <@{inter.author.id}> (<@&{role.id}>)'))
                        else:
                            await inter.response.send_message(embed=Error(description='Пользователь не является участником города'))
                        await db.commit()
                else:
                    await inter.response.send_message(embed=Error(description=f'Роль <@&{role.id}> не является должностью'))
        else:
            await inter.response.send_message(embed=AdminPerError())
    
    @commands.slash_command(name='take-job')
    async def take_job(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member
    ):
        if inter.author.guild_permissions.administrator:
            async with aiosqlite.connect(DB_PATH) as db:
                result = await (await db.execute('''
                    SELECT job_id FROM users
                    WHERE town_id=? AND user_id=?    
                ''', (inter.guild_id, member.id))).fetchall()
                if result is not None:
                    [job_id] = result
                    async with db.execute('''
                        UPDATE users
                        SET job_id=NULL
                        WHERE user_id=?
                    ''', (member.id,)) as cursor:
                        if cursor.rowcount > 0:
                            await member.remove_roles(inter.guild.get_role(job_id))
                            await inter.response.send_message(embed=Success(description=f'Вы забрали должность у <@{inter.author.id}> (<@&{job_id}>)'))
                        else:
                            await inter.response.send_message(embed=Error(description='Пользователь не является участником города'))
                        await db.commit()
                else:
                    await inter.response.send_message(embed=Error(description='Пользователь не является участником города'))
        else:
            await inter.response.send_message(embed=AdminPerError())
    
    @commands.slash_command(name='add-job')
    async def add_job(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role,
        description: str
    ):
        if inter.author.guild_permissions.administrator:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute('''
                    INSERT OR REPLACE INTO jobs
                    VALUES (?, ?, ?)
                ''', (role.id, inter.guild_id, description)) as cursor:
                    if cursor.rowcount > 0:
                        embed = Success(description='Добавлена новая должность')
                        [embed.add_field(opt_name, opt_value) for [opt_name, opt_value] in zip(
                            ['Роль', 'Описание'],
                            [role.mention, description]
                        )]
                        await inter.response.send_message(embed=embed)
                    else:
                        await inter.response.send_message(embed=Error(description='Не удалось добавить должность'))
                    await db.commit()
        else:
            await inter.response.send_message(embed=AdminPerError())
    
    @commands.slash_command(name='edit-job')
    async def edit_job(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role,
        new_role: disnake.Role | None = None,
        new_description: str | None = None
    ):
        if inter.author.guild_permissions.administrator:
            new_role = new_role or role
            async with aiosqlite.connect(DB_PATH) as db:
                if result := await (await db.execute('''
                    SELECT job_description FROM jobs
                    WHERE job_id=?
                ''', (role.id,))).fetchone():
                    [description] = result
                    new_description = new_description or description
                    async with db.execute('''
                        UPDATE jobs
                        SET job_id=?, job_description=?
                    ''', (new_role.id, new_description)) as cursor:
                        if cursor.rowcount:
                            if result := await (await db.execute('''
                                SELECT user_id FROM users
                                WHERE job_id = ? AND town_id = ?
                            ''', (role.id, inter.guild_id))).fetchall():
                                for user_id in (row[0] for row in result):
                                    await db.execute('''
                                        UPDATE users
                                        SET job_id=?
                                        WHERE user_id=?
                                    ''', (new_role.id, user_id))
                            embed = Success(description=f'Отредактирована должность {role.name}. Новые значения:')
                            [embed.add_field(opt_name, 'Без изменений' if opt_value == old_opt_value else opt_value) for [opt_name, opt_value, old_opt_value] in zip(
                                ['Роль', 'Описание'],
                                [new_role.name, new_description],
                                [role.name, description]
                            )]
                            await inter.response.send_message(embed=embed, ephemeral=True)
                        else:
                            await inter.response.send_message(embed=Error(description=f'Должность <@&{role.id}> не существует'), ephemeral=True)
                        await db.commit()
                else:
                    await inter.response.send_message(embed=Error(description='Такой должности не существует'))
        else:
            await inter.response.send_message(embed=AdminPerError())
    
    @commands.slash_command(name='remove-job')
    async def remove_job(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role
    ):
        if inter.author.guild_permissions.administrator:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute('''
                    DELETE FROM jobs
                    WHERE rank_id=? AND town_id=?
                ''', (role.id, inter.guild_id)) as cursor:
                    if cursor.rowcount:
                        await inter.response.send_message(embed=Success(description=f'Удалёна должность <@&{role.id}>'), ephemeral=True)
                    else:
                        await inter.response.send_message(embed=Error(description=f'Должность <@&{role.id}> не существует'), ephemeral=True)
                await db.commit()
        else:
            await inter.response.send_message(embed=AdminPerError())

class JobsMemberCog(commands.Cog, JobsCogMemberInterface):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
    
    @commands.slash_command(name='jobs-list')
    async def jobs_list(self, inter: disnake.ApplicationCommandInteraction):
        async with aiosqlite.connect(DB_PATH) as db:
            if result := await (await db.execute('''
                SELECT job_id, job_description FROM jobs
                WHERE town_id=?
            ''', (inter.guild_id,))).fetchall():
                embed = Info(description='Должности:')
                [embed.add_field(inter.guild.get_role(job_id).name, job_description) for [job_id, job_description] in result]
                await inter.response.send_message(embed=embed, ephemeral=True)
            else:
                await inter.response.send_message(embed=Error(description='На этом сервере нету должностей'))
    
    @commands.slash_command(name='refuse-job')
    async def refuse_job(self, inter: disnake.ApplicationCommandInteraction):
        async with aiosqlite.connect(DB_PATH) as db:
            result = await (await db.execute('''
                SELECT job_id FROM users
                WHERE town_id=? AND user_id=?    
            ''', (inter.guild_id, inter.author.id))).fetchall()
            if result is not None:
                [job_id] = result[0]
                async with db.execute('''
                    UPDATE users
                    SET job_id=NULL
                    WHERE user_id=?
                ''', (inter.author.id,)) as cursor:
                    if cursor.rowcount > 0:
                        await inter.author.remove_roles(inter.guild.get_role(job_id))
                        await inter.response.send_message(embed=Success(description=f'Вы отказались от должности <@&{job_id}>'))
                    else:
                        await inter.response.send_message(embed=Error(description='Вы не являетесь участником города'))
                    await db.commit()
            else:
                await inter.response.send_message(embed=Error(description='Вы не являетесь участником города'))
    
    @commands.slash_command(name='job')
    async def job(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member | None = None
    ):
        member = member or inter.author
        async with aiosqlite.connect(DB_PATH) as db:
            if result := await (await db.execute('''
                SELECT job_id, job_description FROM users
                WHERE town_id=? AND user_id=?
            ''', (inter.guild_id, member.id))).fetchone():
                [job_id, job_description] = result
                embed = Info(description=f'**Должность <@{member.id}>:** <@&{job_id}>' if job_id else f'У <@{member.id}> нету должности')
                embed.add_field('Описание', job_description)
                await inter.response.send_message(embed=embed, ephemeral=True)

            else:
                await inter.response.send_message(embed=Error(description='Вы не являетесь участником города'), ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(JobsAdminCog(bot))
    bot.add_cog(JobsMemberCog(bot))
