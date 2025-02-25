# Импорт основных библиотек
import locale
import logging
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
import re
import sys
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from functools import partial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# Импорт библиотек для работы с QUI - PyQt
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontDatabase, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow
from PyQt5.QtWidgets import QPushButton, QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout
# Импорт UI, созданных в QtDesigner
from main_menu_window import Ui_MainMenuWindow
from welcome_page_window import Ui_WelcomePageWindow
from set_account_page_window import Ui_SetAccountPage
from main_page_window import Ui_MainPageWindow
from confirm_page_window import Ui_ConfirmPageWindow
from new_month_window import Ui_NewMonthWindow
from my_profile_page import Ui_MyProfilePage
from confirm_password_window import Ui_ConfirmPasswordWindow
from my_accounts_page import Ui_MyAccountsPage
from confirm_delete_account_window import Ui_ConfirmDeleteWindow
from success_delete_window import Ui_SuccessDeleteWindow
from new_accounts_window import Ui_NewAccountsWindow
from edit_accounts_window import Ui_EditAccountsWindow
from my_accounts_history_page import Ui_MyAccountsHistoryPage
from help_page import Ui_HelpPage


# Настройка корректного получения русскоязычного текста
locale.setlocale(locale.LC_TIME, "Russian_Russia.1251")

# Настройка логирования
logging.basicConfig(
    filename='app.log',  # Имя файла для записи логов
    level=logging.INFO,  # Уровень логирования (INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщений
    datefmt="%Y-%m-%d %H:%M:%S"  # Формат даты и времени
)
logger = logging.getLogger("BudgetAppLogger")  # Файл лога для обращения в коде


# Работа с бд - выполняется подключение к базе данных, выполнение запроса, подтверждение изменений и
# закрытие подключения
class DatabaseConn:
    def __init__(self, db_name="budget_keeper.db"):
        self.db_name = db_name

    # Попытка подключения к базе данных
    def connect(self):
        try:
            connection = sqlite3.connect(self.db_name)
            logger.info(f"Успешное подключение к базе данных: '{self.db_name}'")
            return connection
        except sqlite3.Error as syserr1:
            logger.error(f"Ошибка подключения к базе данных: '{self.db_name}', детали: '{syserr1}'")
            raise

    # Выполнение запроса к базе данных
    def execute_query(self, query, params=(), fetchone=False, fetchall=False):
        conn = self.connect()
        cursor = conn.cursor()
        logger.info(f"Выполнение запроса к базе данных: '{query}'")
        try:
            cursor.execute(query, params)
            conn.commit()

            if fetchone:
                result_n = cursor.fetchone()
                logger.info(f"Результат fetchone успешно получен")
                return result_n
            if fetchall:
                result_c = cursor.fetchall()
                logger.info(f"Результат fetchall успешно получен")
                return result_c

            logger.info(f"Запрос выполнен успешно, продолжение работы приложения")
        except sqlite3.Error as sqlerror1:
            logger.error(f"Ошибка при выполнении запроса к базе данных, "
                         f"детали: {sqlerror1}'")
            raise
        except Exception as syserr2:
            logger.critical(f"Ошибка подключения к базе данных: '{self.db_name}', "
                            f"детали: '{syserr2}'")
            raise
        finally:
            cursor.close()
            conn.close()
            logger.info(f"Подключение к базе данных закрыто: '{self.db_name}'")


# Статический метод парсинга введённого числового значения
def pars_value(input_value):
    logger.info(f"Выполняется запрос на парсинг числового значения: '{input_value}'")
    cleaned_value = input_value
    try:
        cleaned_value = cleaned_value.replace("-", "0")
        cleaned_value = cleaned_value.replace(" ", "")
        if "," in input_value:
            cleaned_value = input_value.replace(",", ".")
            cleaned_value = cleaned_value.replace("-", "0")
            cleaned_value = cleaned_value.replace(" ", "")

        parsed_value = float(cleaned_value)
        logger.info(f"Запрос на парсинг числового значения успешно выполнен, "
                    f"введённое значение: '{input_value}', "
                    f"полученное значение: '{parsed_value}'")
        return float(parsed_value)
    except ValueError as syserr111:
        logger.warning(f"Запрос на парсинг числового значения не выполнен, "
                       f"введённое значение: '{input_value}', "
                       f"детали: '{syserr111}'")
        return -2
    except Exception as syserr01:
        logger.error(f"Запрос на парсинг числового значения не выполнен, "
                     f"введённое значение: '{input_value}', "
                     f"детали: '{syserr01}'")
        return -1


# Страница главного меню - первая страница приложения, пользователь может выбрать функцию входа или регистрации
class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Импортируем интерфейс
        self.ui = Ui_MainMenuWindow()
        self.ui.setupUi(self)

        # Устанавливаем начальную страницу
        self.ui.stacked_widget.setCurrentIndex(0)

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Коннект кнопок для входа и регистрации
        self.ui.enter_button.clicked.connect(self.go_to_login)
        self.ui.reg_button.clicked.connect(self.go_to_register)

    # Редирект на страницу логина
    def go_to_login(self):
        logger.info(f"Открытие страницы входа в профиль")
        self.ui.stacked_widget.setCurrentIndex(1)

        # Страница входа в профиль - страница с вводом логина и пароля пользователя

        # Метод проверки логина на существование в базе данных
        def check_login():
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

            user_id = get_user_from_db(login, password)

            if user_id:
                # Если пользователь существует, то переходим к главной странице
                logger.info(f"Открытие главной страницы для пользователя: '{user_id}'")
                self.main_page = MainPage(user_id)
                self.main_page.show()
                self.hide()
            else:
                # Если пользователя не существует, то отправляем инфо о проверке пароля или логина
                self.ui.error_label.setText("Неправильный логин или пароль")

        # Ищем в бд указанного пользователя
        def get_user_from_db(login, password):
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

        # Коннект кнопки для входа и возврата в меню
        self.ui.login_button.clicked.connect(check_login)
        self.ui.back_button.clicked.connect(self.back_to_main)

    # Редирект на страницу регистрации
    def go_to_register(self):
        logger.info(f"Открытие страницы регистрации")
        self.ui.stacked_widget.setCurrentIndex(2)

        # Страница регистрации

        # Метод для регистрации пользователя
        def register_user():
            login = self.ui.login_input_reg.text()
            password = self.ui.password_input_reg.text()
            logger.info(f"Выполняется регистрация нового пользователя, логин: '{login}', пароль: '[HIDDEN]'")

            # Проверка на корректность заполнения полей при регистрации
            if not login:
                self.ui.error_label_reg.setText("Введи, пожалуйста, логин пользователя")
                logger.warning(f"Неуспешная попытка регистрации: не введён логин")
                return

            if " " in login:
                self.ui.error_label_reg.setText("Логин пользователя не может содержать пробел")
                logger.warning(f"Неуспешная попытка регистрации: логин содержит пробел")
                return

            if not password:
                self.ui.error_label_reg.setText("Введи, пожалуйста, пароль пользователя")
                logger.warning(f"Неуспешная попытка регистрации: не введён пароль")
                return

            if " " in password:
                self.ui.error_label_reg.setText("Пароль пользователя не может содержать пробел")
                logger.warning(f"Неуспешная попытка регистрации: пароль содержит пробел")
                return

            # Проверка на существование логина в базе данных
            if check_login_exists(login):
                logger.warning(f"Неуспешная попытка регистрации: пользователь с таким логином уже существует, "
                               f"логин: '{login}'")
                self.ui.error_label_reg.setText("Пользователь с таким логином уже существует")
            else:
                # Запись нового пользователя в базу данных
                self.user_id = save_new_user(login, password)
                self.ui.error_label_reg.setText("Пользователь успешно создан")
                QTimer.singleShot(1500, self.anketa_after_delay)

        # Проверка логина на существование в базе данных
        def check_login_exists(login):
            logger.info(f"Выполняется проверка логина на существование в базе данных, логин: '{login}'")
            try:
                query_reg = "select login from user_data where login = ?"
                result_reg = self.db_conn.execute_query(query_reg, params=(login,), fetchone=True)

                if result_reg:
                    logger.info("Пользователь с таким логином уже существует в базе данных")
                    return True
                else:
                    return False
            except Exception as syserr4:
                logger.error(f"Ошибка поиска указанного пользователя в базе данных, "
                             f"логин: '{login}', "
                             f"детали: '{syserr4}'")
                self.ui.error_label_reg.setText(f"Возникла ошибка базы данных, обратись к администратору")

        # Регистрация нового пользователя
        def save_new_user(login, password):
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
                self.ui.error_label_reg.setText(f"Возникла ошибка базы данных, обратись к администратору")

        # Коннект кнопок для регистрации и возврата в меню
        self.ui.regisrtation_button.clicked.connect(register_user)
        self.ui.back_button_reg.clicked.connect(self.back_to_main)

    # Страница анкеты пользователя
    def anketa_after_delay(self):
        logger.info(f"Открытие страницы анкеты для пользователя: '{self.user_id}'")
        self.ui.stacked_widget.setCurrentIndex(3)

        # Сохранение данных пользователя
        def save_anketa_data():
            first_name = self.ui.firstname.text()
            sur_name = self.ui.surname.text()
            not_parsed_income = self.ui.total_income.text()
            logger.info(f"Выполняется сохранение данных нового пользователя")

            if not first_name:
                self.ui.error_label_ank.setText(f"Введи, пожалуйста, своё имя")
                logger.error(f"Неуспешная попытка сохранения: не введено имя пользователя")
                return

            # Если доход введён, парсим при необходимости
            if not_parsed_income:
                parsed_income = pars_value(not_parsed_income)

                # Проверка результата парсинга
                if parsed_income == -2:
                    self.ui.error_label_ank.setText(f"Похоже, ты ввёл некорректное значение дохода, "
                                                    f"вот пример: 10000,00")
                    return
                elif parsed_income == -1:
                    self.ui.error_label_ank.setText(f"Похоже, возникла ошибка обработки, обратись к администратору")
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
                self.ui.error_label_ank.setText(f"Анкета пользователя успешно сохранена")
                QTimer.singleShot(1800, welcome_after_delay)
            except Exception as syserr6:
                logger.error(f"Ошибка сохранения анкеты пользователя в базе данных, "
                             f"имя: '{first_name}', "
                             f"фамилия: '{sur_name}', "
                             f"текущий доход: '{not_parsed_income}', "
                             f"детали: '{syserr6}'")
                self.ui.error_label_ank.setText(f"Возникла ошибка базы данных, обратись к администратору")

        # Метод для перехода к странице с приветствием после задержки
        def welcome_after_delay():
            logger.info(f"Открытие приветственной страницы для пользователя: '{self.user_id}'")
            self.main_page = WelcomePage(self.user_id)
            self.main_page.show()
            self.close()

        # Коннект кнопки для сохранения
        self.ui.save_button.clicked.connect(save_anketa_data)

    # Метод для возврата в главное меню
    def back_to_main(self):
        logger.info(f"Возврат в меню")
        self.ui.stacked_widget.setCurrentIndex(0)


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


# Страница для создания счетов пользователя
class SetAccountPage(QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Для директивного обращения к странице
        self.user_id = user_id

        # Импортируем интерфейс
        self.ui = Ui_SetAccountPage()
        self.ui.setupUi(self)

        # Коннект кнопки для сохранения
        self.ui.save_button.clicked.connect(self.save_accounts)

    # Метод для сохранения счетов пользователя
    def save_accounts(self):
        accounts_data = []
        logger.info(f"Выполняется попытка сохранения счетов пользователя: '{self.user_id}'")

        for account_form in self.ui.account_forms:
            account_username = account_form["name_input"].text()
            account_type_name = account_form["type_dropdown"].currentText()

            # В случае незаполнения какого-либо поля, выводим предупреждение
            if not account_username:
                logger.warning(f"Неуспешная попытка сохранения: не заполнено наименование счёта")
                self.ui.error_label.setText(f"Похоже, ты не заполнил все наименования счёта, заполни и попробуй снова")
                return

            # Собираем данные для записи
            accounts_data.append({
                "user_id": self.user_id,
                "account_username": account_username,
                "account_type_name": account_type_name
            })

        # Информационное окно для пользователя
        self.ui.error_label.setText(f"Подожди, пожалуйста, выполняется сохранение твоих счетов")

        # Если данные валидны, сохраняем их в базу данных
        try:
            # Задаём даты создания, деактивации и апдейта счёта (заглушка)
            create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            deactivate_date = "9999-12-12 23:59:59"
            update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Выполняем сохранение данных по счетам последовательно, для каждого отдельно
            for account in accounts_data:
                user_id = account["user_id"]
                account_username = account["account_username"]
                account_type_name = account["account_type_name"]

                # Собираем дополнительные данные по счёту из справочника
                account_type_code = self.get_acc_type_code(account_type_name)
                account_type = self.get_acc_type(account_type_code)
                logger.info(f"Успешное получение дополнительных данных по счёту из справочника: '{account_username}'")

                # Записываем в базу данных
                insert_query = ("insert into user_account "
                                "(user_id, account_name, account_type_name, account_type, "
                                "account_type_code, create_date, deactivate_date, update_date) "
                                "values (?, ?, ?, ?, ?, ?, ?, ?);")
                self.db_conn.execute_query(insert_query,
                                           params=(user_id, account_username, account_type_name, account_type,
                                                   account_type_code, create_date, deactivate_date, update_date))

            # После успешного сохранения информируем пользователя и переходим к главной странице
            logger.info(f"Выполнено успешное сохранение счетов пользователя в базу данных")
            self.ui.error_label.setText(f"Твои счета были успешно сохранены")

            # Открываем главную страницу после небольшой задержки
            QTimer.singleShot(1800, self.main_page_after_delay)
        except Exception as syserr12:
            logger.error(f"Возникла ошибка при сохранении счетов пользователя, "
                         f"user_id: '{self.user_id}', "
                         f"детали: '{syserr12}'")
            self.ui.error_label.setText(f"Возникла непредвиденная ошибка, обратись к администратору")
            return

    # Забираем код типа счёта
    def get_acc_type_code(self, account_type_name):
        query = "select account_type_code from account_type where account_type_name = ?"
        result = self.db_conn.execute_query(query, params=(account_type_name,), fetchone=True)
        if result:
            return result[0]
        else:
            return None

    # Забираем тип счёта
    def get_acc_type(self, account_type_code):
        query = "select account_type from account_type where account_type_code = ?"
        result = self.db_conn.execute_query(query, params=(account_type_code,), fetchone=True)
        if result:
            return result[0]
        else:
            return None

    # Метод для перехода к главной странице после задержки
    def main_page_after_delay(self):
        logger.info(f"Открытие главной страницы для пользователя: '{self.user_id}'")
        self.main_page = MainPage(self.user_id)
        self.main_page.show()
        self.close()


# Класс для отображения графика - холст
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)  # Создаём ось для графика
        super().__init__(self.fig)


