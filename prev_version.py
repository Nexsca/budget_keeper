# Страница главного меню - первая страница приложения, пользователь может выбрать функцию входа или регистрации
# class MainMenu(QMainWindow):
#    def __init__(self):
#        super().__init__()
#
#        # Устанавливаем иконку для окна
#        self.setWindowIcon(QIcon('content/app_icon.ico'))
#
#        # Импортируем интерфейс
#        self.ui = Ui_MainMenuWindow()
#        self.ui.setupUi(self)
#
# Коннект кнопок для входа и регистрации
#        self.ui.enter_button.clicked.connect(self.go_to_login)
#        self.ui.reg_button.clicked.connect(self.go_to_register)

# Редирект на страницу логина
#    def go_to_login(self):
#        logger.info(f"Открытие страницы входа в профиль")
#        self.login_page = LoginPage()
#        self.login_page.show()
#        self.close()

# Редирект на страницу регистрации
#   def go_to_register(self):
#       logger.info(f"Открытие страницы регистрации")
#       self.register_page = RegisterPage()
#      self.register_page.show()
#      self.close()


# Страница входа в профиль - страница с вводом логина и пароля пользователя
# class LoginPage(QMainWindow):
#   def __init__(self):
#        super().__init__()

# Устанавливаем иконку для окна
#        self.setWindowIcon(QIcon('content/app_icon.ico'))
#
# Для работы с бд
#        self.db_conn = DatabaseConn()

# Импортируем интерфейс
#        self.ui = Ui_LoginPageWindow()
#        self.ui.setupUi(self)

# Коннект кнопок для входа и возврата в меню
#        self.ui.login_button.clicked.connect(self.check_login)
#        self.ui.back_button.clicked.connect(self.back_to_main)

# Проверка логина на существование в базе данных
#    def check_login(self):
#        login = self.ui.login_input.text()
#        password = self.ui.password_input.text()
#        logger.info(f"Выполняется вход в профиль, логин: '{login}', пароль: '[HIDDEN]'")
# Проверки введённых данных
#        if not login:
#            self.ui.error_label.setText("Введи, пожалуйста, логин пользователя")
#            logger.warning(f"Неуспешная попытка входа: не введён логин")
#            return

#        if " " in login:
#            self.ui.error_label.setText("Логин пользователя не может содержать пробел")
#            logger.warning(f"Неуспешная попытка входа: логин содержит пробел")
#            return

#        if not password:
#            self.ui.error_label.setText("Введи, пожалуйста, пароль пользователя")
#            logger.warning(f"Неуспешная попытка входа: не введён пароль")
#            return

#        if " " in password:
#            self.ui.error_label.setText("Пароль пользователя не может содержать пробел")
#            logger.warning(f"Неуспешная попытка входа: пароль содержит пробел")
#            return

#        user_id = self.get_user_from_db(login, password)

#        if user_id:
# Если пользователь существует, то переходим к главной странице
#            logger.info(f"Открытие главной страницы для пользователя: '{user_id}'")
#            self.main_page = MainPage(user_id)
#            self.main_page.show()
#            self.close()
#        else:
#            # Если пользователя не существует, то отправляем инфо о проверке пароля или логина
#            self.ui.error_label.setText("Неправильный логин или пароль")

# Ищем в бд указанного пользователя
#    def get_user_from_db(self, login, password):
#        try:
#            query = "select user_id from user_data where login = ? and password = ?"
#            result = self.db_conn.execute_query(query, params=(login, password), fetchone=True)

#            if result:
#                logger.info(f"Пользователь найден в базе данных, user_id: '{result[0]}'")
#                return result[0]
#            else:
#                logger.info(f"Пользователь не найден в базе данных: неправильный логин или пароль")
#                return None
#        except Exception as syserr3:
#            logger.error(f"Ошибка поиска указанного пользователя в базе данных, "
#                         f"логин: '{login}', "
#                         f"пароль: '[HIDDEN]', "
#                         f"детали: '{syserr3}'")
#            self.ui.error_label.setText("Возникла ошибка базы данных, обратись к администратору")
#            return

