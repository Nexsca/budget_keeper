# Страница главного меню - первая страница приложения, пользователь может выбрать функцию входа или регистрации
class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Импортируем интерфейс
        self.ui = Ui_MainMenuWindow()
        self.ui.setupUi(self)

        # Коннект кнопок для входа и регистрации
        self.ui.enter_button.clicked.connect(self.go_to_login)
        self.ui.reg_button.clicked.connect(self.go_to_register)

    # Редирект на страницу логина
    def go_to_login(self):
        logger.info(f"Открытие страницы входа в профиль")
        self.login_page = LoginPage()
        self.login_page.show()
        self.close()

    # Редирект на страницу регистрации
    def go_to_register(self):
        logger.info(f"Открытие страницы регистрации")
        self.register_page = RegisterPage()
        self.register_page.show()
        self.close()


# Страница входа в профиль - страница с вводом логина и пароля пользователя
class LoginPage(QMainWindow):
    def __init__(self):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Импортируем интерфейс
        self.ui = Ui_LoginPageWindow()
        self.ui.setupUi(self)

        # Коннект кнопок для входа и возврата в меню
        self.ui.login_button.clicked.connect(self.check_login)
        self.ui.back_button.clicked.connect(self.back_to_main)

    # Проверка логина на существование в базе данных
    def check_login(self):
        login = self.ui.login_input.text()
        password = self.ui.password_input.text()
        logger.info(f"Выполняется вход в профиль, логин: '{login}', пароль: '[HIDDEN]'")

        # Проверки введённых данных
        if not login:
            self.ui.error_label.setText("Введи, пожалуйста, логин пользователя")
            logger.warning(f"Неуспешная попытка входа: не введён логин")
            return

        if " " in login:
            self.ui.error_label.setText("Логин пользователя не может содержать пробел")
            logger.warning(f"Неуспешная попытка входа: логин содержит пробел")
            return

        if not password:
            self.ui.error_label.setText("Введи, пожалуйста, пароль пользователя")
            logger.warning(f"Неуспешная попытка входа: не введён пароль")
            return

        if " " in password:
            self.ui.error_label.setText("Пароль пользователя не может содержать пробел")
            logger.warning(f"Неуспешная попытка входа: пароль содержит пробел")
            return

        user_id = self.get_user_from_db(login, password)

        if user_id:
            # Если пользователь существует, то переходим к главной странице
            logger.info(f"Открытие главной страницы для пользователя: '{user_id}'")
            self.main_page = MainPage(user_id)
            self.main_page.show()
            self.close()
        else:
            # Если пользователя не существует, то отправляем инфо о проверке пароля или логина
            self.ui.error_label.setText("Неправильный логин или пароль")

    # Ищем в бд указанного пользователя
    def get_user_from_db(self, login, password):
        try:
            query = "select user_id from user_data where login = ? and password = ?"
            result = self.db_conn.execute_query(query, params=(login, password), fetchone=True)

            if result:
                logger.info(f"Пользователь найден в базе данных, user_id: '{result[0]}'")
                return result[0]
            else:
                logger.info(f"Пользователь не найден в базе данных: неправильный логин или пароль")
                return None
        except Exception as syserr3:
            logger.error(f"Ошибка поиска указанного пользователя в базе данных, "
                         f"логин: '{login}', "
                         f"пароль: '[HIDDEN]', "
                         f"детали: '{syserr3}'")
            self.ui.error_label.setText("Возникла ошибка базы данных, обратись к администратору")
            return

    # Редирект в меню
    def back_to_main(self):
        logger.info(f"Возврат в меню")
        self.main_menu = MainMenu()
        self.main_menu.show()
        self.close()