# Главная страница пользователя
class MainPage(QMainWindow):
    def __init__(self, user_id, parent=None):
        super(MainPage, self).__init__(parent)

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Для директивного обращения к странице
        self.user_id = user_id

        # Импортируем интерфейс
        self.ui = Ui_MainPageWindow()
        self.ui.setupUi(self)

        # Создаём вертикальный layout для главного виджета - столбчатый график
        layout = QVBoxLayout(self.ui.total_income_2)

        # Приветствие пользователя
        user_data = self.get_user_name()

        if user_data:
            user_total_income = user_data[1]
            if user_total_income:
                self.ui.total_income_4.setText(f"{user_total_income:.2f} ")
            else:
                self.ui.total_income_4.setText(f"0.00 ")
            self.ui.welcome_label.setText(f"Привет, {user_data[0]}!")
            logger.info(f"Успешный вход на страницу пользователя")
        else:
            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")
            return

        # Список для периодов и суммы по всем счетам в этот период
        self.period_sum_list = []

        # Список для наименований счетов пользователя
        self.user_accounts_names = []

        # Подсчёт количества записей по счетам
        self.count_strings = 0

        # Забираем данные по пользователю для заполнения списка выше
        self.get_all_strings()

        if self.count_strings >= 1:

            # Инициализируем холст для столбчатого графика
            self.canvas = MplCanvas(self, width=10, height=6, dpi=100)

            # Добавляем холст
            layout.addWidget(self.canvas)

            # Строим и оформляем столбчатый график
            self.set_graphic()

        else:
            self.ui.total_income_5.setText(f"0.00 ")
            self.ui.error_label.setText(f"\nПохоже, у тебя пока нет записей по счетам\nЧтобы это исправить, "
                                        f"нажми на кнопку Записать месяц")

        # Коннект кнопки для записи месяца
        self.ui.new_month_button.clicked.connect(self.new_month_button)

        # Коннект кнопки для перехода к профилю пользователя
        self.ui.my_profile_button.clicked.connect(self.my_profile_button)

        # Коннект кнопки для перехода к счетам пользователя
        self.ui.my_accounts_button.clicked.connect(self.my_accounts_button)

        # Коннект кнопки для перехода к истории счетов
        self.ui.my_writings_button.clicked.connect(self.my_accounts_history)

        # Коннект кнопки для перехода к странице помощи
        self.ui.help_button.clicked.connect(self.help_page)

        # Коннект кнопки для выхода
        self.ui.exit_button.clicked.connect(self.confirm_exit)

    # Забираем имя пользователя из бд по айди
    def get_user_name(self):
        logger.info(f"Выполняется поиск имени пользователя по указанному id: '{self.user_id}'")
        try:
            query = "select first_name, current_income from user_data where user_id = ?"
            user_data = self.db_conn.execute_query(query, params=(self.user_id,), fetchone=True)
            if user_data:
                logger.info(f"Пользователь с заданным id найден, имя: '{user_data[0]}'")
                return user_data
            else:
                logger.error(f"Пользователь с заданным id не найден, id: '{self.user_id}'")
                return
        except Exception as syserr9:
            logger.error(f"Ошибка поиска пользователя с заданным id, "
                         f"id: '{self.user_id}', "
                         f"детали: '{syserr9}'")
            return

    # Метод для получения информации для работы с графиком
    def get_all_strings(self):
        logger.info(f"Выполняется сбор необходимых данных по счетам пользователя для настройки столбчатого графика")
        try:
            # Сначала дёрнем все записи по всем счетам
            users_accounts_data = []
            try:
                query = ("select ab.balance_id, ab.user_id, ab.year, ab.month, ab.account_id, "
                         "ab.account_type_code, ab.amount, ab.created_at "
                         "from account_balance ab "
                         "join ("
                         "select user_id, year, month, account_id, account_type_code, amount, "
                         "max(created_at) AS max_created_at "
                         "from account_balance "
                         "where user_id = ? "
                         "group by user_id, year, month, account_id, account_type_code) subquery "
                         "on ab.user_id = subquery.user_id "
                         "and ab.year = subquery.year "
                         "and ab.month = subquery.month "
                         "and ab.account_id = subquery.account_id "
                         "and ab.account_type_code = subquery.account_type_code "
                         "and ab.created_at = subquery.max_created_at ")
                users_accounts_data = self.db_conn.execute_query(query, params=(self.user_id,), fetchall=True)

                # Если записи есть, то идём дальше
                if users_accounts_data:
                    self.count_strings += len(users_accounts_data)
                    logger.info(f"Все записи по всем счетам пользователя были успешно получены, "
                                f"количество: '{self.count_strings}'")

                    # Если у пользователя есть записи по счетам, притянем их наименования
                    logger.info(f"Выполняется получение наименований для всех счетов пользователя")
                    try:
                        names_query = ("select user_id, account_id, account_name "
                                       "from user_account where user_id = ?")
                        self.user_accounts_names = self.db_conn.execute_query(names_query, params=(self.user_id,),
                                                                              fetchall=True)
                        logger.info(f"Наименования по всем счетам пользователя успешно получены")
                    except Exception as syserr96:
                        logger.error(f"Возникла ошибка при получении всех наименований счетов пользователя, "
                                     f"детали: '{syserr96}'")
                # Если ничего нет, то выходим из метода
                else:
                    logger.warning(f"Данные по всем счетам пользователя за всё время не были получены: у пользователя "
                                   f"нет таковых")
                    return
            except Exception as syserr14:
                logger.error(f"Возникла ошибка при получении всех записей по всем счетам пользователя, "
                             f"детали: '{syserr14}'")
                return

            # Потом найдём все уникальные периоды по этим счетам и расположим их в порядке от меньшего к
            # большему

            # Порядок месяцев - вспомогательный словарь
            month_order = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                           "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

            # Получаем уникальные пары (Месяц, Год)
            unique_month_year = set((row[3], row[2]) for row in users_accounts_data)

            # Сортируем по году и месяцу
            unique_month_year = sorted(unique_month_year, key=lambda x: (x[1], month_order.index(x[0])))

            # Форматируем результат для сохранения - список из строк
            users_periods = [f"{month},{year}" for month, year in unique_month_year]

            # Итоговый список периодов - последние 12 месяцев
            total_periods = users_periods[-12:]

            # Берём период
            for period in total_periods:

                # Для хранения суммы по всем счетам для текущего периода
                sum_per_cur_period = 0

                # Потом берём одну запись по счёту
                for cur_acc in users_accounts_data:

                    # Дёрнем период для выбранной записи и приведём к общему виду
                    periods_month, periods_year = cur_acc[3], cur_acc[2]
                    statement_period = f"{periods_month},{periods_year}"

                    # Проверим, входит ли она в период
                    if statement_period == period:

                        # Если входит, то мы прибавляем сумму денежных средств по этой записи к общей сумме за период
                        sum_per_cur_period += round(cur_acc[6], 2)

                # После сбора всех сумм по всем счетам по выбранному периоду, формируем кортеж
                cortege_per_cur_period = (period, sum_per_cur_period)

                # И добавляем его в список
                self.period_sum_list.append(cortege_per_cur_period)

            logger.info(f"Сбор необходимых данных по счетам пользователя для настройки столбчатого графика "
                        f"выполнен успешно, "
                        f"список периодов и сумм для пользователя: '{self.period_sum_list}'")

        except Exception as syserr22:
            logger.error(f"Возникла ошибка при сборе необходимых данных по счетам пользователя, "
                         f"детали: '{syserr22}'")
        return

    # Метод для построения и оформления столбчатого графика
    def set_graphic(self):
        logger.info(f"Выполняется отрисовка графика")

        try:
            # Напишем свой заголовок
            self.ui.error_label.setText(f"\nГрафик состояния твоих денежных средств")

            # Распакуем список
            period, summa = zip(*self.period_sum_list)

            # Указываем шрифт Involve
            font_path = "content/fonts/Involve-Regular.ttf"
            font_prop = fm.FontProperties(fname=font_path, size=8)

            # Применяем шрифт ко всем текстовым элементам
            plt.rcParams['font.family'] = font_prop.get_name()

            # Задаём список цветов
            colours = [
                (0.427, 0.408, 0.459),      # #6D6875
                (0.710, 0.514, 0.553),      # #B5838D
                (0.898, 0.596, 0.608),      # #E5989B
                (1.0, 0.706, 0.635),        # #FFB4A2
                (1.0, 0.890, 0.811),        # #ffe3cf
                (0.950, 0.914, 0.894)       # #f2e9e4
            ]

            # Рисуем график
            self.canvas.ax.bar(period, summa, color=colours, width=0.2)
            self.canvas.ax.set_xlabel('\nПериоды', fontsize=10, fontproperties=font_prop)
            self.canvas.ax.tick_params(axis='x', labelrotation=25)
            self.canvas.ax.set_ylabel('Сумма денежных средств,\n руб.', fontsize=10, fontproperties=font_prop)
            self.canvas.ax.grid(visible=False)

            # Изменяем шрифт для меток делений осей
            for label in self.canvas.ax.get_xticklabels():
                label.set_fontproperties(font_prop)

            for label in self.canvas.ax.get_yticklabels():
                label.set_fontproperties(font_prop)

            # Рисуем график
            self.canvas.draw()
            logger.info(f"График успешно отрисован")
        except Exception as syserr99:
            logger.error(f"Возникла ошибка при отрисовке графика, "
                         f"детали: '{syserr99}'")
            return

        # Также заполним сумму на счетах на последний месяц
        last_month_data = self.period_sum_list[-1]
        last_sum = last_month_data[-1]
        self.ui.total_income_5.setText(f"{last_sum:.2f} ")

    # Метод для перехода к записи данных по счетам за месяц
    def new_month_button(self):
        logger.info(f"Открытие страницы для записи нового месяца для пользователя: '{self.user_id}'")
        self.new_page = NewMonthPage(self.user_id, parent_window=self)
        self.new_page.show()

    # Метод для перехода к странице профиля пользователя
    def my_profile_button(self):
        logger.info(f"Открытие страницы профиля для пользователя: '{self.user_id}'")
        self.profile_page = MyProfilePage(self.user_id)
        self.profile_page.show()
        self.close()

    # Метод для перехода к странице счетов пользователя
    def my_accounts_button(self):
        logger.info(f"Открытие страницы счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountsPage(self.user_id)
        self.accounts_page.show()
        self.close()

    # Метод для перехода к истории счетов пользователя
    def my_accounts_history(self):
        logger.info(f"Открытие страницы истории счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountHistoryWindow(self.user_id)
        self.accounts_page.show()
        self.close()

    # Метод для перехода к странице помощи
    def help_page(self):
        logger.info(f"Открытие страницы помощи")
        self.help_page = HelpPageWindow(self.user_id)
        self.help_page.show()
        self.close()

    # Метод для выхода из приложения
    def confirm_exit(self):
        logger.info(f"Открытие страницы подтверждения выхода из приложения")
        self.second_page = ConfirmPageWindow()
        self.second_page.show()


# Страница записи данных месяца
class NewMonthPage(QMainWindow):
    def __init__(self, user_id, parent_window=None):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Для директивного обращения к странице
        self.user_id = user_id

        # Для последующей записи суммы средств на счёте
        self.parsed_amount = 0

        # Импортируем интерфейс
        self.ui = Ui_NewMonthWindow()
        self.ui.setupUi(self)

        # Для учёта страницы-родителя
        self.parent_window = parent_window

        # Настраиваем таблицу счетов
        self.setup_table()

        # Коннект кнопки для сохранения
        self.ui.save_month.clicked.connect(self.save_accounts)

        # Коннект кнопки для возврата на главную страницу
        self.ui.back_button.clicked.connect(self.back_to_main)

    # Настраиваем таблицу для отображения счетов пользователя
    def setup_table(self):
        logger.info(f"Выполняется настройка таблицы счетов для пользователя: '{self.user_id}'")
        try:
            query = "select account_name from user_account where user_id = ? and active_flag = 1"
            account_names = self.db_conn.execute_query(query, params=(self.user_id,), fetchall=True)

            # Обработка ошибок при отсутствии счетов по пользователю
            if not account_names:
                logger.error(f"Возникла ошибка: для данного пользователя не создано ни одного счёта, "
                             f"user_id: '{self.user_id}'")
                self.ui.error_label.setText(f"Ошибка получения счетов: "
                                            f"для данного пользователя не создано ни одного счёта")
                return

            # Устанавливаем количество строк по количеству счетов пользователя
            self.ui.accounts_table.setRowCount(len(account_names))

            # Задаём наименования заголовков для таблицы
            self.ui.accounts_table.setColumnCount(2)
            self.ui.accounts_table.setHorizontalHeaderLabels(["Наименование счёта", "Сумма \nденежных средств, руб."])

            for row, account in enumerate(account_names):
                # Заполнение первой колонки - наименование счёта
                account_name_item = QTableWidgetItem(account[0])
                account_name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.accounts_table.setItem(row, 0, account_name_item)
                logger.info(f"Создана колонка: '{account_name_item.text()}'")

                # Заполнение второй колонки - поле для ввода суммы денежных средств по счёту
                value_input = QLineEdit(self)
                value_input.setStyleSheet("font: 14pt \"Involve\";\n"
                                          "color: rgb(34, 34, 59);")
                value_input.setPlaceholderText("пример: 00,00")
                value_input.setAlignment(Qt.AlignLeft)
                self.ui.accounts_table.setCellWidget(row, 1, value_input)

            # Корректируем ширину заголовков таблицы
            self.ui.accounts_table.setColumnWidth(0, 350)
            self.ui.accounts_table.setColumnWidth(1, 270)
            logger.info(f"Таблица пользователя успешно создана")
        except Exception as syserr13:
            logger.error(f"Возникла ошибка при настройке таблицы для пользователя, "
                         f"user_id: '{self.user_id}', "
                         f"детали: '{syserr13}'")

    # Сохраняем введённые пользовательские данные
    def save_accounts(self):
        for row in range(self.ui.accounts_table.rowCount()):
            # Проверка на заполнение поля с наименованием счёта
            logger.info(f"Выполняется проверка заполненности строки {row} в таблице")
            account_name_item = self.ui.accounts_table.item(row, 0)
            account_name = account_name_item.text()

            if account_name_item is None or not account_name_item.text():
                logger.warning(f"Обнаружено пустое значение по столбцу 'Наименование счёта', "
                               f"строка: '{row}'")
                self.ui.error_label.setText(f"Проверь, пожалуйста, заполненность наименования счёта в "
                                            f"строке {row + 1}")
                return

            # Проверки на заполнение поля с суммой денежных средств на счёте
            value_input = self.ui.accounts_table.cellWidget(row, 1)
            account_amount_check = value_input.text().strip() if value_input else ""

            # Проверка на наличие поля
            if not account_amount_check:
                logger.warning(f"Обнаружено пустое значение по столбцу 'Сумма денежных средств, руб', "
                               f"строка: '{row}'")
                self.ui.error_label.setText(f"Введи, пожалуйста, сумму денежных средств по счёту '{account_name}' "
                                            f"в строке {row + 1}")
                return
            logger.info(f"Проверка заполненности строки {row} в таблице выполнена успешно")

            # Проверка на наличие во введённом значении содержания только цифр, пробелов, запятых и точек
            if not re.match(r'^[\d\s.,]*$', account_amount_check):
                logger.warning(f"Обнаружены недопустимые знаки по столбцу 'Сумма денежных средств, руб', "
                               f"строка: '{row}'")
                self.ui.error_label.setText(f"Введи, пожалуйста, корректную сумму денежных средств "
                                            f"по счёту {account_name} "
                                            f"в строке {row + 1}")
                return

        # Сохраняем данные пользователя по счетам
        logger.info(f"Выполняется сохранение данных по счетам для пользователя: '{self.user_id}'")
        try:
            # Список для строки по состоянию счетов
            data_to_save = []

            # Время создания записи
            created_data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Забираем значения года и месяца
            year_text = self.ui.comboBox_year.currentText()
            year_num = int(year_text)
            month_num = self.ui.comboBox_month.currentText()

            logger.info(f"Даты создаваемых записей, "
                        f"дата создания: '{created_data}', "
                        f"год: '{year_num}', "
                        f"месяц: '{month_num}'")

            # Вытаскиваем значение для каждого счёта и записываем в список
            for row in range(self.ui.accounts_table.rowCount()):

                # Наименование счёта (пользовательское)
                account_name_item = self.ui.accounts_table.item(row, 0)
                account_name = account_name_item.text()

                # Сумма денежных средств на счёте
                value_input = self.ui.accounts_table.cellWidget(row, 1)
                account_amount = value_input.text().strip()

                # Парсим значение суммы для счёта
                # logger.info(f"Выполняется парсинг введённой суммы на счёте: '{account_amount}'")
                self.parsed_amount = pars_value(account_amount)

                # Проверка результата парсинга
                if self.parsed_amount == -2:
                    self.ui.error_label.setText(f"Введи корректное числовое значение дохода, например: 50000,00")
                    return
                elif self.parsed_amount == -1:
                    self.ui.error_label.setText(f"Похоже, возникла ошибка обработки, обратись к администратору")
                    return

                # Собираем оставшиеся параметры для счёта пользователя - айди счёта и код типа счёта
                try:
                    get_params_query = ("select account_id, account_type_code from user_account "
                                        "where user_id = ? and account_name = ? and active_flag = 1")
                    logger.info(f"Получение дополнительных параметров для счёта пользователя, "
                                f"user_id: '{self.user_id}', "
                                f"наименование счёта: '{account_name}'")
                    account_data = self.db_conn.execute_query(get_params_query, params=(self.user_id, account_name),
                                                              fetchone=True)
                    # Распаковываем данные
                    account_id, account_type_code = account_data

                    # Записываем данные по счёту в список
                    data_to_save.append((self.user_id, year_num, month_num, account_id, account_type_code,
                                         self.parsed_amount, created_data))
                    logger.info(f"Успешная запись данных в список по {row} счёту:"
                                f"user_id: '{self.user_id}', "
                                f"год: '{year_num}', "
                                f"месяц: '{month_num}', "
                                f"id счёта: '{account_data[0]}', "
                                f"код типа счёта: '{account_data[1]}', "
                                f"сумма: '{self.parsed_amount}', "
                                f"дата создания: '{created_data}'")
                except Exception as syserr19:
                    logger.error(f"Ошибка при получении дополнительных данных для счёта пользователя, "
                                 f"user_id: '{self.user_id}', "
                                 f"наименование счёта: '{account_name}', "
                                 f"детали: '{syserr19}'")
                    self.ui.error_label.setText(f"Возникла ошибка при попытке забрать данные по счёту, обратись к "
                                                f"администратору")
                    return

            # Записываем данные в базу данных построчно
            try:
                logger.info(f"Выполняется запись состояния счетов пользователя в базу данных")
                insert_query = ("insert into account_balance (user_id, year, month, account_id, account_type_code, "
                                "amount, created_at) values (?, ?, ?, ?, ?, ?, ?)")
                for data_row in data_to_save:
                    self.db_conn.execute_query(insert_query, params=data_row)
                    logger.info(f"Успешная запись в базу данных по счёту: '{data_row}'")

                logger.info(f"Все данные по счетам успешно записаны в базу данных для пользователя: '{self.user_id}'")
                self.ui.error_label.setText(f"Данные по счетам успешно сохранены, страница сейчас закроется")
                QTimer.singleShot(1500, self.close_after_delay)
            except Exception as syserr64:
                logger.error(f"Возникла ошибка при попытке записи данных в базу данных, "
                             f"данные по счетам: '{data_to_save}', "
                             f"детали: '{syserr64}'")
                self.ui.error_label.setText(
                    f"Возникла ошибка при попытке записи данных по счёту в базу данных, обратись"
                    f"к администратору")
        except Exception as syserr24:
            logger.error(f"Возникла ошибка при сохранении данных по счёту пользователя, "
                         f"user_id: '{self.user_id}', "
                         f"детали: '{syserr24}'")

    # Метод для автоматического закрытия окна ввода данных по счетам
    def close_after_delay(self):
        self.main_page = MainPage(self.user_id, parent=None)
        self.main_page.show()
        self.close()
        self.parent_window.close()

    # Метод для возврата на главную страницу
    def back_to_main(self):
        logger.info(f"Закрытие страницы для записи нового месяца ")
        self.close()


# Страница профиля пользователя
class MyProfilePage(QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Для директивного обращения к странице
        self.user_id = user_id

        # Импортируем интерфейс
        self.ui = Ui_MyProfilePage()
        self.ui.setupUi(self)

        # Получение данных пользователя
        self.get_users_data()

        # Коннект кнопки для редактирования пользовательских данных
        self.ui.edit_button.clicked.connect(self.edit_data)

        # Коннект кнопки для сохранения пользовательских данных
        self.ui.save_button.clicked.connect(self.pre_save_data)

        # Коннект кнопки для отображения пароля
        self.ui.show_pass_button.clicked.connect(self.confirm_showing_pass)

        # Коннект кнопки для открытия страницы главного меню
        self.ui.main_page_button.clicked.connect(self.main_page_button)

        # Коннект кнопки для перехода к счетам пользователя
        self.ui.my_accounts_button.clicked.connect(self.my_accounts_button)

        # Коннект кнопки для перехода к истории счетов
        self.ui.my_writings_button.clicked.connect(self.my_accounts_history)

        # Коннект кнопки для перехода к странице помощи
        self.ui.help_button.clicked.connect(self.help_page)

        # Коннект кнопки для выхода
        self.ui.exit_button.clicked.connect(self.confirm_exit)

    # Заполняем данные пользователя из базы данных
    def get_users_data(self):
        logger.info(f"Выполняется заполнение данных из базы данных пользователя, user_id: '{self.user_id}'")

        # Обнуляем сообщение на случай, если там было что-то написано
        self.ui.error_label.setText(f"")

        # Включаем echo mode для поля с паролем на случай, если страница обновляется
        self.ui.password_line.setEchoMode(QLineEdit.Password)

        try:
            # Получаем все данные пользователя
            first_query = ("select login, password, first_name, last_name, current_income "
                           "from user_data "
                           "where user_id = ?")
            first_result = self.db_conn.execute_query(first_query, params=(self.user_id,), fetchone=True)

            # Распаковываем по переменным
            login, password, firstname, surname, current_income = first_result

            # Если фамилия не указана, то переменную заполняем руками
            if not surname:
                surname = "-"

            if not current_income:
                current_income = "-"

            income = str(current_income)

            # Заполняем поля
            self.ui.login_line.setText(login)
            self.ui.password_line.setText(password)
            self.ui.first_name_line.setText(firstname)
            self.ui.sur_name_line.setText(surname)
            self.ui.income_line.setText(income)
            logger.info(f"Данные для пользователя успешно заполнены, "
                        f"логин: '{login}', "
                        f"пароль: '[HIDDEN]', "
                        f"имя: '{firstname}', "
                        f"фамилия: '{surname}', "
                        f"доход: '{income}'")

            # Устанавливаем параметр, запрещающий вносить изменения
            self.ui.login_line.setReadOnly(True)
            self.ui.password_line.setReadOnly(True)
            self.ui.first_name_line.setReadOnly(True)
            self.ui.sur_name_line.setReadOnly(True)
            self.ui.income_line.setReadOnly(True)
        except Exception as syserr65:
            logger.error(f"Возникла ошибка при получении логина и пароля для пользователя, "
                         f"user_id: '{self.user_id}', "
                         f"детали: '{syserr65}'")
            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")
            return

    # Метод для активации функции редактирования пользовательских полей
    def edit_data(self):

        # На всякий случай включаем echo mode для пароля
        self.ui.password_line.setEchoMode(QLineEdit.Password)
        try:
            logger.info(f"Выполняется активация функции редактирования пользовательских полей")
            self.ui.login_line.setReadOnly(False)
            self.ui.password_line.setReadOnly(False)
            self.ui.first_name_line.setReadOnly(False)
            self.ui.sur_name_line.setReadOnly(False)
            self.ui.income_line.setReadOnly(False)

            # Информируем пользователя о том, что он может начинать вводить новые данные
            self.ui.error_label.setText(f"Теперь ты можешь редактировать свои данные, не забудь сохранить их")
            logger.info(f"Функция редактирования пользовательских полей успешно активирована")
        except Exception as syserr19:
            logger.warning(f"Возникла ошибка при активации функции редактирования пользовательских полей, "
                           f"детали: '{syserr19}'")
            self.ui.error_label.setText(f"Возникла ошибка при активации полей, обратись к администратору")
            return

    # Метод для сохранения пользовательских данных
    def pre_save_data(self):
        logger.info(f"Выполняется сохранение пользовательских данных")
        # Перед записью проверяем содержимое полей
        self.input_login = self.ui.login_line.text()
        self.input_password = self.ui.password_line.text()
        self.input_firstname = self.ui.first_name_line.text()
        self.input_surname = self.ui.sur_name_line.text()
        input_income = self.ui.income_line.text()

        # Проверяем логин
        if not self.input_login:
            logger.warning(f"Ошибка сохранения пользовательских данных: не заполнен логин")
            self.ui.error_label.setText(f"Введи, пожалуйста, логин")
            return

        if " " in self.input_login:
            logger.warning(f"Ошибка сохранения пользовательских данных: логин содержит пробелы")
            self.ui.error_label.setText(f"Логин не может содержать пробелы")
            return

        # Проверяем пароль
        if not self.input_password:
            logger.warning(f"Ошибка сохранения пользовательских данных: не заполнен пароль")
            self.ui.error_label.setText(f"Введи, пожалуйста, пароль")
            return

        if " " in self.input_password:
            logger.warning(f"Ошибка сохранения пользовательских данных: пароль содержит пробелы")
            self.ui.error_label.setText(f"Пароль не может содержать пробелы")
            return

        # Проверяем имя
        if not self.input_firstname:
            logger.warning(f"Ошибка сохранения пользовательских данных: не заполнено имя")
            self.ui.error_label.setText(f"Введи, пожалуйста, имя")
            return

        # Доход обязательно парсим, если введён
        if input_income:
            self.input_parsed_income = pars_value(input_income)

            # Проверка результата парсинга
            if self.input_parsed_income == -2:
                self.ui.error_label.setText(f"Похоже, ты ввёл некорректное значение дохода, вот пример: 10000,00")
                return
            elif self.input_parsed_income == -1:
                self.ui.error_label.setText(f"Похоже, возникла ошибка обработки, обратись к администратору")
                return
        else:
            self.input_parsed_income = input_income

        # Сохранение данных с вводом пароля в окне-подтверждении
        logger.info(f"Открытие окна для подтверждения пароля при сохранении данных")
        self.confirm_pass_page = ConfirmPasswordWindow(self.user_id, self)
        self.confirm_pass_page.result_signal.connect(self.save_data)
        self.confirm_pass_page.exec_()

    # Сохранение данных при правильно введённом пароле
    def save_data(self, result):
        if result:
            logger.info(f"Проверка пароля выполнена успешно, "
                        f"продолжается сохранение данных для пользователя: '{self.user_id}'")
        try:
            upd_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = ("update user_data "
                     "set login = ?, password = ?, first_name = ?, last_name = ?, current_income = ?, update_date = ? "
                     "where user_id = ?")
            self.db_conn.execute_query(query, params=(self.input_login, self.input_password, self.input_firstname,
                                                      self.input_surname, self.input_parsed_income, upd_date,
                                                      self.user_id))
            logger.info(f"Сохранение данных пользователя прошло успешно, "
                        f"user_id: '{self.user_id}', "
                        f"логин: '{self.input_login}', "
                        f"пароль: '[HIDDEN]', "
                        f"имя: '{self.input_firstname}', "
                        f"фамилия: '{self.input_surname}', "
                        f"доход: '{self.input_parsed_income}', "
                        f"время апдейта: '{upd_date}'")

            # Выводим сообщение для пользователя на 3,5 секунды
            self.ui.error_label.setText(f"Данные успешно сохранены, страница сейчас обновится")

            # Обновляем данные на странице
            QTimer.singleShot(2500, self.update_after_delay)
        except Exception as syserr47:
            logger.error(f"Произошла ошибка при сохранении данных пользователя, "
                         f"user_id: '{self.user_id}', "
                         f"детали: '{syserr47}'")

    # Метод для обновления данных пользователя после сохранения
    def update_after_delay(self):
        self.get_users_data()

    # Открытие специального окна-подтверждения для отображения пароля
    def confirm_showing_pass(self):
        logger.info(f"Открытие окна для подтверждения пароля")
        self.confirm_page = ConfirmPasswordWindow(self.user_id, self)
        self.confirm_page.result_signal.connect(self.show_pass)
        self.confirm_page.exec_()

    # Метод для отображения пароля пользователя
    def show_pass(self, result):
        if result:
            logger.info(f"Проверка пароля выполнена успешно, "
                        f"активация отображения пароля для пользователя: '{self.user_id}'")
            self.ui.password_line.setEchoMode(QLineEdit.Normal)

    # Метод для открытия главной страницы
    def main_page_button(self):
        logger.info(f"Открытие главной страницы приложения")
        self.main_page = MainPage(self.user_id)
        self.main_page.show()
        self.close()

    # Метод для перехода к странице счетов пользователя
    def my_accounts_button(self):
        logger.info(f"Открытие страницы счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountsPage(self.user_id)
        self.accounts_page.show()
        self.close()

    # Метод для перехода к истории счетов пользователя
    def my_accounts_history(self):
        logger.info(f"Открытие страницы истории счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountHistoryWindow(self.user_id)
        self.accounts_page.show()
        self.close()

    # Метод для перехода к странице помощи
    def help_page(self):
        logger.info(f"Открытие страницы помощи")
        self.help_page = HelpPageWindow(self.user_id)
        self.help_page.show()
        self.close()

    # Метод для выхода из приложения
    def confirm_exit(self):
        logger.info(f"Открытие страницы подтверждения выхода из приложения")
        self.second_page = ConfirmPageWindow()
        self.second_page.show()


# Окно для подтверждения пароля пользователя
class ConfirmPasswordWindow(QDialog):
    # Результат подтверждения пароля
    result_signal: pyqtSignal = pyqtSignal(bool)

    def __init__(self, user_id, parent=None):
        super().__init__(parent)

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Для директивного обращения к странице
        self.user_id = user_id

        # Импортируем интерфейс
        self.ui = Ui_ConfirmPasswordWindow()
        self.ui.setupUi(self)

        # Коннект кнопки для подтверждения пароля
        self.ui.confirm_button.clicked.connect(self.check_password)

    # Метод для проверки правильности введённого пароля
    def check_password(self):
        logger.info(f"Выполняется проверка корректности ввода пароля для пользователя: '{self.user_id}'")
        password = self.ui.pass_input.text()

        # Проверка пароля на ввод
        if not password:
            self.ui.error_label.setText("Введи, пожалуйста, пароль пользователя")
            logger.warning(f"Неуспешная попытка проверки: не введён пароль")
            return

        # Проверка пароля на наличие пробелов
        if " " in password:
            self.ui.error_label.setText("Пароль пользователя не может содержать пробел")
            logger.warning(f"Неуспешная попытка проверки: пароль содержит пробел")
            return

        # Ищем пароль пользователя по айди для проверки
        try:
            check_query = "select password from user_data where user_id = ?"
            check_password = self.db_conn.execute_query(check_query, params=(self.user_id,), fetchone=True)

            # Если результат был получен, то отправляем сигнал и закрываем окно
            if password and password == check_password[0]:
                logger.info(f"Успешная проверка на корректность введённого пароля, действие разрешено")
                self.result_signal.emit(True)
                self.accept()
            else:
                logger.warning(f"Неуспешная попытка проверки: введённый пароль неправильный")
                self.ui.error_label.setText(f"Неправильный пароль")
                return
        except Exception as syserr17:
            self.ui.error_label.setText(f"Возникла ошибка базы данных, обратись к администратору")
            logger.error(f"Возникла ошибка при выполнении проверки корректности введённого пароля, "
                         f"user_id: '{self.user_id}', "
                         f"пароль: '[HIDDEN]', "
                         f"детали: '{syserr17}'")
            return


# Страница счетов пользователя
class MyAccountsPage(QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Для директивного обращения к странице
        self.user_id = user_id

        # Импортируем интерфейс
        self.ui = Ui_MyAccountsPage()
        self.ui.setupUi(self)

        # Для заполнения информации по счетам пользователей
        self.accounts = []

        # Отладка отображения счетов пользователя
        self.setup_accounts()

        # Коннект кнопки для добавления новых счетов
        self.ui.add_button.clicked.connect(self.add_an_account)

        # Коннект кнопки для редактирования счётов
        self.ui.rename_button.clicked.connect(self.edit_account)

        # Коннект кнопки для открытия страницы главного меню
        self.ui.main_page_button.clicked.connect(self.main_page_button)

        # Коннект кнопки для перехода к профилю пользователя
        self.ui.my_profile_button.clicked.connect(self.my_profile_button)

        # Коннект кнопки для перехода к истории счетов
        self.ui.my_writings_button.clicked.connect(self.my_accounts_history)

        # Коннект кнопки для перехода к странице помощи
        self.ui.help_button.clicked.connect(self.help_page)

        # Коннект кнопки для выхода
        self.ui.exit_button.clicked.connect(self.confirm_exit)

    # Метод для генерации и отображения счетов пользователя
    def setup_accounts(self):
        logger.info(f"Выполняется настройка для отображения счетов пользователя")

        # Получаем информацию по счетам пользователя
        try:
            get_query = ("select account_id, account_name, account_type_name, account_type_code "
                         "from user_account "
                         "where user_id = ? and active_flag = 1")
            self.accounts = self.db_conn.execute_query(get_query, params=(self.user_id,), fetchall=True)
            logger.info(f"Информация по счетам пользователя успешно получена")
        except Exception as syserr31:
            logger.error(f"Возникла ошибка при получении счетов пользователя, "
                         f"user_id: '{self.user_id}', "
                         f"детали: '{syserr31}'")
            self.ui.error_label.setText(f"Возникла ошибка базы данных при получении данных о счетах, "
                                        f"обратись к администратору")
            return

        # Создаем вертикальный layout для размещения форм счетов
        layout = QVBoxLayout(self.ui.scroll_widget)

        # Переменная для подсчёта количества счетов пользователя
        self.count_accounts = 0

        # Выполняется настройка отображения информации по счетам пользователя
        for account in self.accounts:
            # Горизонтальный контейнер для одного счёта
            account_layout = QHBoxLayout()

            # Параметры для заголовка "Наименование счёта" (пользовательское)
            account_name_label = QLabel(f"Наименование счёта: ")
            account_name_label.setStyleSheet("font: 14pt \"Involve\";\n"
                                             "color: rgb(34, 34, 59);")
            account_name_label.setAlignment(Qt.AlignCenter)
            account_name_label.setFixedHeight(40)
            account_name_label.setFixedWidth(230)

            # Параметры для поля "Наименование счёта" (пользовательское)
            account_name = QLineEdit()
            account_name.setText(account[1])  # 1 - индекс наименования счёта в кортеже account
            account_name.setReadOnly(True)
            account_name.setStyleSheet("font: 14pt 'Involve';"
                                       "color: rgb(34, 34, 59); "
                                       "border-radius: 15px;"
                                       "background-color: rgb(242, 233, 228);")
            account_name.setAlignment(Qt.AlignLeft)
            account_name.setAlignment(Qt.AlignVCenter)
            account_name.setFixedHeight(40)
            account_name.setFixedWidth(320)

            # Параметры для заголовка "Тип счёта"
            account_type_name_label = QLabel(f"Тип счёта:")
            account_type_name_label.setStyleSheet("font: 14pt \"Involve\";\n"
                                                  "color: rgb(34, 34, 59);")
            account_type_name_label.setAlignment(Qt.AlignLeft)
            account_type_name_label.setAlignment(Qt.AlignVCenter)
            account_type_name_label.setFixedHeight(40)
            account_type_name_label.setFixedWidth(105)

            # Параметры для поля "Тип счёта"
            account_type_name = QLabel(account[2])  # 2 - индекс наименования типа счёта в кортеже account
            account_type_name.setStyleSheet("font: 14pt 'Involve'; "
                                            "color: rgb(34, 34, 59); "
                                            "border-radius: 15px;"
                                            "background-color: rgb(242, 233, 228);")
            account_type_name.setAlignment(Qt.AlignLeft)
            account_type_name.setAlignment(Qt.AlignVCenter)
            account_type_name.setFixedHeight(40)
            account_type_name.setFixedWidth(250)

            # Кнопка для удаления счёта
            delete_button = QPushButton()
            delete_button.setStyleSheet("background-image: url(:/icons/delete_icon_40x40.png);"
                                        "background-color: rgb(255, 255, 255);")
            delete_button.setFixedWidth(40)
            delete_button.setFixedHeight(40)

            # Коннект кнопки для удаления счёта
            delete_button.clicked.connect(partial(self.accept_delete_account, account[0]))

            # Добавляем виджеты в горизонтальный layout
            account_layout.addWidget(account_name_label)
            account_layout.addWidget(account_name)
            account_layout.addWidget(account_type_name_label)
            account_layout.addWidget(account_type_name)
            account_layout.addWidget(delete_button)

            # Фиксируем размер спейсеров
            spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
            account_layout.addSpacerItem(spacer)

            # Добавляем горизонтальный layout в основной вертикальный layout
            layout.addLayout(account_layout)

            # Обновляем количество счетов
            self.count_accounts = self.count_accounts + 1

        # Устанавливаем обновленный layout для scroll_widget
        self.ui.scroll_widget.setLayout(layout)
        logger.info(f"Отображение счетов пользователя успешно выполнено, количество счетов: '{self.count_accounts}'")

    # Метод для подтверждения удаления счёта (переноса счёта в архив)
    def accept_delete_account(self, account_id):
        # Если у пользователя 2 счёта и более, то мы продолжаем обрабатывать запрос на удаление счёта
        if self.count_accounts > 1:
            logger.info(f"Открытие окна для подтверждения удаления счёта")
            self.confirm_delete = ConfirmDeleteAccount(self.user_id, account_id, self.count_accounts,
                                                       parent_window=self)
            self.confirm_delete.show()
        else:
            # Если же у пользователя один или менее счёт, то уведомляем о том, что он не может удалить единственный счёт
            if self.count_accounts <= 1:
                logger.info(f"Количество счётов пользователя менее или равно одному, удаление невозможно")
                self.reject_delete = SuccessDeleteWindow(self.user_id, 2, self.count_accounts, parent_window=self)
                self.reject_delete.show()

    # Метод для добавления новых счетов
    def add_an_account(self):
        logger.info(f"Открытие окна создания счетов пользователя")
        self.new_account_page = NewAccountsWindow(self.user_id, self.count_accounts, parent_window=self)
        self.new_account_page.show()

    # Метод для редактирования счетов пользователя
    def edit_account(self):
        logger.info(f"Открытия окна редактирования счетов пользователя")
        self.edit_accounts = EditAccountsWindow(self.user_id, self.accounts, parent_window=self)
        self.edit_accounts.show()

    # Метод для открытия главной страницы
    def main_page_button(self):
        logger.info(f"Открытие главной страницы приложения")
        self.main_page = MainPage(self.user_id)
        self.main_page.show()
        self.close()

    # Метод для перехода к странице профиля пользователя
    def my_profile_button(self):
        logger.info(f"Открытие страницы профиля для пользователя: '{self.user_id}'")
        self.profile_page = MyProfilePage(self.user_id)
        self.profile_page.show()
        self.close()

    # Метод для перехода к истории счетов пользователя
    def my_accounts_history(self):
        logger.info(f"Открытие страницы истории счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountHistoryWindow(self.user_id)
        self.accounts_page.show()
        self.close()

    # Метод для перехода к странице помощи
    def help_page(self):
        logger.info(f"Открытие страницы помощи")
        self.help_page = HelpPageWindow(self.user_id)
        self.help_page.show()
        self.close()

    # Метод для выхода из приложения
    def confirm_exit(self):
        logger.info(f"Открытие страницы подтверждения выхода из приложения")
        self.second_page = ConfirmPageWindow()
        self.second_page.show()


# Окно для подтверждения удаления счёта пользователя
class ConfirmDeleteAccount(QMainWindow):
    def __init__(self, user_id, account_id, count_accounts, parent_window=None):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Импортируем интерфейс
        self.ui = Ui_ConfirmDeleteWindow()
        self.ui.setupUi(self)

        # Для обработки запроса на удаление счёта пользователя
        self.user_id = user_id  # Айди пользователя
        self.account_id = account_id  # Айди счёта
        self.parent_window = parent_window  # Установление окна-родителя - MyAccountsPage
        self.count_accounts = count_accounts  # Количество счетов пользователя

        # Коннект кнопок для подтверждения и удаления счёта
        self.ui.yes_button.clicked.connect(self.delete_account)
        self.ui.no_button.clicked.connect(self.reject)

    # Метод для удаления счёта пользователя (переноса в архив)
    def delete_account(self):
        logger.info(f"Выполняется архивирование счёта: '{self.account_id}'")
        try:
            # Устанавливаем дату архивации счёта
            deactivate_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            archive_query = ("update user_account "
                             "set active_flag = 0, deactivate_date = ?, update_date = ? "
                             "where user_id = ? and account_id = ?")
            self.db_conn.execute_query(archive_query, params=(deactivate_date, update_date,
                                                              self.user_id, self.account_id))
            logger.info(f"Счёт успешно заархивирован, "
                        f"user_id: '{self.user_id}', "
                        f"айди счёта: '{self.account_id}', "
                        f"дата: '{deactivate_date}'")

            # Открываем окно для пользователя - если 1 - успешное удаление счёта
            logger.info(f"Открытие окна для информирования пользователя об успешном статусе удаления счёта")
            self.success_window = SuccessDeleteWindow(self.user_id, 1, self.count_accounts, self.parent_window)
            self.success_window.show()
            self.close()
        except Exception as syserr40:
            logger.error(f"Возникла ошибка при удалении счёта пользователя, "
                         f"user_id: '{self.user_id}', "
                         f"айди счёта: '{self.account_id}', "
                         f"детали: '{syserr40}'")
            self.error_window = SuccessDeleteWindow(self.user_id, 0, self.count_accounts, self.parent_window)
            self.error_window.show()
            self.close()

    # Метод для обработки отказа пользователя от удаления счёта
    def reject(self):
        logger.info(f"Закрытие окна для подтверждения удаления счёта, пользователь не подтвердил удаление")
        self.close()


# Окно успешного удаления счёта пользователя
class SuccessDeleteWindow(QMainWindow):
    def __init__(self, user_id, var, count_accounts, parent_window=None):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для директивного обращения к странице
        self.user_id = user_id

        # Для учёта количества счетов пользователя
        self.count_accounts = count_accounts

        # Импортируем интерфейс
        self.ui = Ui_SuccessDeleteWindow()
        self.ui.setupUi(self)

        # Сохраняем страницу-родителя - MyAccountsPage
        self.parent_window = parent_window

        # Если у пользователя один или менее счёт, то информируем о невозможности удаления
        if self.count_accounts <= 1:
            self.ui.confirm_label.setText(f"Ты не можешь удалить свой единственный счёт")
            QTimer.singleShot(1500, self.close_window)
        else:
            # Если var = 1, то это значит, что удаление окна произошло успешно, информируем пользователя и обновляем
            # страницу со счетами
            if var == 1:
                QTimer.singleShot(1200, self.open_my_accounts)
            # Если же var = 0, то удаление не случилось, возникла ошибка, информируем пользователя и открываем снова
            # страницу со счетами
            else:
                if var == 0:
                    self.ui.confirm_label.setText(f"Возникла ошибка при удалении счёта, обратись к администратору")
                    QTimer.singleShot(1200, self.open_my_accounts)

    # Метод для перехода к странице счетам пользователя
    def open_my_accounts(self):
        logger.info(f"Открытие страницы счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountsPage(self.user_id)
        self.accounts_page.show()
        self.parent_window.close()
        self.close()

    # Метод для закрытия окна при отказе в удалении единственного счёта
    def close_window(self):
        self.close()


# Окно создания новых счетов пользователя
class NewAccountsWindow(QMainWindow):
    def __init__(self, user_id, count_accounts, parent_window=None):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Импортируем интерфейс
        self.ui = Ui_NewAccountsWindow()
        self.ui.setupUi(self)

        # Для директивного обращения к странице
        self.user_id = user_id

        # Для учёта количества счетов пользователя
        self.count_accounts = count_accounts  # Текущее количество счетов
        max_count_accounts = 10 - count_accounts  # Максимально возможное для создания количество счетов

        # Для учёта страницы-родителя
        self.parent_window = parent_window

        # Устанавливаем ограничения по количеству создаваемых счетов
        self.ui.spinBox.setMinimum(1)
        self.ui.spinBox.setMaximum(int(max_count_accounts))

        # Список для хранения данных по созданным счетам
        self.account_forms = []

        # Список для сохранения данных по текущим счетам пользователя
        self.current_accounts = []

        # Коннект кнопки для создания форм
        self.ui.create_button.clicked.connect(self.generate_account_forms)

        # Коннект кнопки для сохранения счетов
        self.ui.save_button.clicked.connect(self.save_accounts)

        # Коннект кнопки для возврата к счетам
        self.ui.back_button.clicked.connect(self.back)

    # Метод для генерации определённого количества форм для заполнения информации по счетам
    def generate_account_forms(self):
        # Устанавливаем лэйаут для главного виджета
        layout = QVBoxLayout(self.ui.accounts_forms)
        self.ui.accounts_forms.setLayout(layout)

        # Устанавливаем количество форм
        num_forms = self.ui.spinBox.value()
        logger.info(f"Выполняется генерация форм счетов для заполнения в количестве: '{num_forms}'")

        # Очистка виджета для заполнения новыми данными
        layout = self.ui.accounts_forms.layout()
        try:
            for i in reversed(range(layout.count())):
                widget_to_remove = layout.itemAt(i).widget()
                if widget_to_remove:
                    widget_to_remove.deleteLater()
            logger.info(f"Выполнена очистка форм для заполнения счетов пользователя")
        except Exception as syserr78:
            logger.error(f"Возникла ошибка при очистке формы: '{syserr78}'")
            self.ui.error_label.setText(f"Возникла непредвиденная ошибка при очистке форм, обратись к администратору")
            return

        # Генерация форм
        try:
            # Также очищаем список информации по счетам
            self.account_forms.clear()

            # Генерация форм
            for i in range(num_forms):
                form_widget = QtWidgets.QWidget()
                form_layout = QHBoxLayout(form_widget)
                form_widget.setLayout(form_layout)

                # Заголовок "Наименование счёта"
                account_name_label = QtWidgets.QLabel(f"Счёт №{i + 1}: ")
                account_name_label.setStyleSheet("font: 12pt \"Involve\";\n"
                                                 "color: rgb(34, 34, 59);")

                # Поле для ввода наименования
                account_name_input = QtWidgets.QLineEdit()
                account_name_input.setStyleSheet("border-radius: 15px;\n"
                                                 "background-color: rgb(242, 233, 228);\n"
                                                 "font: 12pt \"Involve\";\n"
                                                 "color: rgb(34, 34, 59)")
                account_name_input.setPlaceholderText(" наименование счёта")
                account_name_input.setFixedHeight(30)
                account_name_input.setFixedWidth(290)

                # Заголовок для типа счёта
                account_type_label = QtWidgets.QLabel("Тип счёта: ")
                account_type_label.setStyleSheet("font: 12pt \"Involve\";\n"
                                                 "color: rgb(34, 34, 59);")

                # Список для выбора типа счёта
                account_type_dropdown = QtWidgets.QComboBox()
                account_type_dropdown.setStyleSheet("font: 12pt \"Involve\";\n"
                                                    "color: rgb(34, 34, 59);\n"
                                                    "background-color: rgb(242, 233, 228);\n"
                                                    "border-radius: 15px;")
                account_type_dropdown.addItems(
                    ["Карточный счёт", "Текущий счёт", "Резервный счёт", "Накопительный счёт", "Валютный счёт", "Вклад",
                     "Займ"])
                account_type_dropdown.setFixedHeight(30)
                account_type_dropdown.setFixedWidth(190)

                # Добавляем форму в лэйаут
                form_layout.addWidget(account_name_label)
                form_layout.addWidget(account_name_input)
                form_layout.addWidget(account_type_label)
                form_layout.addWidget(account_type_dropdown)

                # Задаём спэйсер
                spacer_forms = QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
                form_layout.addItem(spacer_forms)

                # Добавляем созданную форму в итоговый лэйаут
                self.ui.accounts_forms.layout().addWidget(form_widget)

                # Дозаписываем данные по счёту в список
                self.account_forms.append({
                    "name_input": account_name_input,
                    "type_dropdown": account_type_dropdown
                })

            # Информируем об успешной генерации форм
            logger.info(f"Успешное выполнение генерации форм")
        except Exception as syserr36:
            logger.error(f"Возникла ошибка при генерации форм: '{syserr36}'")
            self.ui.error_label.setText(f"Возникла ошибка при генерации форм, обратись к администратору")
            return

        # Заберём текущие наименования и типы активных счетов пользователя для последующей проверки
        try:
            select_query = ("select account_name, account_type_name from user_account "
                            "where user_id = ? and active_flag = 1")
            self.current_accounts = self.db_conn.execute_query(select_query, params=(self.user_id,), fetchall=True)
        except Exception as syserr86:
            logger.error(f"Возникла ошибка при получении текущих счетов пользователя,"
                         f"детали: '{syserr86}'")
            self.ui.error_label.setText(f"Возникла непредвиденная ошибка при получении списка твоих счетов, "
                                        f"обратись к администратору")
            return

    # Метод для сохранения счетов
    def save_accounts(self):
        logger.info(f"Выполняется сохранение счетов пользователя")

        # Список для данных по новым счетам
        accounts_data = []

        # Теперь собираем введённые пользователем данные на запись
        try:
            for account_form in self.account_forms:
                account_users_name = account_form["name_input"].text()
                account_type_name = account_form["type_dropdown"].currentText()

                # Проверка на заполнение полей
                if not account_users_name:
                    logger.warning(f"Неуспешная попытка сохранения: не заполнено(ы) наименование(я) счёта(ов)")
                    self.ui.error_label.setText(f" Похоже, есть незаполненные наименования счетов, "
                                                f"проверь их и попробуй ещё")
                    return

                # Проверка на уникальность
                if (account_users_name, account_type_name) in self.current_accounts:
                    logger.warning(f"Неуспешная попытка сохранения: пользователь пытается создать счёт с наименованием "
                                   f"и типом, которые уже существуют: "
                                   f"наименование: '{account_users_name}', "
                                   f"тип счёта: '{account_type_name}'")
                    self.ui.error_label.setText(f"Похоже, что у тебя уже есть счёт с "
                                                f"наименованием '{account_users_name}' и "
                                                f"типом '{account_type_name}', счета не могут быть идентичными")
                    return

                # Если всё ок, то записываем данные по счёту в итоговый список
                accounts_data.append({
                    "user_id": self.user_id,
                    "account_username": account_users_name,
                    "account_type_name": account_type_name
                })
        except Exception as syserr89:
            logger.error(f"Возникла ошибка при попытке сохранить новые счета пользователя, "
                         f"детали: '{syserr89}'")
            self.ui.error_label.setText(f"Возникла непредвиденная ошибка при попытке сохранить твои счета, обратись "
                                        f"к администратору")

        # Заливаем данные в базу данных
        try:
            # Заглушки для даты создания и даты архивации счёта
            create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            deactivate_date = "9999-12-12 23:59:59"
            update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Забираем каждый счёт отдельно
            for account in accounts_data:
                user_id = account["user_id"]
                account_name = account["account_username"]
                account_type_name = account["account_type_name"]

                # Потом дёргаем дополнительные данные для счёта
                account_type_code = self.get_acc_type_code(account_type_name)
                account_type = self.get_acc_type(account_type_code)
                logger.info(f"Успешное получение дополнительных данных из справочника по счёту: '{account_name}'")

                # Записываем информацию в базу данных
                insert_query = ("insert into user_account "
                                "(user_id, account_name, account_type_name, account_type, "
                                "account_type_code, create_date, deactivate_date, update_date) "
                                "values (?, ?, ?, ?, ?, ?, ?, ?);")
                self.db_conn.execute_query(insert_query,
                                           params=(user_id, account_name, account_type_name, account_type,
                                                   account_type_code, create_date, deactivate_date, update_date))

            # После успешного сохранения информируем пользователя и переходим к главной странице
            logger.info(f"Выполнено успешное сохранение счетов пользователя в базу данных")
            self.ui.error_label.setText(f"Твои счета были успешно сохранены")

            # Возвращаемся на страницу счетов пользователя после небольшой задержки
            QTimer.singleShot(1800, self.account_page_after_delay)
        except Exception as syserr98:
            self.ui.error_label.setText(f"Возникла ошибка при попытке записать твои данные в базу данных, "
                                        f"обратись к администратору")
            logger.error(f"Возникла ошибка при попытке записи данных в базу данных, "
                         f"детали: '{syserr98}'")
            return

    # Забираем код типа счёта
    def get_acc_type_code(self, account_type_name):
        query = "select account_type_code from account_type where account_type_name = ?"
        result = self.db_conn.execute_query(query, params=(account_type_name,), fetchone=True)
        if result:
            return result[0]
        else:
            return None

    # Забираем тип счёта
    def get_acc_type(self, account_type_code):
        query = "select account_type from account_type where account_type_code = ?"
        result = self.db_conn.execute_query(query, params=(account_type_code,), fetchone=True)
        if result:
            return result[0]
        else:
            return None

    # Метод для возврата к странице счетов пользователя после сохранения
    def account_page_after_delay(self):
        logger.info(f"Открытие страницы счетов пользователя")
        self.new_page = MyAccountsPage(self.user_id)
        self.new_page.show()
        self.close()
        self.parent_window.close()

    # Метод для возврата к счетам пользователя
    def back(self):
        logger.info(f"Закрытие окна создания счетов пользователя")
        self.close()


# Окно редактирования счетов пользователя
class EditAccountsWindow(QMainWindow):
    def __init__(self, user_id, current_accounts, parent_window=None):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Импортируем интерфейс
        self.ui = Ui_EditAccountsWindow()
        self.ui.setupUi(self)

        # Для директивного обращения к странице
        self.user_id = user_id

        # Для учёта страницы-родителя
        self.parent_window = parent_window

        # Список счетов пользователя
        self.accounts = current_accounts

        # Отфильтрованный список счетов пользователя
        self.filtered_accounts = []

        # # Список для хранения ссылок на виджеты
        self.account_widgets = []

        # Настройка отображения страницы
        self.setup_page()

        # Коннект кнопки для сохранения счетов пользователя
        self.ui.save_button.clicked.connect(self.save_accounts)

        # Коннект кнопки для возврата к счетам
        self.ui.back_button.clicked.connect(self.back)

    # Метод для настройки отображения страницы
    def setup_page(self):
        try:
            logger.info(f"Выполняется настройка отображения счетов пользователя для их редактирования")

            # Создаем вертикальный layout для размещения форм счетов
            layout = QVBoxLayout(self.ui.accounts_forms)

            # Создание форм для редактирования информации по счетам
            for account in self.accounts:
                # Горизонтальный контейнер для одного счёта
                account_layout = QHBoxLayout()

                account_name_label = QLabel(f"Наименование счёта: ")
                account_name_label.setStyleSheet("font: 12pt \"Involve\";\n"
                                                 "color: rgb(34, 34, 59);")
                account_name_label.setAlignment(Qt.AlignCenter)
                account_name_label.setFixedHeight(30)

                # Параметры для поля "Наименование счёта" (пользовательское)
                account_name = QLineEdit()
                account_name.setText(account[1])  # 1 - индекс наименования счёта в кортеже account
                account_name.setReadOnly(False)
                account_name.setStyleSheet("font: 12pt 'Involve';"
                                           "color: rgb(34, 34, 59); "
                                           "border-radius: 15px;"
                                           "background-color: rgb(242, 233, 228);")
                account_name.setAlignment(Qt.AlignLeft)
                account_name.setAlignment(Qt.AlignVCenter)
                account_name.setFixedHeight(30)
                account_name.setFixedWidth(210)

                # Параметры для заголовка "Тип счёта"
                account_type_name_label = QLabel(f"Тип счёта:")
                account_type_name_label.setStyleSheet("font: 12pt \"Involve\";\n"
                                                      "color: rgb(34, 34, 59);")
                account_type_name_label.setAlignment(Qt.AlignLeft)
                account_type_name_label.setAlignment(Qt.AlignVCenter)
                account_type_name_label.setFixedHeight(30)

                # Параметры для поля "Тип счёта"
                account_type_name = QLabel(f"{account[2]}")
                account_type_name.setStyleSheet("font: 12pt 'Involve'; "
                                                "color: rgb(34, 34, 59); "
                                                "border-radius: 15px;"
                                                "background-color: rgb(242, 233, 228);")
                # account_type_name.setCurrentText(account[2])  # 2 - индекс наименования типа счёта в кортеже account
                account_type_name.setFixedHeight(30)
                account_type_name.setFixedWidth(190)

                # Добавляем виджеты в горизонтальный layout
                account_layout.addWidget(account_name_label)
                account_layout.addWidget(account_name)
                account_layout.addWidget(account_type_name_label)
                account_layout.addWidget(account_type_name)

                # Фиксируем размер спейсеров
                spacer = QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
                account_layout.addSpacerItem(spacer)

                # Добавляем горизонтальный layout в основной вертикальный layout
                layout.addLayout(account_layout)

                # Сохраняем ссылки на виджеты в список
                self.account_widgets.append({
                    "account_id": account[0],
                    "account_name": account_name,
                    "account_type_name": account_type_name
                })

            # Устанавливаем обновленный layout для scroll_widget
            self.ui.accounts_forms.setLayout(layout)
            logger.info(f"Отображение счетов пользователя успешно выполнено")
        except Exception as syserr67:
            logger.error(f"Возникла ошибка при настройке страницы для редактирования счетов, "
                         f"детали: '{syserr67}'")
            self.ui.error_label.setText(f"Возникла ошибка при настройке отображения твоих счетов, обратись "
                                        f"к администратору")
            return

    # Метод для сохранения счетов пользователя
    def save_accounts(self):
        logger.info(f"Выполняется сохранение счетов пользователя")

        # Список для сохранения новых данных по счетам
        accounts_data = []

        # Теперь собираем введённые пользователем данные на запись
        try:
            for account_form in self.account_widgets:
                account_name = account_form["account_name"].text()
                account_type_name = account_form["account_type_name"].text()
                account_id = account_form["account_id"]

                # Проверка на заполнение полей
                if not account_name:
                    logger.warning(f"Неуспешная попытка сохранения: не заполнено(ы) наименование(я) счёта(ов)")
                    self.ui.error_label.setText(f" Похоже, есть незаполненные наименования счетов, "
                                                f"проверь их и попробуй ещё")
                    return

                # Проверка на уникальность наименования
                filtered_id = account_id

                # Фильтруем список - отбираем все счета, кроме того, который редактируется на данный момент
                self.filtered_accounts = [account for account in self.accounts if account[0] != filtered_id]

                # Список для последующей проверки уникальности
                curr_accounts = []

                for curr_account in self.filtered_accounts:
                    curr_accounts.append((
                        curr_account[1],
                        curr_account[2]
                    ))

                # Смотрим, есть ли у пользователя уже такой счёт
                if (account_name, account_type_name) in curr_accounts:
                    logger.warning(f"Неуспешная попытка сохранения: счёт с таким наименование и типом уже существует, "
                                   f"наименование: '{account_name}', "
                                   f"тип счёта: '{account_type_name}'")
                    self.ui.error_label.setText(f"Похоже, что у тебя уже есть счёт с "
                                                f"наименованием '{account_name}' и "
                                                f"типом '{account_type_name}', счета не могут быть идентичными")
                    return

                # Если всё ок, то записываем
                accounts_data.append({
                    "user_id": self.user_id,
                    "account_id": account_id,
                    "account_username": account_name,
                    "account_type_name": account_type_name
                })
        except Exception as syserr71:
            logger.error(f"Возникла ошибка при сохранении счетов пользователя, "
                         f"детали: '{syserr71}'")
            self.ui.error_label.setText(f"Возникла ошибка при сохранении новых данных твоих счетов, "
                                        f"обратись к администратору")
            return

        # Далее заливаем данные в базу данных
        try:
            # Задаём дату апдейта счёта
            update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Заливаем каждый счёт отдельно
            for account in accounts_data:
                user_id = account["user_id"]
                account_id = account["account_id"]
                account_name = account["account_username"]
                account_type_name = account["account_type_name"]

                # Потом дёргаем дополнительные данные для счёта
                account_type_code = self.get_acc_type_code(account_type_name)
                account_type = self.get_acc_type(account_type_code)
                logger.info(f"Успешное получение дополнительных данных из справочника по счёту: '{account_name}'")

                update_query = ("update user_account "
                                "set account_name = ?, account_type_name = ?, account_type = ?, "
                                "account_type_code = ?, update_date = ? "
                                "where user_id = ? and account_id = ?")
                self.db_conn.execute_query(update_query, params=(account_name, account_type_name, account_type,
                                                                 account_type_code, update_date, user_id, account_id))

            # После успешного сохранения информируем пользователя и переходим к главной странице
            logger.info(f"Выполнено успешное сохранение счетов пользователя в базу данных")
            self.ui.error_label.setText(f"Твои счета были успешно сохранены")

            # Возвращаемся на страницу счетов пользователя после небольшой задержки
            QTimer.singleShot(1800, self.account_page_after_delay)
        except Exception as syserr36:
            logger.error(f"Возникла ошибка при сохранении данных по счёту в базу данных, "
                         f"детали: '{syserr36}'")
            self.ui.error_label.setText(f"Возникла ошибка при попытке записать твои данные в базу данных, "
                                        f"обратись к администратору")
            return

    # Забираем код типа счёта
    def get_acc_type_code(self, account_type_name):
        query = "select account_type_code from account_type where account_type_name = ?"
        result = self.db_conn.execute_query(query, params=(account_type_name,), fetchone=True)
        if result:
            return result[0]
        else:
            return None

    # Забираем тип счёта
    def get_acc_type(self, account_type_code):
        query = "select account_type from account_type where account_type_code = ?"
        result = self.db_conn.execute_query(query, params=(account_type_code,), fetchone=True)
        if result:
            return result[0]
        else:
            return None

    # Метод для возврата к странице счетов пользователя после сохранения
    def account_page_after_delay(self):
        logger.info(f"Открытие страницы счетов пользователя")
        self.new_page = MyAccountsPage(self.user_id)
        self.new_page.show()
        self.close()
        self.parent_window.close()

    # Метод для возврата к счетам пользователя
    def back(self):
        logger.info(f"Закрытие окна редактирования счетов пользователя")
        self.close()


# Окно для отображения истории счетов пользователя
class MyAccountHistoryWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Импортируем интерфейс
        self.ui = Ui_MyAccountsHistoryPage()
        self.ui.setupUi(self)

        # Для директивного обращения к странице
        self.user_id = user_id

        # Переменная для подсчёта записей по счетам для пользователя
        self.count = 0

        # Список для хранения всех записей по счетам пользователя
        self.user_accounts_history = []

        # Список для всех уникальных периодов по счетам пользователя
        self.users_periods = []

        # Список всех наименований для счетов пользователя
        self.user_accounts_names = []

        # Получение всех записей по счетам пользователя
        self.get_all_history()

        # Если у пользователя есть записи по счетам, то отображаем их
        if self.count >= 1:

            # Отображение дефолтных данных
            self.accounts_default_view()

        # Коннект кнопки для установки фильтра по периоду
        self.ui.set_period_button.clicked.connect(self.get_user_period)

        # Коннект кнопки для открытия страницы главного меню
        self.ui.main_page_button.clicked.connect(self.main_page_button)

        # Коннект кнопки для перехода к профилю пользователя
        self.ui.my_profile_button.clicked.connect(self.my_profile_button)

        # Коннект кнопки для перехода к счетам пользователя
        self.ui.my_accounts_button.clicked.connect(self.my_accounts_button)

        # Коннект кнопки для перехода к странице помощи
        self.ui.help_button.clicked.connect(self.help_page)

        # Коннект кнопки для выхода
        self.ui.exit_button.clicked.connect(self.confirm_exit)

    # Метод для получения всех записей по всем счетам пользователя и их наименования
    def get_all_history(self):
        logger.info(f"Выполняется получение всех данных по всем счетам пользователя за всё время ")
        try:
            get_query = ("select ab.balance_id, ab.user_id, ab.year, ab.month, ab.account_id, ab.account_type_code, "
                         "ab.amount, ab.created_at "
                         "from account_balance ab "
                         "join ("
                         "select user_id, year, month, account_id, account_type_code, amount, "
                         "max(created_at) AS max_created_at "
                         "from account_balance "
                         "where user_id = ? "
                         "group by user_id, year, month, account_id, account_type_code) subquery "
                         "on ab.user_id = subquery.user_id "
                         "and ab.year = subquery.year "
                         "and ab.month = subquery.month "
                         "and ab.account_id = subquery.account_id "
                         "and ab.account_type_code = subquery.account_type_code "
                         "and ab.created_at = subquery.max_created_at ")
            self.user_accounts_history = self.db_conn.execute_query(get_query, params=(self.user_id,), fetchall=True)

            # Проверка на наличие записей по счетам у пользователя
            if self.user_accounts_history:

                # Если есть записи по счетам, то запомним их количество, чтобы вызвать далее метод отображения
                # дефолтных периодов
                self.count += len(self.user_accounts_history)
                logger.info(f"Данные по всем счетам пользователя за всё время успешно получены")
            else:

                # Если у пользователя вообще нет записей, устанавливаем в фильтры текущие значения дат и уведомляем
                # пользователя о том, где он может внести записи по месяцам
                cur_default_date = datetime.now().strftime("%B,%Y")
                cur_default_month, cur_default_year = cur_default_date.split(',')
                self.ui.comboBox_month_start.setCurrentText(cur_default_month)
                self.ui.comboBox_year_start.setCurrentText(cur_default_year)
                self.ui.comboBox_month_end.setCurrentText(cur_default_month)
                self.ui.comboBox_year_end.setCurrentText(cur_default_year)
                self.ui.error_label.setText(f"Похоже, что у тебя ещё нет записей по счетам\n"
                                            f"Перейди на Главную страницу и нажми на Записать месяц")
                logger.warning(f"Данные по всем счетам пользователя за всё время не были получены: у пользователя нет "
                               f"таковых")
                return
        except Exception as syserr41:
            logger.error(f"Возникла ошибка при получении всех данных по всем счетам пользователя за всё время, "
                         f"детали: '{syserr41}'")
            return

        # Если у пользователя есть записи по счетам, притянем их наименования
        logger.info(f"Выполняется получение наименований для всех счетов пользователя")
        try:
            names_query = ("select user_id, account_id, account_name "
                           "from user_account where user_id = ?")
            self.user_accounts_names = self.db_conn.execute_query(names_query, params=(self.user_id,),fetchall=True)
            logger.info(f"Наименования по всем счетам пользователя успешно получены")
        except Exception as syserr43:
            logger.error(f"Возникла ошибка при получении всех наименований счетов пользователя, "
                         f"детали: '{syserr43}'")

    # Метод для отображения данных по счетам пользователя по дефолту
    def accounts_default_view(self):
        logger.info(f"Выполняется дефолтное заполнение данных по счетам пользователя")
        try:
            # Устанавливаем лэйаут для главного виджета
            main_layout = QHBoxLayout(self.ui.widget_for_tables)
            self.ui.widget_for_tables.setLayout(main_layout)

            # Порядок месяцев - вспомогательный словарь
            month_order = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                           "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

            # Получаем уникальные пары (Месяц, Год)
            unique_month_year = set((row[3], row[2]) for row in self.user_accounts_history)

            # Сортируем по году и месяцу
            unique_month_year = sorted(unique_month_year, key=lambda x: (x[1], month_order.index(x[0])))

            # Отберём уникальные значения годов
            unique_year = list(set(row[1] for row in unique_month_year))
            unique_year = sorted(unique_year, key=lambda x: x)

            # Список для элементов выпадающего меню с годами для фильтрации
            year_list = []

            # Заполняем годы для выпадающего меню QComboBox
            for year in unique_year:
                year_list.append(str(year))
            self.ui.comboBox_year_start.addItems(year_list)
            self.ui.comboBox_year_end.addItems(year_list)

            # Форматируем результат для сохранения - список из строк
            self.users_periods = [f"{month},{year}" for month, year in unique_month_year]

            # Список для определения дефолтных периодов для отображения - список из строк
            default_periods = []

            # Смотрим, по скольким уникальным периодам у пользователя есть записи
            # если у пользователя 3 или более периодов, то мы берём последние 3:
            if len(self.users_periods) >= 3:
                n = 3
                while n >= 1:
                    default_periods.append(self.users_periods[-n])
                    n -= 1

            # Если 2 периода, берём их
            elif len(self.users_periods) == 2:
                n = 2
                while n >= 1:
                    default_periods.append(self.users_periods[-n])
                    n -= 1

            # Если 1, то берём его
            elif len(self.users_periods) == 1:
                default_periods.append(self.users_periods[-1])

            logger.info(f"Выполнен поиск дефолтных периодов для отображения: '{default_periods}'")

            # Дополнительные параметры - QComboBox для дат фильтрации:
            # - начальные параметры периода - месяц и год - первая строка из default_periods
            month_start, year_start = default_periods[0].split(',')             # Распаковываем первую строку-дату
            self.ui.comboBox_month_start.setCurrentText(month_start)
            self.ui.comboBox_year_start.setCurrentText(year_start)

            # - конечные параметры периода - месяц и год - последняя строка из default_periods
            month_end, year_end = default_periods[-1].split(',')
            self.ui.comboBox_month_end.setCurrentText(month_end)
            self.ui.comboBox_year_end.setCurrentText(year_end)

            logger.info(f"Выполняется генерация таблиц для отображения истории счетов в количестве: "
                        f"'{len(default_periods)}'")

            # Идём генерировать таблицы
            self.generate_tables(default_periods)
            self.ui.error_label.setText(f"Отображение счетов успешно выполнено")
        except Exception as syserr13:
            logger.error(f"Возникла ошибка при поиске периодов, детали: '{syserr13}'")
            self.ui.error_label.setText(f"Возникла ошибка при попытке найти периоды, обратись к "
                                        f"администратору")
            return

    # Метод для получения пользовательского периода для отображения истории счетов
    def get_user_period(self):
        logger.info(f"Выполняется заполнение пользовательских периодов для отображении истории по счетам")
        # Забираем установленные периоды
        selected_start_month = self.ui.comboBox_month_start.currentText()
        selected_start_year = self.ui.comboBox_year_start.currentText()
        selected_end_month = self.ui.comboBox_month_end.currentText()
        selected_end_year = self.ui.comboBox_year_end.currentText()

        # Приводим к нужному виду
        selected_start_date = f"{selected_start_month},{selected_start_year}"
        selected_end_date = f"{selected_end_month},{selected_end_year}"

        # Преобразуем в дату
        selected_start_date = datetime.strptime(selected_start_date, "%B,%Y")
        selected_end_date = datetime.strptime(selected_end_date, "%B,%Y")

        # Список для пользовательских периодов - список из строк
        users_period = []

        # Заполняем список периодов
        cur_date = selected_start_date
        while cur_date <= selected_end_date:
            users_period.append(cur_date.strftime("%B,%Y"))
            cur_date += relativedelta(months=1)

        logger.info(f"Выполнено заполнение пользовательских периодов: '{users_period}'")
        # Передаём список в метод и переходим к генерации таблиц
        self.generate_tables(users_period)

        logger.info(f"Выполнено отображение данных по счетам по пользовательским периодам")
        self.ui.error_label.setText(f"Отображение счетов успешно выполнено")

    # Метод для генерации строк по счетам по периоду
    def generate_tables(self, list_of_periods):
        # Очистка виджета для заполнения новыми данными после применения фильтра
        main_layout = self.ui.widget_for_tables.layout()
        try:
            for i in reversed(range(main_layout.count())):
                widget_to_remove = main_layout.itemAt(i).widget()
                if widget_to_remove:
                    widget_to_remove.deleteLater()
            logger.info(f"Выполнена очистка форм для заполнения счетов пользователя")
        except Exception as syserr14:
            logger.error(f"Возникла ошибка при очистке форм: '{syserr14}'")
            self.ui.error_label.setText(f"Возникла непредвиденная ошибка при очистке форм, "
                                        f"обратись к администратору")
            return
        # Генерация таблиц:
        logger.info(f"Выполняется генерация таблиц для периодов")
        try:
            # Берём один период
            for period in list_of_periods:                                      # Пример общего вида - 'Сентябрь,2024'

                # Найдём для него предыдущий
                cur_period_date = datetime.strptime(period, '%B,%Y')
                prev_period_date = cur_period_date - relativedelta(months=1)
                prev_period = prev_period_date.strftime('%B,%Y')

                # Список для хранения итоговых записей по счетам для периодов
                cur_period_data21 = []
                cur_period_data31 = []
                cur_period_data41 = []
                cur_period_data51 = []
                cur_period_data91 = []
                cur_period_data11 = []
                cur_period_data4 = []
                prev_period_data21 = []
                prev_period_data31 = []
                prev_period_data41 = []
                prev_period_data51 = []
                prev_period_data91 = []
                prev_period_data11 = []
                prev_period_data4 = []

                # Список для размещения итоговых строк таблицы
                total_rows = []

                # Потом берём одну запись по счёту
                for account_statement in self.user_accounts_history:

                    # Дёрнем период для выбранной записи и приведём к общему виду
                    periods_month, periods_year = account_statement[3], account_statement[2]
                    statement_period = f"{periods_month},{periods_year}"

                    # Проверяем, входит ли запись в нужный нам период - текущий или предыдущий
                    # - текущий - если входит, то:
                    if statement_period == period:

                        # - тянем наименование счёта
                        for acc_name in self.user_accounts_names:
                            if acc_name[1] == account_statement[4]:
                                account_statement += (acc_name[2],)

                        # Если входит в текущий, проверяем какой код у счёта по записи и запоминаем
                        if account_statement[5] == 21:
                            cur_period_data21.append(account_statement)
                        elif account_statement[5] == 31:
                            cur_period_data31.append(account_statement)
                        elif account_statement[5] == 41:
                            cur_period_data41.append(account_statement)
                        elif account_statement[5] == 51:
                            cur_period_data51.append(account_statement)
                        elif account_statement[5] == 91:
                            cur_period_data91.append(account_statement)
                        elif account_statement[5] == 11:
                            cur_period_data11.append(account_statement)
                        elif account_statement[5] == 4:
                            cur_period_data4.append(account_statement)

                    # - предыдущий
                    elif statement_period == prev_period:

                        # - тянем наименование счёта
                        for acc_name in self.user_accounts_names:
                            if acc_name[1] == account_statement[4]:
                                account_statement += (acc_name[2],)

                        # Если входит в предыдущий, делаем всё то же самое
                        if account_statement[5] == 21:
                            prev_period_data21.append(account_statement)
                        elif account_statement[5] == 31:
                            prev_period_data31.append(account_statement)
                        elif account_statement[5] == 41:
                            prev_period_data41.append(account_statement)
                        elif account_statement[5] == 51:
                            prev_period_data51.append(account_statement)
                        elif account_statement[5] == 91:
                            prev_period_data91.append(account_statement)
                        elif account_statement[5] == 11:
                            prev_period_data11.append(account_statement)
                        elif account_statement[5] == 4:
                            prev_period_data4.append(account_statement)

                # Отсортируем счета по наименования перед вставкой
                # устанавливаем английскую локаль, чтобы сортировать сначала английский алфавит
                locale.setlocale(locale.LC_COLLATE, 'en_US.UTF-8')

                # Сортируем каждый список
                cur_period_data21 = sorted(cur_period_data21, key=lambda x: locale.strxfrm(x[-1]))
                cur_period_data31 = sorted(cur_period_data31, key=lambda x: locale.strxfrm(x[-1]))
                cur_period_data41 = sorted(cur_period_data41, key=lambda x: locale.strxfrm(x[-1]))
                cur_period_data51 = sorted(cur_period_data51, key=lambda x: locale.strxfrm(x[-1]))
                cur_period_data91 = sorted(cur_period_data91, key=lambda x: locale.strxfrm(x[-1]))
                cur_period_data11 = sorted(cur_period_data11, key=lambda x: locale.strxfrm(x[-1]))
                cur_period_data4 = sorted(cur_period_data4, key=lambda x: locale.strxfrm(x[-1]))
                prev_period_data21 = sorted(prev_period_data21, key=lambda x: locale.strxfrm(x[-1]))
                prev_period_data31 = sorted(prev_period_data31, key=lambda x: locale.strxfrm(x[-1]))
                prev_period_data41 = sorted(prev_period_data41, key=lambda x: locale.strxfrm(x[-1]))
                prev_period_data51 = sorted(prev_period_data51, key=lambda x: locale.strxfrm(x[-1]))
                prev_period_data91 = sorted(prev_period_data91, key=lambda x: locale.strxfrm(x[-1]))
                prev_period_data11 = sorted(prev_period_data11, key=lambda x: locale.strxfrm(x[-1]))
                prev_period_data4 = sorted(prev_period_data4, key=lambda x: locale.strxfrm(x[-1]))

                # Возвращаем локаль
                locale.setlocale(locale.LC_TIME, "Russian_Russia.1251")

                # Предварительно формируем строки для отображения счетов пользователя по разделам
                # - записи по счетам для первого раздела - записи по счетам с типом кода 21
                first_section_data = []
                # - для счёта строк
                a = 1

                # Берём первую запись по счёту с кодом типа 21
                for cur_row_a in cur_period_data21:

                    # Для хранения данных по текущей итерации
                    # - сначала запишем наименование счёта
                    current_row_a = [f"1.{a}. {cur_row_a[-1]}"]

                    # Инициализируем сумму на случай, если за прошлый период по счёту не будет записи
                    result_amount_a = '0.00'

                    # Берём теперь запись из предыдущего периода по счетам с кодом типа 21
                    for prev_row_a in prev_period_data21:

                        # Найдём запись для того же самого счёта - если она есть, то запишем её
                        # если таковой нет, то запишем нули
                        if prev_row_a[4] == cur_row_a[4]:
                            result_amount_a = f"{prev_row_a[6]:.2f}"
                            break

                    # Добавляем сумму за прошлый период
                    current_row_a.append(f"{result_amount_a}")

                    # И сумму за текущий период
                    current_row_a.append(f"{cur_row_a[6]:.2f}")

                    # Форматируем список в кортеж и добавляем в итоговый список
                    first_section_data.append(tuple(current_row_a))

                    # Обновляем переменную для построчной записи
                    a += 1

                # Далее проделываем всё то же самое и для других счетов
                # - записи по счетам для второго раздела - записи по счетам с типом кода 31, 41, 51 и 91
                second_section_data31 = []
                # - для счёта строк
                b = 1
                # - счёт 31
                for cur_row_b in cur_period_data31:
                    current_row_b = [f"2.{b}. {cur_row_b[-1]}"]
                    result_amount_b = '0.00'
                    for prev_row_b in prev_period_data31:
                        if prev_row_b[4] == cur_row_b[4]:
                            result_amount_b = f"{prev_row_b[6]:.2f}"
                            break
                    current_row_b.append(f"{result_amount_b}")
                    current_row_b.append(f"{cur_row_b[6]:.2f}")
                    second_section_data31.append(tuple(current_row_b))
                    b += 1

                # - счёт 41
                second_section_data41 = []
                for cur_row_b in cur_period_data41:
                    current_row_b = [f"2.{b}. {cur_row_b[-1]}"]
                    result_amount_b = '0.00'
                    for prev_row_b in prev_period_data41:
                        if prev_row_b[4] == cur_row_b[4]:
                            result_amount_b = f"{prev_row_b[6]:.2f}"
                            break
                    current_row_b.append(f"{result_amount_b}")
                    current_row_b.append(f"{cur_row_b[6]:.2f}")
                    second_section_data41.append(tuple(current_row_b))
                    b += 1

                # - счёт 51
                second_section_data51 =[]
                for cur_row_b in cur_period_data51:
                    current_row_b = [f"2.{b}. {cur_row_b[-1]}"]
                    result_amount_b = '0.00'
                    for prev_row_b in prev_period_data51:
                        if prev_row_b[4] == cur_row_b[4]:
                            result_amount_b = f"{prev_row_b[6]:.2f}"
                            break
                    current_row_b.append(f"{result_amount_b}")
                    current_row_b.append(f"{cur_row_b[6]:.2f}")
                    second_section_data51.append(tuple(current_row_b))
                    b += 1

                # - счёт 91
                second_section_data91 = []
                for cur_row_b in cur_period_data91:
                    current_row_b = [f"2.{b}. {cur_row_b[-1]}"]
                    result_amount_b = '0.00'
                    for prev_row_b in prev_period_data91:
                        if prev_row_b[4] == cur_row_b[4]:
                            result_amount_b = f"{prev_row_b[6]:.2f}"
                            break
                    current_row_b.append(f"{result_amount_b}")
                    current_row_b.append(f"{cur_row_b[6]:.2f}")
                    second_section_data91.append(tuple(current_row_b))
                    b += 1

                # - записи по счетам для третьего раздела - записи по счетам с типом кода 11
                third_section_data = []
                # - для счёта строк
                c = 1
                for cur_row_c in cur_period_data11:
                    current_row_c = [f"3.{c}. {cur_row_c[-1]}"]
                    result_amount_c = '0.00'
                    for prev_row_c in prev_period_data11:
                        if prev_row_c[4] == cur_row_c[4]:
                            result_amount_c = f"{prev_row_c[6]:.2f}"
                            break
                    current_row_c.append(f"{result_amount_c}")
                    current_row_c.append(f"{cur_row_c[6]:.2f}")
                    third_section_data.append(tuple(current_row_c))
                    c += 1

                # - записи по счетам для четвёртого раздела - записи по счетам с типом кода 4
                fourth_section_data = []
                # - для счёта строк
                d = 1
                for cur_row_d in cur_period_data4:
                    current_row_d = [f"4.{d}. {cur_row_d[-1]}"]
                    result_amount_d = '0.00'
                    for prev_row_d in prev_period_data4:
                        if prev_row_d[4] == cur_row_d[4]:
                            result_amount_d = f"{prev_row_d[6]:.2f}"
                            break
                    current_row_d.append(f"{result_amount_d}")
                    current_row_d.append(f"{cur_row_d[6]:.2f}")
                    fourth_section_data.append(tuple(current_row_d))
                    d += 1

                # Далее переходим к формированию таблицы, задаём контейнер для периода
                period_widget = QtWidgets.QWidget()
                period_layout = QVBoxLayout(period_widget)
                period_widget.setLayout(period_layout)

                # Для периода создаём таблицу с тремя колонками
                period_table = QTableWidget()
                period_table.setColumnCount(3)
                period_table.setColumnWidth(0, 240)
                period_table.setColumnWidth(1, 110)
                period_table.setColumnWidth(2, 110)

                # Устанавливаем заголовки колонок
                period_table.setHorizontalHeaderLabels([
                    'Наименование раздела',
                    'Сальдо \nначальное, \nруб.',
                    'Сальдо \nконечное, \nруб.'
                ])

                # Отключаем нумерацию строк
                period_table.verticalHeader().setVisible(False)

                # Отключаем кликабельность ячеек
                period_table.setSelectionMode(QAbstractItemView.NoSelection)

                # Формируем статичные строки
                # - наименования разделов
                first_section = ('1. Счета', '', '')                             # Коды: 21
                second_section = ('2. Сбережения', '', '')                       # Коды: 31, 41, 51, 91
                third_section = ('3. Валюта', '', '')                            # Коды: 11
                fourth_section = ('4. Обязательства', '', '')                    # Коды: 4
                # - пустая строка для перехода между разделами
                empty_row = ('', '', '')

                # Дополнительные списки для сумм для счёта итогов
                cur_sum_first_section = 0                    # Суммы по текущему состоянию счёта первого раздела
                cur_sum_second_section31 = 0                 # Суммы по текущему состоянию счёта второго раздела (31)
                cur_sum_second_section41 = 0                 # Суммы по текущему состоянию счёта второго раздела (41)
                cur_sum_second_section51 = 0                 # Суммы по текущему состоянию счёта второго раздела (51)
                cur_sum_second_section91 = 0                 # Суммы по текущему состоянию счёта второго раздела (91)
                cur_sum_third_section = 0                    # Суммы по текущему состоянию счёта третьего раздела
                cur_sum_fourth_section = 0                   # Суммы по текущему состоянию счёта четвёртого раздела
                prev_sum_first_section = 0                   # Суммы по предыдущему состоянию счёта первого раздела
                prev_sum_second_section31 = 0                # Суммы по предыдущему состоянию счёта второго раздела (31)
                prev_sum_second_section41 = 0                # Суммы по предыдущему состоянию счёта второго раздела (41)
                prev_sum_second_section51 = 0                # Суммы по предыдущему состоянию счёта второго раздела (51)
                prev_sum_second_section91 = 0                # Суммы по предыдущему состоянию счёта второго раздела (91)
                prev_sum_third_section = 0                   # Суммы по предыдущему состоянию счёта третьего раздела
                prev_sum_fourth_section = 0                  # Суммы по предыдущему состоянию счёта четвёртого раздела

                # Собираем кортежи в список - один кортеж = строка в таблице
                try:
                    # Статично задаём первую строку
                    total_rows.append(first_section)

                    # Проверяем, есть ли у пользователя записи в текущем периоде по первому разделу
                    if first_section_data:
                        # Если у пользователя есть данные по текущему периоду для первого раздела, то добавляем
                        # эти данные в список
                        for data in first_section_data:
                            total_rows.append(data)

                            # Прибавляем значение к сумме
                            cur_sum_first_section += round(float(data[2]), 2)
                            prev_sum_first_section += round(float(data[1]), 2)

                        # В конце добавляем пустую строчку для перехода между разделами
                        total_rows.append(empty_row)
                    elif not first_section_data:
                        # Если же данных нет, то просто переходим в другой раздел
                        total_rows.append(empty_row)

                    # Далее делаем то же самое для других разделов
                    # - записи по счетам по второму разделу
                    total_rows.append(second_section)
                    if second_section_data31:
                        for data in second_section_data31:
                            total_rows.append(data)
                            cur_sum_second_section31 += round(float(data[2]), 2)
                            prev_sum_second_section31 += round(float(data[1]), 2)

                    if second_section_data41:
                        for data in second_section_data41:
                            total_rows.append(data)
                            cur_sum_second_section41 += round(float(data[2]), 2)
                            prev_sum_second_section41 += round(float(data[1]), 2)

                    if second_section_data51:
                        for data in second_section_data51:
                            total_rows.append(data)
                            cur_sum_second_section51 += round(float(data[2]), 2)
                            prev_sum_second_section51 += round(float(data[1]), 2)

                    if second_section_data91:
                        for data in second_section_data91:
                            total_rows.append(data)
                            cur_sum_second_section91 += round(float(data[2]), 2)
                            prev_sum_second_section91 += round(float(data[1]), 2)

                    # После второго раздела добавляем пустую строку
                    total_rows.append(empty_row)

                    # - записи по счетам по третьему разделу
                    total_rows.append(third_section)
                    if third_section_data:
                        print(f"third_section_data: {third_section_data}")
                        for data in third_section_data:
                            print(f"data: {data}")
                            total_rows.append(data)
                            cur_sum_third_section += round(float(data[2]), 2)
                            prev_sum_third_section += round(float(data[1]), 2)
                        total_rows.append(empty_row)
                    elif not third_section_data:
                        total_rows.append(empty_row)

                    # - записи по счетам по четвёртому разделу
                    total_rows.append(fourth_section)
                    if fourth_section_data:
                        for data in fourth_section_data:
                            total_rows.append(data)
                            cur_sum_fourth_section += round(float(data[2]), 2)
                            prev_sum_fourth_section += round(float(data[1]), 2)
                        total_rows.append(empty_row)
                    elif not fourth_section_data:
                        total_rows.append(empty_row)
                except Exception as syserr55:
                    self.ui.error_label.setText(f"Возникла ошибке при сборе списка из кортежей, обратись к "
                                                f"администратору")
                    logger.error(f"Возникла ошибка при сборе списка из кортежей - строк для таблицы, "
                                 f"детали: '{syserr55}'")
                    return

                # Далее считаем итоговые суммы
                # - итого по рублёвым счетам
                prev_sum_total_all = (prev_sum_first_section + prev_sum_second_section31 + prev_sum_second_section41 +
                                      prev_sum_second_section51 + prev_sum_second_section91 + prev_sum_fourth_section)
                prev_sum_total_all = round(prev_sum_total_all, 2)
                prev_sum_total_all_cl = f"{prev_sum_total_all:.2f}"
                cur_sum_total_all = (cur_sum_first_section + cur_sum_second_section31 + cur_sum_second_section41 +
                                     cur_sum_second_section51 + cur_sum_second_section91 + cur_sum_fourth_section)
                cur_sum_total_all = round(cur_sum_total_all, 2)
                cur_sum_total_all_cl = f"{cur_sum_total_all:.2f}"
                total_all_rub = (f'     Итого по рублёвым счетам:',
                                 f'{prev_sum_total_all_cl}',
                                 f'{cur_sum_total_all_cl}')
                total_rows.append(total_all_rub)

                # - итого по валютным счетам
                prev_sum_total_val = prev_sum_third_section
                prev_sum_total_val = round(prev_sum_total_val, 2)
                prev_sum_total_val_cl = f"{prev_sum_total_val:.2f}"
                cur_sum_total_val = cur_sum_third_section
                cur_sum_total_val = round(cur_sum_total_val, 2)
                cur_sum_total_val_cl = f"{cur_sum_total_val:.2f}"
                total_all_val = (f'     Итого по валютным счетам:',
                                 f'{prev_sum_total_val_cl} $',
                                 f'{cur_sum_total_val_cl} $')
                total_rows.append(total_all_val)
                total_rows.append(empty_row)

                # - сумма расходов/доходов
                sum_dif_rub = (cur_sum_total_all - prev_sum_total_all)
                sum_dif_rub = round(sum_dif_rub, 2)
                sum_dif_rub_cl = f"{sum_dif_rub:.2f}"
                sum_dif_val = (cur_sum_total_val - prev_sum_total_val)
                sum_dif_val = round(sum_dif_val, 2)
                sum_dif_val_cl = f"{sum_dif_val:.2f}"
                total_sum_dif = (f'     Сумма расходов/доходов:',
                                 f'{sum_dif_rub_cl}',
                                 f'{sum_dif_val_cl} $')
                total_rows.append(total_sum_dif)

                # - в разбивке: по текущим счетам
                current_acc_dif = ((cur_sum_first_section + cur_sum_second_section31) -
                                   (prev_sum_first_section + prev_sum_second_section31))
                current_acc_dif = round(current_acc_dif, 2)
                current_acc_dif_cl = f"{current_acc_dif:.2f}"
                total_current_acc = (f'                    по текущим счетам:',
                                     f'{current_acc_dif_cl}',
                                     f'')
                total_rows.append(total_current_acc)

                # - в разбивке: по резервным счетам
                reserve_acc_dif = (cur_sum_second_section41 - prev_sum_second_section41)
                reserve_acc_dif = round(reserve_acc_dif, 2)
                reserve_acc_dif_cl = f"{reserve_acc_dif:.2f}"
                total_reserve_acc = (f'               по резервным счетам:',
                                     f'{reserve_acc_dif_cl}',
                                     f'')
                total_rows.append(total_reserve_acc)

                # - в разбивке: по накопительным счетам
                save_acc_dif = ((cur_sum_second_section51 + cur_sum_second_section91) -
                                (prev_sum_second_section51 + prev_sum_second_section91))
                save_acc_dif = round(save_acc_dif, 2)
                save_acc_dif_cl = f"{save_acc_dif:.2f}"
                total_save_acc = (f'       по накопительным счетам:',
                                  f'{save_acc_dif_cl}',
                                  f'')
                total_rows.append(total_save_acc)

                # Добавляем строки в таблицу
                for row_data in total_rows:
                    row_position = period_table.rowCount()
                    period_table.insertRow(row_position)
                    for col, value in enumerate(row_data):

                        # Кастомизация ячейки
                        item = QTableWidgetItem(value)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                        # Если ячейка для суммы - выравниваем по правому краю
                        if col in (1, 2):
                            item.setTextAlignment(Qt.AlignRight)

                        # Добавление ячейки в таблицу
                        period_table.setItem(row_position, col, item)

                # Наименование таблицы по периоду
                label_first_row = QLabel(f"{period}")
                label_first_row.setStyleSheet("font: 11pt \"Involve\";\n"
                                              "color: rgb(34, 34, 59);\n"
                                              "border-radius: 15px; \n"
                                              "background-color: rgb(255, 255, 255);")
                label_first_row.setAlignment(Qt.AlignCenter)
                label_first_row.setFixedWidth(490)

                # Помещаем заголовок и таблицу в layout
                period_layout.addWidget(label_first_row)
                period_layout.addWidget(period_table)

                # Затем добавляем итоговый контейнер с таблицей в основной лэйаут
                self.ui.widget_for_tables.layout().addWidget(period_widget)
            logger.info(f"Таблицы успешно сформированы")
        except Exception as syserr95:
            self.ui.error_label.setText(f"Произошла ошибка при генерации таблиц, обратись к администратору")
            logger.error(f"Возникла ошибка при генерации таблиц для пользователя, "
                         f"детали: '{syserr95}'")

    # Метод для открытия главной страницы
    def main_page_button(self):
        logger.info(f"Открытие главной страницы приложения")
        self.main_page = MainPage(self.user_id)
        self.main_page.show()
        self.close()

    # Метод для перехода к странице профиля пользователя
    def my_profile_button(self):
        logger.info(f"Открытие страницы профиля для пользователя: '{self.user_id}'")
        self.profile_page = MyProfilePage(self.user_id)
        self.profile_page.show()
        self.close()

    # Метод для перехода к странице счетов пользователя
    def my_accounts_button(self):
        logger.info(f"Открытие страницы счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountsPage(self.user_id)
        self.accounts_page.show()
        self.close()

    # Метод для перехода к странице помощи
    def help_page(self):
        logger.info(f"Открытие страницы помощи")
        self.help_page = HelpPageWindow(self.user_id)
        self.help_page.show()
        self.close()

    # Метод для выхода из приложения
    def confirm_exit(self):
        logger.info(f"Открытие страницы подтверждения выхода из приложения")
        self.exit_page = ConfirmPageWindow()
        self.exit_page.show()


# Окно помощи
class HelpPageWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Для работы с бд
        self.db_conn = DatabaseConn()

        # Для директивного обращения к странице
        self.user_id = user_id

        # Импортируем интерфейс
        self.ui = Ui_HelpPage()
        self.ui.setupUi(self)

        # Устанавливаем начальную страницу
        self.ui.stackedWidget.setCurrentIndex(0)

        # Коннект кнопок для открытия разделов помощи
        # - помощь по разделу Главная страница
        self.ui.main_page_help_button.clicked.connect(self.main_page_help)

        # - помощь по разделу Запись месяца
        self.ui.new_month_help_button.clicked.connect(self.new_month_help)

        # - помощь по разделу Мой профиль
        self.ui.my_profile_help_button.clicked.connect(self.my_profile_help)

        # - помощь по разделу Мои счета
        self.ui.my_accounts_help_button.clicked.connect(self.my_accounts_help)

        # - помощь по разделу Редактирование счетов
        self.ui.edit_account_help_button.clicked.connect(self.edit_account_help)

        # - помощь по разделу Добавление нового счёта
        self.ui.new_account_help_button.clicked.connect(self.new_account_help)

        # - помощь по разделу История счетов
        self.ui.accounts_history_help_button.clicked.connect(self.accounts_history_help)

        # Коннект кнопки для открытия страницы главного меню
        self.ui.main_page_button.clicked.connect(self.main_page_button)

        # Коннект кнопки для перехода к профилю пользователя
        self.ui.my_profile_button.clicked.connect(self.my_profile_button)

        # Коннект кнопки для перехода к счетам пользователя
        self.ui.my_accounts_button.clicked.connect(self.my_accounts_button)

        # Коннект кнопки для перехода к истории счетов
        self.ui.my_writings_button.clicked.connect(self.my_accounts_history)

        # Коннект кнопки для выхода
        self.ui.exit_button.clicked.connect(self.confirm_exit)

    # Метод для перехода к странице помощи раздела - Главная страница
    def main_page_help(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.back_button.clicked.connect(self.back_to_main_menu)

    # Метод для перехода к странице помощи раздела - Запись месяца
    def new_month_help(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.back_button_2.clicked.connect(self.back_to_main_menu)

    # Метод для перехода к странице помощи раздела - Мой профиль
    def my_profile_help(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.back_button_4.clicked.connect(self.back_to_main_menu)

    # Метод для перехода к странице помощи раздела - Мои счета
    def my_accounts_help(self):
        self.ui.stackedWidget.setCurrentIndex(4)
        self.ui.back_button_5.clicked.connect(self.back_to_main_menu)

    # Метод для перехода к странице помощи раздела - Редактирование счетов
    def edit_account_help(self):
        self.ui.stackedWidget.setCurrentIndex(5)
        self.ui.back_button_6.clicked.connect(self.back_to_main_menu)

    # Метод для перехода к странице помощи раздела - Добавление нового счёта
    def new_account_help(self):
        self.ui.stackedWidget.setCurrentIndex(6)
        self.ui.back_button_7.clicked.connect(self.back_to_main_menu)

    # Метод для перехода к странице помощи раздела - История счетов
    def accounts_history_help(self):
        self.ui.stackedWidget.setCurrentIndex(7)
        self.ui.back_button_8.clicked.connect(self.back_to_main_menu)

    # Метод для возврата в главное меню помощи
    def back_to_main_menu(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    # Метод для открытия главной страницы
    def main_page_button(self):
        logger.info(f"Открытие главной страницы приложения")
        self.main_page = MainPage(self.user_id)
        self.main_page.show()
        self.close()

    # Метод для перехода к странице профиля пользователя
    def my_profile_button(self):
        logger.info(f"Открытие страницы профиля для пользователя: '{self.user_id}'")
        self.profile_page = MyProfilePage(self.user_id)
        self.profile_page.show()
        self.close()

    # Метод для перехода к странице счетов пользователя
    def my_accounts_button(self):
        logger.info(f"Открытие страницы счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountsPage(self.user_id)
        self.accounts_page.show()
        self.close()

    # Метод для перехода к истории счетов пользователя
    def my_accounts_history(self):
        logger.info(f"Открытие страницы истории счетов для пользователя: '{self.user_id}'")
        self.accounts_page = MyAccountHistoryWindow(self.user_id)
        self.accounts_page.show()
        self.close()

    # Метод для выхода из приложения
    def confirm_exit(self):
        logger.info(f"Открытие страницы подтверждения выхода из приложения")
        self.second_page = ConfirmPageWindow()
        self.second_page.show()


# Окно для подтверждения выхода из приложения
class ConfirmPageWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Устанавливаем иконку для окна
        self.setWindowIcon(QIcon('content/app_icon.ico'))

        # Импортируем интерфейс
        self.ui = Ui_ConfirmPageWindow()
        self.ui.setupUi(self)

        # Коннект кнопки для подтверждения и отказа от выхода
        self.ui.yes_button.clicked.connect(self.exit_confirmed)
        self.ui.no_button.clicked.connect(self.exit_not_confirmed)

    def exit_confirmed(self):
        # Пользователь подтвердил выход
        logger.info(f"Пользователь подтвердил выход из приложения")
        QApplication.instance().quit()

    def exit_not_confirmed(self):
        # Пользователь не подтвердил выход
        logger.info(f"Пользователь не подтвердил выход из приложения")
        self.close()


# Метод для загрузки шрифта
def load_custom_font(font_reg_path: str, font_semi_bold_path: str, font_name_reg: str, font_name_semi_bold: str):
    try:
        logger.info(f"Выполняется попытка загрузки шрифта")

        # Сначала грузим regular
        font_reg_id = QFontDatabase.addApplicationFont(font_reg_path)
        if font_reg_id == -1:
            logger.error(f"Неуспешная попытка загрузки шрифта: '{font_name_reg}'")
            return

        # Получаем имя шрифта после загрузки
        font_reg_family = QFontDatabase.applicationFontFamilies(font_reg_id)[0]
        logger.info(f"Шрифт был успешно загружен: '{font_reg_family}'")

        # Потом догружаем semi-bold
        font_semi_bold_id = QFontDatabase.addApplicationFont(font_semi_bold_path)
        if font_semi_bold_id == -1:
            logger.error(f"Неуспешная попытка загрузки шрифта: '{font_name_semi_bold}'")
            return

        # Получаем имя шрифта после загрузки
        font_semi_bold_family = QFontDatabase.applicationFontFamilies(font_semi_bold_id)[0]
        logger.info(f"Шрифт был успешно загружен: '{font_semi_bold_family}'")

        return
    except Exception as syserr65:
        logger.error(f"Возникла ошибка при попытке загрузки шрифта: '{syserr65}'")
        return


if __name__ == "__main__":
    logger.info(f"Запуск приложения Budget Keeper")

    # Инициализация приложения
    app = QApplication(sys.argv)

    # Работа со шрифтами
    logger.info(f"Проверка на наличие шрифта в системе пользователя")
    if 'Involve' in QFontDatabase().families():
        # Если шрифт уже есть в системе, то переходим к запуску приложения
        logger.info(f"Шрифт 'Involve' уже присутствует в системе, загрузка не требуется")
    else:
        # Если шрифта нет, то загружаем
        logger.info(f"Шрифт 'Involve' не был найден в системе")

        # Путь к шрифту
        font_reg_path = os.path.join(os.path.dirname(__file__), "content/fonts", "Involve-Regular.ttf")
        font_semi_bold_path = os.path.join(os.path.dirname(__file__), "content/fonts", "Involve-SemiBold.ttf")

        # Попытка установки regular шрифта
        load_custom_font(font_reg_path, font_semi_bold_path,"Involve", "Involve SemiBold")

    # Открытие главного меню
    window = MainMenu()
    window.show()

    try:
        sys.exit(app.exec_())
    except Exception as syserr:
        logger.error(f"Возникла ошибка во время работы приложения: '{syserr}'")
    finally:
        logger.info(f"Завершение работы приложения Budget Keeper")