# Редирект в меню
#    def back_to_main(self):
#        logger.info(f"Возврат в меню")
#        self.main_menu = MainMenu()
#        self.main_menu.show()
#        self.close()


# Страница регистрации
# class RegisterPage(QMainWindow):
#    def __init__(self):
#        super().__init__()

# Устанавливаем иконку для окна
#        self.setWindowIcon(QIcon('content/app_icon.ico'))

# Для работы с бд
#        self.db_conn = DatabaseConn()

# Импортируем интерфейс
#        self.ui = Ui_RegPageWindow()
#        self.ui.setupUi(self)

# Коннект кнопок для регистрации и возврата в меню
#        self.ui.registration_button.clicked.connect(self.register_user)
#        self.ui.back_button.clicked.connect(self.back_to_main)

# Метод для регистрации пользователя
#    def register_user(self):
#        login = self.ui.login_input.text()
#        password = self.ui.password_input.text()
#        logger.info(f"Выполняется регистрация нового пользователя, логин: '{login}', пароль: '[HIDDEN]'")

# Проверка на корректность заполнения полей при регистрации
#        if not login:
#            self.ui.error_label.setText("Введи, пожалуйста, логин пользователя")
#            logger.warning(f"Неуспешная попытка регистрации: не введён логин")
#            return

#        if " " in login:
#            self.ui.error_label.setText("Логин пользователя не может содержать пробел")
#            logger.warning(f"Неуспешная попытка регистрации: логин содержит пробел")
#            return

#        if not password:
#            self.ui.error_label.setText("Введи, пожалуйста, пароль пользователя")
#            logger.warning(f"Неуспешная попытка регистрации: не введён пароль")
#            return

#        if " " in password:
#            self.ui.error_label.setText("Пароль пользователя не может содержать пробел")
#            logger.warning(f"Неуспешная попытка регистрации: пароль содержит пробел")
#            return

# Проверка на существование логина в базе данных
#        if self.check_login_exists(login):
#            logger.warning(f"Неуспешная попытка регистрации: пользователь с таким логином уже существует, "
#                          f"логин: '{login}'")
#            self.ui.error_label.setText("Пользователь с таким логином уже существует")
#        else:
# Запись нового пользователя в базу данных
#            self.user_id = self.save_new_user(login, password)
#            self.ui.error_label.setText("Пользователь успешно создан")
#            QTimer.singleShot(1500, self.anketa_after_delay)

# Проверка логина на существование в базе данных
#    def check_login_exists(self, login):
#        logger.info(f"Выполняется проверка логина на существование в базе данных, логин: '{login}'")
#        try:
#            query = "select login from user_data where login = ?"
#            result = self.db_conn.execute_query(query, params=(login,), fetchone=True)

#            if result:
#                logger.info("Пользователь с таким логином уже существует в базе данных")
#                return True
#            else:
#                return False
#        except Exception as syserr4:
#            logger.error(f"Ошибка поиска указанного пользователя в базе данных, "
#                         f"логин: '{login}', "
#                         f"детали: '{syserr4}'")
#            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")

# Регистрация нового пользователя
#    def save_new_user(self, login, password):
#        try:
#            insert_query = "insert into user_data (login, password) values (?, ?)"
#            self.db_conn.execute_query(insert_query, params=(login, password), fetchone=True)

#            get_id_query = "select user_id from user_data where login = ?"
#            result = self.db_conn.execute_query(get_id_query, params=(login,), fetchone=True)
#            logger.info(f"Пользователь успешно зарегистрирован, "
#                        f"логин: '{login}', "
#                        f"пароль: '[HIDDEN]'")
#            return result[0]
#        except sqlite3.Error as sqlerr2:
#            logger.error(f"Ошибка базы данных при регистрации указанного пользователя, "
#                         f"логин: '{login}', "
#                         f"пароль: '[HIDDEN]', "
#                         f"детали: '{sqlerr2}'")
#        except Exception as syserr5:
#            logger.error(f"Ошибка регистрации указанного пользователя в базе данных, "
#                        f"логин: '{login}', "
#                         f"пароль: '[HIDDEN]', "
#                         f"детали: '{syserr5}'")
#            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")

