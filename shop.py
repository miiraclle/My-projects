# -*- coding: utf-8 -*-

import tkinter as tk
import psycopg2
import tkinter.messagebox as msg
import pandas as pd
from decimal import Decimal
import tkinter.simpledialog



class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Текстовое поле для ввода названия таблицы
        self.text1 = tk.Label(text="Выберите таблицу для ввода данных")
        self.text1.pack()

        # Кнопки для выбора таблиц
        self.btn_booking = tk.Button(self, text="Внести данные в таблицу booking",
                                     command=lambda: self.start_window('booking'))
        self.btn_customers = tk.Button(self, text="Внести данные в таблицу customers",
                                       command=lambda: self.start_window('customers'))
        self.btn_cart_items = tk.Button(self, text="Внести данные в таблицу cart_items",
                                        command=lambda: self.start_window('cart_items'))
        self.btn_computers = tk.Button(self, text="Внести данные в таблицу computers",
                                       command=lambda: self.start_window('computers'))

        # Кнопки для отображения данных
        self.btn_booking.pack(padx=50, pady=2)
        self.btn_customers.pack(padx=50, pady=2)
        self.btn_cart_items.pack(padx=50, pady=2)
        self.btn_computers.pack(padx=50, pady=2)

        # Кнопка выхода
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.btn_exit = tk.Button(self, text="Выйти из программы", command=self.on_exit)
        self.btn_exit.pack(padx=50, pady=2)

    def on_exit(self):
        """Подтверждение выхода из программы."""
        if msg.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.quit()

    def postgresconnection(self):
        """Подключение к базе данных PostgreSQL."""
        self.connection = psycopg2.connect(
            host='localhost',
            user='postgres',
            password='adminadmin',
            port='5432',
            dbname='shop',
            options='-c client_encoding=UTF8'
        )
        return

    def start_window(self, table_name):
        """Окно для работы с таблицей."""
        self.new_window = tk.Tk()
        self.new_window.title(f"Работа с таблицей {table_name}")
        self.new_window.resizable()
        self.canvas = tk.Canvas(self.new_window)
        self.canvas.pack()

        # Поля для ввода данных
        self.entries = {}
        self.labels = {}
        columns = self.get_columns(table_name)

        for column in columns:
            self.labels[column] = tk.Label(self.canvas, text=f"Введите {column}")
            self.labels[column].pack(expand=True, padx=10, pady=10)
            self.entries[column] = tk.Entry(self.canvas, textvariable=tk.StringVar())
            self.entries[column].pack()

        # Кнопки для различных операций
        tk.Button(self.canvas, text="Внести данные", command=lambda: self.insert_in_table(table_name)).pack(pady=2)
        tk.Button(self.canvas, text="Показать все записи", command=lambda: self.show_all_records(table_name)).pack(pady=2)
        tk.Button(self.canvas, text="Удалить запись", command=lambda: self.delete_record(table_name)).pack(pady=2)
        tk.Button(self.canvas, text="Изменить запись", command=lambda: self.update_record(table_name)).pack(pady=2)
        tk.Button(self.canvas, text="Поиск по названию", command=lambda: self.search_record(table_name)).pack(pady=2)
        tk.Button(self.canvas, text="Закрыть окно", command=self.new_window.destroy).pack(pady=2)

    def get_columns(self, table_name):
        """Получение списка колонок для таблицы."""
        columns = {
            "booking": ["order_number", "customer_email", "delivery_number", "payment_type", "payment_status",
                        "total_cost", "status", "order_date"],
            "customers": ["customer_email", "last_name", "first_name", "phone_number"],
            "cart_items": ["cart_item_id", "order_number", "component_number", "computer_id", "quantity", "item_cost"],
            "computers": ["computer_id", "configuration_position", "name", "purpose"]
        }
        return columns.get(table_name, [])

    def insert_in_table(self, table_name):
        """Внесение данных в таблицу."""
        self.postgresconnection()
        columns = self.get_columns(table_name)
        values = []

        # Преобразуем значение для total_cost в Decimal
        for column in columns:
            value = self.entries[column].get()
            if column == "total_cost":  # Для столбца `total_cost` переводим в Decimal
                try:
                    value = Decimal(value)  # Преобразуем в Decimal для типа money
                except:
                    msg.showerror("Ошибка", "Некорректное значение для total_cost. Введите число.")
                    return
            values.append(value)

        values = tuple(values)  # Преобразуем список значений в кортеж

        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, values)
            self.connection.commit()
            msg.showinfo("Успех", f"Данные успешно внесены в таблицу {table_name}")
            self.connection.close()
            self.new_window.destroy()

    def show_all_records(self, table_name):
        """Показать все записи из выбранной таблицы."""
        self.postgresconnection()

        # Создаем SQL запрос для получения всех данных из таблицы
        sql = f"SELECT * FROM {table_name}"

        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            records = cursor.fetchall()

            if records:
                # Создаем новое окно для отображения результатов
                result_window = tk.Toplevel(self.new_window)
                result_window.title(f"Все записи из таблицы {table_name}")

                # Отображаем результаты
                for record in records:
                    record_text = " | ".join([str(val) for val in record])
                    label = tk.Label(result_window, text=record_text)
                    label.pack(pady=2)
            else:
                msg.showinfo("Результаты", "Записи не найдены.")

        self.connection.close()

    def update_record(self, table_name):
        """Изменение данных записи по идентификатору."""
        from decimal import Decimal
        # Получение идентификатора записи
        id_column = self.get_columns(table_name)[0]
        record_id = self.entries[id_column].get()

        if record_id:
            self.postgresconnection()
            columns = self.get_columns(table_name)

            values = []
            for col in columns[1:]:  # Пропускаем ID столбец
                value = self.entries[col].get()

                # Проверка поля payment_type на допустимые значения
                if col == "payment_type":
                    if value not in ["cash", "card"]:  # Замените на фактические допустимые значения
                        msg.showerror("Ошибка",
                                      "Некорректное значение для payment_type. Допустимые значения: cash, card.")
                        return

                # Преобразуем total_cost в Decimal
                if col == "total_cost":
                    try:
                        value = Decimal(value)
                    except:
                        msg.showerror("Ошибка", "Некорректное значение для total_cost. Введите число.")
                        return
                values.append(value)

            # Добавляем идентификатор записи в конец списка значений
            values.append(record_id)

            set_clause = ', '.join([f"{col} = %s" for col in columns[1:]])  # Пропускаем ID столбец
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"

            with self.connection.cursor() as cursor:
                cursor.execute(sql, values)
                self.connection.commit()
                msg.showinfo("Успех", "Запись успешно обновлена.")
            self.connection.close()
        else:
            msg.showerror("Ошибка", f"Введите ID ({id_column}) для обновления записи.")

    def search_record(self, table_name):
        """Поиск записи по названию (или другому полю)."""
        self.postgresconnection()

        # Для поиска будем использовать одно поле из таблицы
        if table_name == "booking":
            column_to_search = "customer_email"
        elif table_name == "customers":
            column_to_search = "customer_email"
        elif table_name == "cart_items":
            column_to_search = "cart_item_id"
        elif table_name == "computers":
            column_to_search = "name"
        else:
            msg.showerror("Ошибка", f"Поиск для таблицы {table_name} не поддерживается.")
            return

        # Окно для ввода значения для поиска
        search_value = tk.simpledialog.askstring(f"Поиск в таблице {table_name}",
                                                 f"Введите {column_to_search} для поиска:")
        if not search_value:
            msg.showerror("Ошибка", "Введите значение для поиска.")
            return

        # Выполнение SQL запроса
        sql = f"SELECT * FROM {table_name} WHERE {column_to_search} = %s"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (search_value,))
            records = cursor.fetchall()

            if records:
                result_window = tk.Toplevel(self.new_window)
                result_window.title(f"Результаты поиска в {table_name}")

                # Отображаем результаты поиска
                for i, record in enumerate(records):
                    record_text = " | ".join([str(val) for val in record])
                    label = tk.Label(result_window, text=record_text)
                    label.pack(pady=2)
            else:
                msg.showinfo("Результаты поиска", "Записи не найдены.")

        self.connection.close()

    def delete_record(self, table_name):
        """Удалить запись из таблицы по идентификатору."""
        self.postgresconnection()

        # Определяем столбец для идентификации записи, например, ID или уникальное поле
        if table_name == "booking":
            id_column = "order_number"
        elif table_name == "customers":
            id_column = "customer_email"
        elif table_name == "cart_items":
            id_column = "cart_item_id"
        elif table_name == "computers":
            id_column = "computer_id"
        else:
            msg.showerror("Ошибка", f"Удаление записей для таблицы {table_name} не поддерживается.")
            return

        # Окно для ввода ID записи для удаления
        record_id = tk.simpledialog.askstring(f"Удаление из таблицы {table_name}",
                                              f"Введите {id_column} для удаления записи:")

        if not record_id:
            msg.showerror("Ошибка", f"Введите {id_column} для удаления записи.")
            return

        # SQL запрос на удаление записи
        sql = f"DELETE FROM {table_name} WHERE {id_column} = %s"

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, (record_id,))
                self.connection.commit()

                # Проверка на количество затронутых строк
                if cursor.rowcount > 0:
                    msg.showinfo("Успех", f"Запись с {id_column} = {record_id} успешно удалена.")
                else:
                    msg.showinfo("Ошибка", f"Запись с {id_column} = {record_id} не найдена.")
        except Exception as e:
            msg.showerror("Ошибка", f"Произошла ошибка при удалении записи: {str(e)}")
        finally:
            self.connection.close()


# Запуск приложения
if __name__ == "__main__":
    app = App()
    app.title("Магазин техники")
    app.mainloop()
