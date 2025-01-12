import sqlite3

# Создаём подключение к базе данных
connection = sqlite3.connect("budget_keeper.db")

cursor = connection.cursor()

# Создание таблиц
# user_data - данные пользователей
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    current_income REAL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# account_type - справочник типов счетов
cursor.execute("""
CREATE TABLE IF NOT EXISTS account_type (
    account_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_type TEXT NOT NULL,
    account_type_name TEXT NOT NULL,
    account_type_code INTEGER NOT NULL UNIQUE,
    description TEXT
);
""")

# user_account - счета пользователя
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_account (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_name TEXT NOT NULL,
    account_type_name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    account_type_code INTEGER NOT NULL,
    create_date TIMESTAMP,
    active_flag INTEGER NOT NULL DEFAULT 1,
    deactivate_date TIMESTAMP,
    update_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_data(user_id) ON DELETE CASCADE,
    FOREIGN KEY (account_type_code) REFERENCES account_type(account_type_code) ON DELETE CASCADE
);
""")

# account_balance - суммы по счетам пользователей на определенный момент времени
cursor.execute("""
CREATE TABLE IF NOT EXISTS account_balance (
    balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month TEXT NOT NULL,
    account_id INTEGER NOT NULL,
    account_type_code INTEGER NOT NULL,
    amount REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_data(user_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES user_account(account_id) ON DELETE CASCADE,
    FOREIGN KEY (account_type_code) REFERENCES account_type(account_type_code) ON DELETE CASCADE
);
""")

# Заполнение справочника счетов
cursor.execute("""
INSERT INTO account_type (account_type, account_type_name, account_type_code, description)
VALUES 
    ('Дебетовый', 'Карточный счёт', 21, 'Счёт, который используется для внесения информации по карточным продуктам 
    (только дебетовым)'),
    ('Дебетовый', 'Текущий счёт', 31, 'Счёт, на котором хранятся денежные средства в текущем пользовании'),
    ('Дебетовый', 'Резервный счёт', 41, 'Счёт, который используется для хранения резервных денежных средств'),
    ('Дебетовый', 'Накопительный счёт', 51, 'Счёт для хранения денежных средств с целью накопления на что-либо'),
    ('Дебетовый', 'Вклад', 91, 'Счёт для отражения денежных средств, находящихся на данный момент на вкладе'),
    ('Дебетовый', 'Валютный счёт', 11, 'Счёт для отражения денежных средств, находящихся в валюте'),
    ('Кредитовый', 'Займ', 04, 'Счёт, отражающий денежные средства, выданные кому-либо в долг');
""")

# Сохраняем изменения и закрываем подключение
connection.commit()
connection.close()

print("База данных и таблицы успешно созданы.")