# Метод для перехода к странице анкеты
#    def anketa_after_delay(self):
#        logger.info(f"Открытие страницы анкеты для пользователя: '{self.user_id}'")
#        self.anketa_page = AnketaPage(self.user_id)
#        self.anketa_page.show()
#        self.close()

# Редирект в меню
#    def back_to_main(self):
#        logger.info(f"Возврат в меню")
#        self.main_menu = MainMenu()
#        self.main_menu.show()
#        self.close()


# Страница анкеты
# class AnketaPage(QMainWindow):
#    def __init__(self, user_id):
#        super().__init__()

# Устанавливаем иконку для окна
#        self.setWindowIcon(QIcon('content/app_icon.ico'))

# Для работы с бд
#        self.db_conn = DatabaseConn()

# Импортируем интерфейс
#        self.ui = Ui_AnketaPageWindow()
#        self.ui.setupUi(self)

# Для директивного обращения к странице
#        self.user_id = user_id

# Коннект кнопки для сохранения
#        self.ui.save_button.clicked.connect(self.save_anketa_data)

# Сохранение данных пользователя
#    def save_anketa_data(self):
#        first_name = self.ui.firstname.text()
#        sur_name = self.ui.surname.text()
#        not_parsed_income = self.ui.total_income.text()
#        logger.info(f"Выполняется сохранение данных нового пользователя")

#        if not first_name:
#            self.ui.error_label.setText(f"Введи, пожалуйста, своё имя")
#            logger.error(f"Неуспешная попытка сохранения: не введено имя пользователя")
#            return

# Если доход введён, парсим при необходимости
#        if not_parsed_income:
#            parsed_income = pars_value(not_parsed_income)

# Проверка результата парсинга
#            if parsed_income == -2:
#                self.ui.error_label.setText(f"Похоже, ты ввёл некорректное значение дохода, вот пример: 10000,00")
#                return
#            elif parsed_income == -1:
#                self.ui.error_label.setText(f"Похоже, возникла ошибка обработки, обратись к администратору")
#                return
#        else:
#            parsed_income = not_parsed_income

# Сохраняем данные пользователя в базе данных
#        try:
#            query = "update user_data set first_name = ?, last_name = ?, current_income = ? where user_id = ?"
#            self.db_conn.execute_query(query, params=(first_name, sur_name, parsed_income, self.user_id))
#            logger.info(f"Анкета пользователя успешно сохранена: "
#                        f"id: '{self.user_id}', "
#                        f"имя: '{first_name}', "
#                        f"фамилия: '{sur_name}', "
#                        f"текущий доход: '{parsed_income}'")
#            self.ui.error_label.setText(f"Анкета пользователя успешно сохранена")
#            QTimer.singleShot(1800, self.welcome_after_delay)
#        except Exception as syserr6:
#            logger.error(f"Ошибка сохранения анкеты пользователя в базе данных, "
#                         f"имя: '{first_name}', "
#                         f"фамилия: '{sur_name}', "
#                         f"текущий доход: '{not_parsed_income}', "
#                         f"детали: '{syserr6}'")
#            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")

# Метод для перехода к странице с приветствием после задержки
#    def welcome_after_delay(self):
#        logger.info(f"Открытие приветственной страницы для пользователя: '{self.user_id}'")
#        self.main_page = WelcomePage(self.user_id)
#        self.main_page.show()
#        self.close()


# Страница-приветствие
# class WelcomePage(QMainWindow):
#    def __init__(self, user_id):
#        super().__init__()

# Устанавливаем иконку для окна
#        self.setWindowIcon(QIcon('content/app_icon.ico'))

