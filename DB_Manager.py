import sqlite3
import os
red       = "\033[91m"
green     = "\033[92m"
white     = "\033[97m"
yellow    = "\033[33m"
SkyB      = "\033[36m"
blue      = "\033[34m"
purple    = "\033[35m"
gray      = "\033[90m"
C14       = "\033[38;5;159m"
reset     = "\033[0m"
cursor = None
conn = None

def ex(e):
	return e == '..'
	
def create_db():
	global conn, cursor
	while True:
		db_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter the name of the new database with (.db): {reset}')
		if ex(db_n): 
			break
		if os.path.exists(db_n):
			print(f'{red}There is a database with this name, try again!{reset}')
		else:
			conn = sqlite3.connect(db_n)
			cursor = conn.cursor()
			print(f'{green}Database created successfully!{reset}')
			com = input(f'{yellow}Do you want to manage it ? (y/n) : {reset}')
			if com == 'n':
				conn.close()
				break
			elif com == 'y':
				edit()

def create_t():
	global conn, cursor
	while True:
		t_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter table name to create : {reset}')
		if t_n == '..':
			break
		c_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter columns name, text with TEXT, number with INTEGER, like that (name TEXT, age INTEGER) :\n {reset}')
		if c_n == '..':
			break
		cursor.execute(f"CREATE TABLE IF NOT EXISTS {t_n} (id INTEGER PRIMARY KEY AUTOINCREMENT, {c_n});")
		conn.commit()
		print(f"{green}Table created successfully!{reset}")

def show_tables():
	global conn, cursor
	try:
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
		tables = cursor.fetchall()
		if not tables:
			print(f"{red}No tables found in the database!{reset}")
			return
		for i, table in enumerate(tables, start=1):
			table_name = table[0]
			print(f"{green}{i:02d}. Table: {table_name}{reset}")
			cursor.execute(f"PRAGMA table_info({table_name});")
			columns = [col[1] for col in cursor.fetchall()]
			print(f"{yellow}Columns: {', '.join(columns)}{reset}")
			cursor.execute(f"SELECT * FROM {table_name};")
			rows = cursor.fetchall()
			if rows:
				for row in rows:
					print(row)
			else:
				print(f"{red}-- No data in this table --{reset}")
			print("=" * 40)
	except Exception as e:
		print(f"Error: {e}")

def show_names():
	global cursor
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	tables = cursor.fetchall()
	for table in tables:
		print(table[0])

def show_table():
	global cursor
	while True:
		table_name = input(f"{yellow}Write (..) to exit\n{blue}Enter table name to show: {reset}").strip()
		if table_name == '..':
			break
		try:
			cursor.execute(f"SELECT * FROM {table_name};")
			rows = cursor.fetchall()
			for row in rows:
				print(row)
		except Exception as e:
			print(f"Error: {e}")

def delete_table():
	global conn, cursor
	while True:
		t_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter table name to delete : {reset}')
		if t_n == '..':
			break
		cursor.execute(f'DROP TABLE IF EXISTS {t_n};')
		conn.commit()
		print(f'{green}Deleted successfully!{reset}')

def rename_t():
	global conn, cursor
	while True:
		old_n = input(f'{yellow}- Write (..) to exit {blue}Enter the old name : {reset}')
		if old_n == '..':
			break
		new_n = input(f'{yellow}- Write (..) to exit {blue}Enter a new name : {reset}')
		if new_n == '..':
			break
		cursor.execute(f'ALTER TABLE {old_n} RENAME TO {new_n};')
		conn.commit()
		print(f'{green}Table renamed successfully!{reset}')
		break

def show_c():
	global cursor
	while True:
		t_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter table name : {reset}')
		if t_n == '..':
			break
		c_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter column name : {reset}')
		if c_n == '..':
			break
		cursor.execute(f'SELECT {c_n} FROM {t_n}')
		print(cursor.fetchall())

def add_c():
	global conn, cursor
	while True:
		t_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter table name : {reset}')
		if t_n == '..':
			break
		op = input(f'''{SkyB}Column type :
1 - TEXT
2 - INTEGER
3 - Exit
Choose : {reset}''')
		if op == '3':
			break
		c_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter the name of the new column : {reset}')
		if c_n == '..':
			break
		if op == '1':
			cursor.execute(f'ALTER TABLE {t_n} ADD COLUMN {c_n} TEXT')
		elif op == '2':
			cursor.execute(f'ALTER TABLE {t_n} ADD COLUMN {c_n} INTEGER')
		conn.commit()
		print(f'{green}Column added successfully!{reset}')

def rename_c():
	global conn, cursor
	while True:
		t_n = input(f'{yellow}- Write (..) to exit {blue}\nEnter table name : {reset}')
		if t_n == '..':
			break
		old_n = input(f'{yellow}- Write (..) to exit\n{blue}Enter the old name : {reset}')
		if old_n == '..':
			break
		new_n = input(f'{yellow}- Write (..) to exit\n{blue}Enter a new name : {reset}')
		if new_n == '..':
			break
		cursor.execute(f'ALTER TABLE {t_n} RENAME COLUMN {old_n} TO {new_n};')
		conn.commit()
		print(f'{green}Column renamed successfully!{reset}')
		break

