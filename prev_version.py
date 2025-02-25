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


# Страница регистрации
class RegisterPage(QMainWindow):
    def __init__(self):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Импортируем интерфейс
        self.ui = Ui_RegPageWindow()
        self.ui.setupUi(self)

        # Коннект кнопок для регистрации и возврата в меню
        self.ui.regisrtation_button.clicked.connect(self.register_user)
        self.ui.back_button.clicked.connect(self.back_to_main)

    # Метод для регистрации пользователя
    def register_user(self):
        login = self.ui.login_input.text()
        password = self.ui.password_input.text()
        logger.info(f"Выполняется регистрация нового пользователя, логин: '{login}', пароль: '[HIDDEN]'")

        # Проверка на корректность заполнения полей при регистрации
        if not login:
            self.ui.error_label.setText("Введи, пожалуйста, логин пользователя")
            logger.warning(f"Неуспешная попытка регистрации: не введён логин")
            return

        if " " in login:
            self.ui.error_label.setText("Логин пользователя не может содержать пробел")
            logger.warning(f"Неуспешная попытка регистрации: логин содержит пробел")
            return

        if not password:
            self.ui.error_label.setText("Введи, пожалуйста, пароль пользователя")
            logger.warning(f"Неуспешная попытка регистрации: не введён пароль")
            return

        if " " in password:
            self.ui.error_label.setText("Пароль пользователя не может содержать пробел")
            logger.warning(f"Неуспешная попытка регистрации: пароль содержит пробел")
            return

        # Проверка на существование логина в базе данных
        if self.check_login_exists(login):
            logger.warning(f"Неуспешная попытка регистрации: пользователь с таким логином уже существует, "
                           f"логин: '{login}'")
            self.ui.error_label.setText("Пользователь с таким логином уже существует")
        else:
            # Запись нового пользователя в базу данных
            self.user_id = self.save_new_user(login, password)
            self.ui.error_label.setText("Пользователь успешно создан")
            QTimer.singleShot(1500, self.anketa_after_delay)

    # Проверка логина на существование в базе данных
    def check_login_exists(self, login):
        logger.info(f"Выполняется проверка логина на существование в базе данных, логин: '{login}'")
        try:
            query = "select login from user_data where login = ?"
            result = self.db_conn.execute_query(query, params=(login,), fetchone=True)

            if result:
                logger.info("Пользователь с таким логином уже существует в базе данных")
                return True
            else:
                return False
        except Exception as syserr4:
            logger.error(f"Ошибка поиска указанного пользователя в базе данных, "
                         f"логин: '{login}', "
                         f"детали: '{syserr4}'")
            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")

    # Регистрация нового пользователя
    def save_new_user(self, login, password):
        try:
            insert_query = "insert into user_data (login, password) values (?, ?)"
            self.db_conn.execute_query(insert_query, params=(login, password), fetchone=True)

            get_id_query = "select user_id from user_data where login = ?"
            result = self.db_conn.execute_query(get_id_query, params=(login,), fetchone=True)
            logger.info(f"Пользователь успешно зарегистрирован, "
                        f"логин: '{login}', "
                        f"пароль: '[HIDDEN]'")
            return result[0]
        except sqlite3.Error as sqlerr2:
            logger.error(f"Ошибка базы данных при регистрации указанного пользователя, "
                         f"логин: '{login}', "
                         f"пароль: '[HIDDEN]', "
                         f"детали: '{sqlerr2}'")
        except Exception as syserr5:
            logger.error(f"Ошибка регистрации указанного пользователя в базе данных, "
                         f"логин: '{login}', "
                         f"пароль: '[HIDDEN]', "
                         f"детали: '{syserr5}'")
            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")

    # Метод для перехода к странице анкеты
    def anketa_after_delay(self):
        logger.info(f"Открытие страницы анкеты для пользователя: '{self.user_id}'")
        self.anketa_page = AnketaPage(self.user_id)
        self.anketa_page.show()
        self.close()

    # Редирект в меню
    def back_to_main(self):
        logger.info(f"Возврат в меню")
        self.main_menu = MainMenu()
        self.main_menu.show()
        self.close()


# Страница анкеты
class AnketaPage(QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Импортируем интерфейс
        self.ui = Ui_AnketaPageWindow()
        self.ui.setupUi(self)

        # Для директивного обращения к странице
        self.user_id = user_id

        # Коннект кнопки для сохранения
        self.ui.save_button.clicked.connect(self.save_anketa_data)

    # Сохранение данных пользователя
    def save_anketa_data(self):
        first_name = self.ui.firstname.text()
        sur_name = self.ui.surname.text()
        not_parsed_income = self.ui.total_income.text()
        logger.info(f"Выполняется сохранение данных нового пользователя")

        if not first_name:
            self.ui.error_label.setText(f"Введи, пожалуйста, своё имя")
            logger.error(f"Неуспешная попытка сохранения: не введено имя пользователя")
            return

        # Если доход введён, парсим при необходимости
        if not_parsed_income:
            parsed_income = pars_value(not_parsed_income)

            # Проверка результата парсинга
            if parsed_income == -2:
                self.ui.error_label.setText(f"Похоже, ты ввёл некорректное значение дохода, вот пример: 10000,00")
                return
            elif parsed_income == -1:
                self.ui.error_label.setText(f"Похоже, возникла ошибка обработки, обратись к администратору")
                return
        else:
            parsed_income = not_parsed_income

        # Сохраняем данные пользователя в базе данных
        try:
            query = "update user_data set first_name = ?, last_name = ?, current_income = ? where user_id = ?"
            self.db_conn.execute_query(query, params=(first_name, sur_name, parsed_income, self.user_id))
            logger.info(f"Анкета пользователя успешно сохранена: "
                        f"id: '{self.user_id}', "
                        f"имя: '{first_name}', "
                        f"фамилия: '{sur_name}', "
                        f"текущий доход: '{parsed_income}'")
            self.ui.error_label.setText(f"Анкета пользователя успешно сохранена")
            QTimer.singleShot(1800, self.welcome_after_delay)
        except Exception as syserr6:
            logger.error(f"Ошибка сохранения анкеты пользователя в базе данных, "
                         f"имя: '{first_name}', "
                         f"фамилия: '{sur_name}', "
                         f"текущий доход: '{not_parsed_income}', "
                         f"детали: '{syserr6}'")
            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")

    # Метод для перехода к странице с приветствием после задержки
    def welcome_after_delay(self):
        logger.info(f"Открытие приветственной страницы для пользователя: '{self.user_id}'")
        self.main_page = WelcomePage(self.user_id)
        self.main_page.show()
        self.close()


# Страница-приветствие
class WelcomePage(QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для директивного обращения к странице
        self.user_id = user_id

        # Импортируем интерфейс
        self.ui = Ui_WelcomePageWindow()
        self.ui.setupUi(self)

        # Коннект кнопки для сохранения
        self.ui.next_button.clicked.connect(self.go_next)

    # Метод для перехода на страницу создания счетов пользователя
    def go_next(self):
        logger.info(f"Открытие страницы создания счетов для пользователя: '{self.user_id}'")
        self.main_page = SetAccountPage(self.user_id)
        self.main_page.show()
        self.close()