# Для директивного обращения к странице
#        self.user_id = user_id

# Импортируем интерфейс
#        self.ui = Ui_WelcomePageWindow()
#        self.ui.setupUi(self)

# Коннект кнопки для сохранения
#        self.ui.next_button.clicked.connect(self.go_next)

# Метод для перехода на страницу создания счетов пользователя
#    def go_next(self):
#        logger.info(f"Открытие страницы создания счетов для пользователя: '{self.user_id}'")
#        self.main_page = SetAccountPage(self.user_id)
#        self.main_page.show()
#        self.close()

# Прошлый метод генерации форм для заполнения данных по счетам
# Connect button to generate forms
# self.create_button.clicked.connect(self.generate_account_forms)


# def generate_account_forms(self):
#    """Generates account forms dynamically based on the selected number of accounts."""
# Clear previous forms
#    logger.info(f"Выполняется очистка форм для заполнения счетов пользователя")
#    for i in reversed(range(self.scroll_layout.count())):
#        widget_to_remove = self.scroll_layout.itemAt(i).widget()
#        if widget_to_remove:
#            widget_to_remove.deleteLater()

#    self.account_forms.clear()

# Generate forms
#    num_accounts = self.amount_accounts.value()
#    logger.info(f"Выполняется генерация форм для заполнения данных о счетах пользователя, "
#                f"количество: '{num_accounts}'")
#    for i in range(num_accounts):
#        form_widget = QtWidgets.QWidget()
#        form_layout = QtWidgets.QHBoxLayout(form_widget)

# Account Name Input
#        account_name_label = QtWidgets.QLabel(f"Счёт №{i + 1}:")
#        account_name_label.setStyleSheet("font: 12pt \"Involve\";\n"
#                                         "color: rgb(34, 34, 59);")
#        account_name_input = QtWidgets.QLineEdit()
#        account_name_input.setStyleSheet("border-radius: 15px;\n"
#                                         "background-color: rgb(242, 233, 228);\n"
#                                         "font: 12pt \"Involve\";\n"
#                                         "color: rgb(34, 34, 59)")
#        account_name_input.setPlaceholderText(" наименование счёта")
#        account_name_input.setFixedHeight(30)
#        account_name_input.setFixedWidth(390)

# Account Type Dropdown
#        account_type_label = QtWidgets.QLabel("Тип счёта:")
#        account_type_label.setStyleSheet("font: 12pt \"Involve\";\n"
#                                         "color: rgb(34, 34, 59);")
#        account_type_dropdown = QtWidgets.QComboBox()
#        account_type_dropdown.setStyleSheet("font: 12pt \"Involve\";\n"
#                                            "color: rgb(34, 34, 59);\n"
#                                            "background-color: rgb(242, 233, 228);\n"
#                                            "border-radius: 15px;")
#        account_type_dropdown.addItems(
#            ["Карточный счёт", "Текущий счёт", "Резервный счёт", "Накопительный счёт", "Вклад", "Валютный счёт",
#             "Займ"])
#        account_type_dropdown.setFixedHeight(30)
#        account_type_dropdown.setFixedWidth(200)

# Add widgets to the form layout
#        form_layout.addWidget(account_name_label)
#        form_layout.addWidget(account_name_input)
#        form_layout.addWidget(account_type_label)
#        form_layout.addWidget(account_type_dropdown)

# Зададим вручную спэйсер
#        spacer = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
#        form_layout.addItem(spacer)

# Add form to the scroll layout
#        self.scroll_layout.addWidget(form_widget)

#        self.account_forms.append({
#            "name_input": account_name_input,
#            "type_dropdown": account_type_dropdown
#        })

# Страница для создания счетов пользователя
# class SetAccountPage(QMainWindow):
#    def __init__(self, user_id):
#        super().__init__()

# Устанавливаем иконку для окна
#        self.setWindowIcon(QIcon('content/app_icon.ico'))

# Для работы с бд
#        self.db_conn = DatabaseConn()

