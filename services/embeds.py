import disnake


class Footer(disnake.Embed):
    def __init__(
        self,
        title: str = '',
        description: str = '',
        footer_text: str = '',
        **kwargs
    ):
        super().__init__(title=title, description=description, **kwargs)
        self.set_footer(text=footer_text)


class Success(Footer):
    def __init__(
        self,
        title: str = 'Успешно',
        description: str = '',
        footer_text: str = '',
        **kwargs
    ):
        super().__init__(title=title, description=description, footer_text=footer_text, **kwargs)
        self.color = disnake.Color.green()


class Error(Footer):
    def __init__(
        self,
        title: str = 'Ошибка',
        description: str = '',
        footer_text: str = '',
        **kwargs
    ):
        super().__init__(title=title, description=description, footer_text=footer_text, **kwargs)
        self.color = disnake.Color.red()


class Info(Footer):
    def __init__(
        self,
        title: str = 'Информация',
        description: str = '',
        footer_text: str = '',
        **kwargs
    ):
        super().__init__(title=title, description=description, footer_text=footer_text, **kwargs)
        self.color = disnake.Color.blue()


class AdminPerError(Error):
    def __init__(
        self,
        title = 'Ошибка',
        description = 'Вам необходимо иметь права администратора для выполнения этой команды',
        footer_text = '',
        **kwargs
    ):
        super().__init__(title, description, footer_text, **kwargs)
