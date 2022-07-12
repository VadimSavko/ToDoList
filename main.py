# ToDo list organizer.

from sys import path
path.append('..\\packages')

from os import strerror
from unicodedata import name
import sqlite3 as sql
from prettytable import PrettyTable

# Константы.
TASK_NAME_MIN_LENGTH = 7  # Минимальная длина названия задания.
TASK_PRIORITY_MIN = 1  # Минимальное значения приоритета задания.
TASK_PRIORITY_MAX = 100  # Максимальное значения приоритета задания.
TASK_EXIT_CONDITION = 'stop'  # Слово-условие для выхода из программы.
TASK_DISPLAY_CONDITION = 'show'  # Слово-условие для вывода списка заданий на экран.
TASK_FIND_CONDITION = 'find'  # Слово-условие для поиска задания в списке и вывода его на экран.
TASK_FILE_CONDITION = 'file'  # Слово-условие для сохранения списка заданий в файл.
TASK_CHANGE_CONDITION = 'change'  # Слово-условие для редактирования задания из списка.
TASK_DELETE_CONDITION = 'delete'  # Слово-условие для удаления задания из списка.
TASK_FILE_NAME = 'task.txt'  # Имя файла для сохранения заданий.


# Исключения для класса "Task".
class TaskError(Exception):
    def __init__(self, name, message):
        Exception.__init__(self, message)
        self.name = name


class NotFoundTaskError(TaskError):
    def __init__(self, name):
        TaskError.__init__(self, name, 'Task not found')


class FileNotWriteTaskError(TaskError):
    def __init__(self, name):
        TaskError.__init__(self, name, 'File not writen')
        

# Класс "Task"
class Task():   
    def __init__(self):        
        self.conn = sql.connect('todo.db')
        self.cur = self.conn.cursor()
        self.create_db_table()
        self.task_table = PrettyTable()        

    def close_db_connection(self):
        self.conn.close()

    def create_db_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY,
            task_name TEXT NOT NULL,
            task_priority INTEGER NOT NULL
            );''')

    # Проверка имени задания.
    @staticmethod
    def check_task_name(name):
        return len(name) >= TASK_NAME_MIN_LENGTH
        
    # Проверка приоритета задания.
    @staticmethod
    def check_task_priority(priority):
        if priority.isdigit():
            return (int(priority) >= TASK_PRIORITY_MIN) and (int(priority) <= TASK_PRIORITY_MAX)
        else:
            return False
    
    # Вывод требований к формату задания на экран.
    @staticmethod
    def show_task_condition():
        task_name = '\nTask name must be more than {} characters.'.format(TASK_NAME_MIN_LENGTH)
        task_priority = '\nTask priority must be a number between {} and {}.'.format(TASK_PRIORITY_MIN, TASK_PRIORITY_MAX)
        task_exit = '\nEnter "{}" to exit.'.format(TASK_EXIT_CONDITION)
        task_display = '\nEnter "{}" to display the task list.'.format(TASK_DISPLAY_CONDITION)
        task_find = '\nEnter "{}" to find the task in list.'.format(TASK_FIND_CONDITION)
        task_file = '\nEnter "{}" to save the task list to file.'.format(TASK_FILE_CONDITION)
        task_change = '\nEnter "{}" to change the task in list.'.format(TASK_CHANGE_CONDITION)
        delete_change = '\nEnter "{}" to delete the task in list.'.format(TASK_DELETE_CONDITION)
        return task_name + task_priority + task_exit + task_display + task_find + task_file + task_change + delete_change
    
    # Добавления задания в список.
    def add_task(self, name, priority):
        self.cur.execute('INSERT INTO tasks (task_name, task_priority) VALUES (?, ?)', (name, priority))
        self.conn.commit

    # Перезапись задания в списке.
    def update_task(self, id, name, priority):
        #if id in self.__task_list:            
        self.cur.execute('UPDATE tasks SET task_name = ?, task_priority = ? where task_id = ?;',
        (name, priority, id))
        return True

    # Вывод списка заданий на экран.
    def show_task(self):        
        self.task_table.field_names = ["ID", "Name", "Priority"]
        self.cur.execute('SELECT task_id, task_name, task_priority FROM tasks')
        mytable = PrettyTable.from_db_cursor(self.cur)
        print(mytable)
    
    # Редактирование задания из списка.
    def change_task(self):
        id = input('\nEnter task ID : ')

        if id in self.__task_list:
            while True:
                name = input('\nEnter new name or empty string : ')
                if name == '': 
                    name = self.__task_list[id][0]
                    break
                else:
                    if Task.check_task_name(name):
                        break
                            
            while True:
                priority = input('\nEnter new priority or empty string : ')
                if priority == '': 
                    priority = self.__task_list[id][1]                   
                    break
                else:
                    if Task.check_task_priority(priority):
                        break
            
            if self.update_task(id, name, priority):
                print('Task succesfully changed.')        
        else:
            raise NotFoundTaskError(id)

    # Редактирование задания из списка.
    def delete_task(self):
        id = input('\nEnter task ID : ')
        if id in self.__task_list:
            self.cur.execute('DELETE FROM tasks WHERE task_id = ?;', (id,))
            self.conn.commit

    # Поиск задания в списке.
    def find_task(self):        
        name = input('\nEnter task name to find it and show : ')

        found_task = ''        
        rows = self.cur.execute('''SELECT task_id, task_name, task_priority FROM tasks;''')
        for row in rows:
            if row[1] == name:
                found_task = row
        
        if found_task != '':
            print(found_task)            
        else:
            raise NotFoundTaskError(name)
                    
    # Запись списка заданий в файл.
    def write_to_file(self):
        s = ''            
        for key, value in self.__task_list.items():
            s += '{} {} {}'.format(key, value[0], value[1]) + "\n"
        
        try:
            f = open(TASK_FILE_NAME, 'wt')    
            f.write(s)               
            f.close
        except IOError:
            raise FileNotWriteTaskError(TASK_FILE_NAME)            
        else:
            print('File succesfully writen.')
    
    # Вывод сообщения и получение текста запроса.
    def get_input(self, message, check_message):        
        while True:
            input_text = input(message)

            if input_text == TASK_EXIT_CONDITION:  # Проверка выхода из программы.
                self.close_db_connection
                exit()
            elif input_text == TASK_DISPLAY_CONDITION:  # Проверка на вывод списка заданий на экран.
                self.show_task()
                return ''
            elif input_text == TASK_FIND_CONDITION:  # Проверка на поиск задания в списке.
                self.find_task()
                return ''
            elif input_text == TASK_CHANGE_CONDITION:  # Проверка на редактирование задания из списка.
                self.change_task()
                return ''
            elif input_text == TASK_DELETE_CONDITION:  # Проверка на удаление задания из списка.
                self.delete_task()
                return ''
            elif input_text == TASK_FILE_CONDITION:  # Проверка на сохранение списка заданий в файл.
                self.write_to_file()
                return ''
            elif check_message(input_text):  # Проверка полученного атрибута задания на валидность.
                return input_text
            

# Основная программа.
task = Task()

print(task.show_task_condition())

while True:
    try:
        # Запрос названия задания.
        name = task.get_input('\nEnter task name : ', Task.check_task_name)
        if name == '':
            continue

        # Запрос приоритета задания.
        priority = task.get_input('Enter task priority : ', Task.check_task_priority)
        if priority == '':
            continue
    
        # Добавление задания в список.
        task.add_task(name, priority)

    except NotFoundTaskError as e:
            print(e, ':', e.name)
    except FileNotWriteTaskError as e:
            print(e, ':', e.name)