# Для директивного обращения к странице
#        self.user_id = user_id

# Импортируем интерфейс
#        self.ui = Ui_SetAccountPage()
#        self.ui.setupUi(self)

# Коннект кнопки для сохранения
#        self.ui.save_button.clicked.connect(self.save_accounts)

# Метод для сохранения счетов пользователя
#    def save_accounts(self):
#        accounts_data = []
#        logger.info(f"Выполняется попытка сохранения счетов пользователя: '{self.user_id}'")

#        for account_form in self.ui.account_forms:
#            account_username = account_form["name_input"].text()
#            account_type_name = account_form["type_dropdown"].currentText()

# В случае незаполнения какого-либо поля, выводим предупреждение
#            if not account_username:
#                logger.warning(f"Неуспешная попытка сохранения: не заполнено наименование счёта")
#                self.ui.error_label.setText(f"Похоже, ты не заполнил все наименования счёта, заполни и попробуй снова")
#                return

# Собираем данные для записи
#            accounts_data.append({
#                "user_id": self.user_id,
#                "account_username": account_username,
#                "account_type_name": account_type_name
#            })

# Информационное окно для пользователя
#        self.ui.error_label.setText(f"Подожди, пожалуйста, выполняется сохранение твоих счетов")

# Если данные валидны, сохраняем их в базу данных
#        try:
# Задаём даты создания, деактивации и апдейта счёта (заглушка)
#            create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#            deactivate_date = "9999-12-12 23:59:59"
#            update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Выполняем сохранение данных по счетам последовательно, для каждого отдельно
#            for account in accounts_data:
#                user_id = account["user_id"]
#                account_username = account["account_username"]
#                account_type_name = account["account_type_name"]

# Собираем дополнительные данные по счёту из справочника
#                account_type_code = self.get_acc_type_code(account_type_name)
#                account_type = self.get_acc_type(account_type_code)
#                logger.info(f"Успешное получение дополнительных данных по счёту из справочника: '{account_username}'")

# Записываем в базу данных
#                insert_query = ("insert into user_account "
#                                "(user_id, account_name, account_type_name, account_type, "
#                                "account_type_code, create_date, deactivate_date, update_date) "
#                                "values (?, ?, ?, ?, ?, ?, ?, ?);")
#                self.db_conn.execute_query(insert_query,
#                                           params=(user_id, account_username, account_type_name, account_type,
#                                                   account_type_code, create_date, deactivate_date, update_date))

# После успешного сохранения информируем пользователя и переходим к главной странице
#            logger.info(f"Выполнено успешное сохранение счетов пользователя в базу данных")
#            self.ui.error_label.setText(f"Твои счета были успешно сохранены")

# Открываем главную страницу после небольшой задержки
#            QTimer.singleShot(1800, self.main_page_after_delay)
#        except Exception as syserr12:
#            logger.error(f"Возникла ошибка при сохранении счетов пользователя, "
#                         f"user_id: '{self.user_id}', "
#                         f"детали: '{syserr12}'")
#            self.ui.error_label.setText(f"Возникла непредвиденная ошибка, обратись к администратору")
#            return

# Забираем код типа счёта
#    def get_acc_type_code(self, account_type_name):
#        query = "select account_type_code from account_type where account_type_name = ?"
#        result_1 = self.db_conn.execute_query(query, params=(account_type_name,), fetchone=True)
#        if result_1:
#            return result[0]
#        else:
#            return None

# Забираем тип счёта
#    def get_acc_type(self, account_type_code):
#        query = "select account_type from account_type where account_type_code = ?"
#        result_2 = self.db_conn.execute_query(query, params=(account_type_code,), fetchone=True)
#        if result_2:
#            return result[0]
#        else:
#            return None

# Метод для перехода к главной странице после задержки
#    def main_page_after_delay(self):
#        logger.info(f"Открытие главной страницы для пользователя: '{self.user_id}'")
#        self.main_page = MainPage(self.user_id)
#        self.main_page.show()
#        self.close()