def search():
	global cursor
	while True:
		t_n = input(f'{yellow}- Write (..) to exit {blue}\nEnter table name  : {reset}')
		if t_n == '..':
			break
		c_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter column name : {reset}')
		if c_n == '..':
			break
		op = input(f'''{SkyB}Search type :
1 - TEXT
2 - INTEGER
3 - Exit
Choose : {reset}''')
		if op == '3':
			break
		data = input(f'{yellow}- Write (..) to exit {blue}\nEnter the data to search : {reset}')
		if data == '..':
			break
		if op == '1':
			cursor.execute(f"SELECT * FROM {t_n} WHERE {c_n}='{data}';")
		elif op == '2':
			cursor.execute(f"SELECT * FROM {t_n} WHERE {c_n}={data};")
		print(cursor.fetchall())

def delete_data():
	global conn, cursor
	while True:
		table_name = input(f"{yellow}Write (..) to exit\n{blue}Enter table name: {reset}").strip()
		if table_name == "..":
			break
		column = input(f"{yellow}Write (..) to exit\n{blue}Enter column name to delete from: {reset}").strip()
		if column == "..":
			break
		type_choice = input(f"""{SkyB}
Delete from:
1 - TEXT
2 - INTEGER
3 - Exit
Choose: {reset}""").strip()
		if type_choice == "3":
			break
		row = input(f"{yellow}Write (..) to exit\nEnter the value to delete: {reset}").strip()
		if row == "..":
			break
		try:
			if type_choice == '1':
				cursor.execute(f"DELETE FROM {table_name} WHERE {column} = '{row}';")
			elif type_choice == '2':
				cursor.execute(f"DELETE FROM {table_name} WHERE {column} = {row};")
			else:
				continue
			conn.commit()
			print(f"{green}Delete value successfully!{reset}")
		except Exception as e:
			print(f"{red}Error: {e}{reset}")

def change_data():
	global conn, cursor
	while True:
		table_name = input(f"{yellow}Write (..) to exit\n{blue}Enter table name: {reset}").strip()
		if table_name == "..":
			break
		column = input(f"{yellow}Write (..) to exit\n{blue}Column to change: {reset}").strip()
		if column == "..":
			break
		cond_where = input(f"{yellow}Write (..) to exit\n{blue}Condition column: {reset}").strip()
		if cond_where == "..":
			break
		cond_value = input(f"{yellow}Write (..) to exit\n{blue}Condition value: {reset}").strip()
		if cond_value == "..":
			break
		type_choice = input(f"""{SkyB}Change type: 
1-TEXT 
2-INTEGER
3-Exit
Choose: {reset}""").strip()
		if type_choice == '3':
			break
		new_data = input(f"{yellow}Write (..) to exit\n{blue}Enter new value: {reset}").strip()
		if new_data == "..":
			break
		try:
			if type_choice == '1':
				cursor.execute(f"UPDATE {table_name} SET {column} = '{new_data}' WHERE {cond_where} = '{cond_value}';")
			elif type_choice == '2':
				cursor.execute(f"UPDATE {table_name} SET {column} = {new_data} WHERE {cond_where} = '{cond_value}';")
			conn.commit()
			print(f"{green}Update value successfully!{reset}")
		except Exception as e:
			print(f"Error: {e}")

def insert_d():
	global conn, cursor
	while True:
		t_n = input(f'{yellow}- Write (..) to exit {blue}\nEnter table name : {reset}')
		if t_n == '..':
			break
		c_n = input(f'''{yellow}- Write (..) to exit {blue}
Enter the names of the columns you want to add data to, like this:
first_name, last_name, age :{reset}
''')
		if c_n == '..':
			break
		data = input(f"""{yellow}- Write (..) to exit {blue}
Enter the data ( 'TEXT', INTEGER ), like that :
'ALI', 'Ahmed', 30 :{reset}
""")
		if data == '..':
			break
		cursor.execute(f"INSERT INTO {t_n} ({c_n}) VALUES ({data});")
		conn.commit()
		print(f'{green}Add data successfully!{reset}')

def edit():
	global conn, cursor
	while True:
		db_n = input(f'{yellow}- Write (..) to exit {blue}\n Enter the database name with (.db): {reset}')
		if db_n == '..':
			break
		if os.path.exists(db_n):
			conn = sqlite3.connect(db_n)
			cursor = conn.cursor()
			while True:
				op = input(f'''{SkyB}
1 - Show all database tables with their data
2 - Table names
3 - Show a specific table
4 - Drop a table
5 - Add a new table
6 - Rename a table
7 - Show a specific column
8 - Add a new column
9 - Rename a column
10 - Search for data
11 - Update data
12 - Delete data
13 - Insert new data
14 - EXIT
Choose : {reset}''')
				if op == '1':
					show_tables()
				elif op == '2':
					show_names()
				elif op == '3':
					show_table()
				elif op == '4':
					delete_table()
				elif op == '5':
					create_t()
				elif op == '6':
					rename_t()
				elif op == '7':
					show_c()
				elif op == '8':
					add_c()
				elif op == '9':
					rename_c()
				elif op == '10':
					search()
				elif op == '11':
					change_data()
				elif op == '12':
					delete_data()
				elif op == '13':
					insert_d()
				elif op == '14':
					conn.close()
					break
			break
		else:
			n_f = input(f'{yellow}There is no database with this name, Do you want to create a new one? (y/n) : {reset}')
			if n_f == 'y':
				create_db()
			else:
				break
while True:				
	options = input(f'''{blue}
1 - Create a database
2 - Manage a database
Choose : {reset}''')
	if options == '1':
		create_db()
	elif options == '2':
		edit()