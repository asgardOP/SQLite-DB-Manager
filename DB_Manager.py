import sqlite3
import os

# add tabulate import with graceful fallback
try:
    from tabulate import tabulate
except Exception:
    tabulate = None

red = "\033[91m"
green = "\033[92m"
white = "\033[97m"
yellow = "\033[33m"
SkyB = "\033[36m"
blue = "\033[34m"
purple = "\033[35m"
gray = "\033[90m"
C14 = "\033[38;5;159m"
reset = "\033[0m"
cursor = None
conn = None


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_table(rows, headers):
    """Pretty-print a table using tabulate if available, otherwise basic output."""
    if tabulate:
        try:
            print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            return
        except Exception:
            pass

    col_widths = [
        max(len(str(h)), *(len(str(r[i])) for r in rows) if rows else 0)
        for i, h in enumerate(headers)
    ]
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep = "-+-".join("-" * w for w in col_widths)
    print(header_line)
    print(sep)
    for r in rows:
        print(" | ".join(str(r[i]).ljust(col_widths[i]) for i in range(len(headers))))


def ex(e):
    return e == ".."


def create_db():
    clear()
    global conn, cursor
    while True:

        db_n = input(
            f"{yellow}- Write (..) to exit {blue}\n Enter the name of the new database: {reset}"
        )
        if ex(db_n):
            break

        # Add .db extension if not present
        if not db_n.endswith(".db"):
            db_n = f"{db_n}.db"

        if os.path.exists(db_n):
            print(f"{red}There is a database with this name, try again!{reset}")
        else:
            conn = sqlite3.connect(db_n)
            cursor = conn.cursor()
            print(f"{green}Database created successfully!{reset}")
            com = input(f"{yellow}Do you want to manage it ? (y/n) : {reset}")
            if com == "n":
                conn.close()
                break
            elif com == "y":
                edit()


def create_t():
    global conn, cursor
    clear()
    while True:
        t_n = input(
            f"{yellow}- Write (..) to exit {blue}\n Enter table name to create : {reset}"
        )
        if t_n == "..":
            break
        c_n = input(
            f"{yellow}- Write (..) to exit {blue}\n Enter columns name, text with TEXT, number with INTEGER, like that (name TEXT, age INTEGER) :\n {reset}"
        )
        if c_n == "..":
            break
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {t_n} (id INTEGER PRIMARY KEY AUTOINCREMENT, {c_n});"
        )
        conn.commit()
        print(f"{green}Table created successfully!{reset}")


def show_tables():
    global conn, cursor
    clear()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        if not tables:
            print(f"{red}No tables found in the database!{reset}")
            return
        rows = []
        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            # get row count safely
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
            except Exception:
                count = "N/A"
            rows.append([table_name, ", ".join(columns), count])
        print_table(rows, ["Table", "Columns", "Rows"])
    except Exception as e:
        print(f"Error: {e}")


def show_names():
    clear()
    global cursor
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])


def show_table():
    clear()
    global cursor
    while True:
        # list tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        if not tables:
            print(f"{red}No tables found in the database!{reset}")
            return
        rows = [[i, name] for i, name in enumerate(tables, 1)]
        print_table(rows, ["#", "Table"])

        sel = input(
            f"{yellow}Write (..) to exit\n{blue}Enter table name or number to show: {reset}"
        ).strip()
        if sel == "..":
            break

        # allow choosing by number
        if sel.isdigit():
            idx = int(sel) - 1
            if idx < 0 or idx >= len(tables):
                print(f"{red}Invalid table number.{reset}")
                continue
            table_name = tables[idx]
        else:
            table_name = sel

        if table_name not in tables:
            print(f"{red}Table {table_name} does not exist!{reset}")
            continue

        # get headers
        cursor.execute(f"PRAGMA table_info({table_name});")
        info = cursor.fetchall()
        headers = [col[1] for col in info] if info else []

        try:
            cursor.execute(f"SELECT * FROM {table_name};")
            data = cursor.fetchall()
        except Exception as e:
            print(f"{red}Error reading table: {e}{reset}")
            continue

        if not data:
            print(f"{yellow}Table {table_name} is empty.{reset}")
            if headers:
                print_table([], headers)
        else:
            print_table(data, headers)

        again = input(f"\n{yellow}Show another table? (y/n): {reset}").strip().lower()
        if again != "y":
            break


def delete_table():
    global conn, cursor
    clear()
    while True:
        # Show available tables first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        if not tables:
            print(f"{red}No tables found in the database!{reset}")
            return

        # Display tables with numbers
        rows = [[i, name] for i, name in enumerate(tables, 1)]
        print_table(rows, ["#", "Table"])

        t_n = input(
            f"{yellow}- Write (..) to exit {blue}\nEnter table name or number to delete: {reset}"
        ).strip()
        if t_n == "..":
            break

        # Handle selection by number
        if t_n.isdigit():
            idx = int(t_n) - 1
            if idx < 0 or idx >= len(tables):
                print(f"{red}Invalid table number.{reset}")
                continue
            t_n = tables[idx]

        # Verify table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t_n,)
        )
        if not cursor.fetchone():
            print(f"{red}Table {t_n} does not exist!{reset}")
            continue

        # Confirm deletion
        confirm = (
            input(f"{red}Are you sure you want to delete table '{t_n}'? (y/n): {reset}")
            .strip()
            .lower()
        )
        if confirm != "y":
            print(f"{yellow}Deletion cancelled.{reset}")
            continue

        try:
            cursor.execute(f"DROP TABLE IF EXISTS {t_n}")
            conn.commit()
            print(f"{green}Table '{t_n}' deleted successfully!{reset}")
        except Exception as e:
            print(f"{red}Error deleting table: {e}{reset}")
            conn.rollback()

        again = input(f"\n{yellow}Delete another table? (y/n): {reset}").strip().lower()
        if again != "y":
            break


def rename_t():
    global conn, cursor
    clear()
    while True:
        old_n = input(
            f"{yellow}- Write (..) to exit {blue}Enter the old name : {reset}"
        )
        if old_n == "..":
            break
        new_n = input(f"{yellow}- Write (..) to exit {blue}Enter a new name : {reset}")
        if new_n == "..":
            break
        cursor.execute(f"ALTER TABLE {old_n} RENAME TO {new_n};")
        conn.commit()
        print(f"{green}Table renamed successfully!{reset}")
        break


def show_c():
    global cursor
    clear()
    while True:
        t_n = input(f"{yellow}- Write (..) to exit {blue}\n Enter table name : {reset}")
        if t_n == "..":
            break
        c_n = input(
            f"{yellow}- Write (..) to exit {blue}\n Enter column name : {reset}"
        )
        if c_n == "..":
            break
        cursor.execute(f"SELECT {c_n} FROM {t_n}")
        print(cursor.fetchall())


def add_c():
    global conn, cursor
    clear()
    while True:
        t_n = input(f"{yellow}- Write (..) to exit {blue}\n Enter table name : {reset}")
        if t_n == "..":
            break
        op = input(
            f"""{SkyB}Column type :
1 - TEXT
2 - INTEGER
3 - Exit
Choose : {reset}"""
        )
        if op == "3":
            break
        c_n = input(
            f"{yellow}- Write (..) to exit {blue}\n Enter the name of the new column : {reset}"
        )
        if c_n == "..":
            break
        if op == "1":
            cursor.execute(f"ALTER TABLE {t_n} ADD COLUMN {c_n} TEXT")
        elif op == "2":
            cursor.execute(f"ALTER TABLE {t_n} ADD COLUMN {c_n} INTEGER")
        conn.commit()
        print(f"{green}Column added successfully!{reset}")


def rename_c():
    global conn, cursor
    clear()
    while True:
        t_n = input(f"{yellow}- Write (..) to exit {blue}\nEnter table name : {reset}")
        if t_n == "..":
            break
        old_n = input(
            f"{yellow}- Write (..) to exit\n{blue}Enter the old name : {reset}"
        )
        if old_n == "..":
            break
        new_n = input(f"{yellow}- Write (..) to exit\n{blue}Enter a new name : {reset}")
        if new_n == "..":
            break
        cursor.execute(f"ALTER TABLE {t_n} RENAME COLUMN {old_n} TO {new_n};")
        conn.commit()
        print(f"{green}Column renamed successfully!{reset}")
        break


def search():
    global cursor
    clear()
    while True:
        t_n = input(f"{yellow}- Write (..) to exit {blue}\nEnter table name  : {reset}")
        if t_n == "..":
            break
        c_n = input(
            f"{yellow}- Write (..) to exit {blue}\n Enter column name : {reset}"
        )
        if c_n == "..":
            break
        op = input(
            f"""{SkyB}Search type :
1 - TEXT
2 - INTEGER
3 - Exit
Choose : {reset}"""
        )
        if op == "3":
            break
        data = input(
            f"{yellow}- Write (..) to exit {blue}\nEnter the data to search : {reset}"
        )
        if data == "..":
            break
        if op == "1":
            cursor.execute(f"SELECT * FROM {t_n} WHERE {c_n}='{data}';")
        elif op == "2":
            cursor.execute(f"SELECT * FROM {t_n} WHERE {c_n}={data};")
        print(cursor.fetchall())


def delete_data():
    global conn, cursor
    clear()
    while True:
        table_name = input(
            f"{yellow}Write (..) to exit\n{blue}Enter table name: {reset}"
        ).strip()
        if table_name == "..":
            break
        column = input(
            f"{yellow}Write (..) to exit\n{blue}Enter column name to delete from: {reset}"
        ).strip()
        if column == "..":
            break
        type_choice = input(
            f"""{SkyB}
Delete from:
1 - TEXT
2 - INTEGER
3 - Exit
Choose: {reset}"""
        ).strip()
        if type_choice == "3":
            break
        row = input(
            f"{yellow}Write (..) to exit\nEnter the value to delete: {reset}"
        ).strip()
        if row == "..":
            break
        try:
            if type_choice == "1":
                cursor.execute(f"DELETE FROM {table_name} WHERE {column} = '{row}';")
            elif type_choice == "2":
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
        table_name = input(
            f"{yellow}Write (..) to exit\n{blue}Enter table name: {reset}"
        ).strip()
        if table_name == "..":
            break
        column = input(
            f"{yellow}Write (..) to exit\n{blue}Column to change: {reset}"
        ).strip()
        if column == "..":
            break
        cond_where = input(
            f"{yellow}Write (..) to exit\n{blue}Condition column: {reset}"
        ).strip()
        if cond_where == "..":
            break
        cond_value = input(
            f"{yellow}Write (..) to exit\n{blue}Condition value: {reset}"
        ).strip()
        if cond_value == "..":
            break
        type_choice = input(
            f"""{SkyB}Change type: 
1-TEXT 
2-INTEGER
3-Exit
Choose: {reset}"""
        ).strip()
        if type_choice == "3":
            break
        new_data = input(
            f"{yellow}Write (..) to exit\n{blue}Enter new value: {reset}"
        ).strip()
        if new_data == "..":
            break
        try:
            if type_choice == "1":
                cursor.execute(
                    f"UPDATE {table_name} SET {column} = '{new_data}' WHERE {cond_where} = '{cond_value}';"
                )
            elif type_choice == "2":
                cursor.execute(
                    f"UPDATE {table_name} SET {column} = {new_data} WHERE {cond_where} = '{cond_value}';"
                )
            conn.commit()
            print(f"{green}Update value successfully!{reset}")
        except Exception as e:
            print(f"Error: {e}")


def insert_d():
    global conn, cursor
    clear()
    while True:
        # Show available tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        if not tables:
            print(f"{red}No tables found in the current database!{reset}")
            break

        # prepare rows for display
        rows = []
        for i, name in enumerate(tables, 1):
            # fetch column count or columns for nicer display
            try:
                cursor.execute(f"PRAGMA table_info({name});")
                cols = [c[1] for c in cursor.fetchall()]
                col_str = ", ".join(cols)
            except Exception:
                col_str = ""
            rows.append([i, name, col_str])

        print_table(rows, ["#", "Table", "Columns"])

        t_n = input(
            f"{yellow}- Write (..) to exit {blue}\nEnter table name or number to insert into: {reset}"
        ).strip()
        if t_n == "..":
            break

        # allow choosing by number
        if t_n.isdigit():
            idx = int(t_n) - 1
            if idx < 0 or idx >= len(tables):
                print(f"{red}Invalid table number.{reset}")
                continue
            t_n = tables[idx]

        # Verify table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t_n,)
        )
        if not cursor.fetchone():
            print(f"{red}Table {t_n} does not exist!{reset}")
            continue

        # Get column information
        cursor.execute(f"PRAGMA table_info({t_n})")
        cols = cursor.fetchall()
        print(f"\n{yellow}Available columns (skip id):{reset}")
        for col in cols:
            if col[1] != "id":
                print(f"- {col[1]} ({col[2]})")

        c_n = input(
            f"""{yellow}- Write (..) to exit {blue}
Enter column names separated by commas (e.g.: first_name, last_name, age): {reset}"""
        ).strip()
        if c_n == "..":
            break

        column_names = [c.strip() for c in c_n.split(",") if c.strip()]
        if not column_names:
            print(f"{red}No columns provided.{reset}")
            continue

        # Collect values and validate columns exist
        values = []
        ok = True
        # Fetch PRAGMA once into a dict for quick lookup
        cursor.execute(f"PRAGMA table_info({t_n})")
        info = cursor.fetchall()
        col_types = {c[1]: c[2].upper() for c in info}
        for col in column_names:
            if col not in col_types:
                print(f"{red}Column {col} does not exist!{reset}")
                ok = False
                break
            val = input(f"{blue}Enter value for {col} ({col_types[col]}): {reset}")
            if val == "..":
                ok = False
                break
            # leave typing to SQLite; but try to convert integers to int
            if col_types[col] == "INTEGER":
                try:
                    values.append(int(val))
                except:
                    # fallback to original string; SQLite will cast if possible
                    values.append(val)
            else:
                values.append(val)
        if not ok:
            continue

        try:
            placeholders = ", ".join(["?"] * len(values))
            cols_sql = ", ".join(column_names)
            query = f"INSERT INTO {t_n} ({cols_sql}) VALUES ({placeholders});"
            cursor.execute(query, tuple(values))
            conn.commit()
            print(f"{green}Data inserted successfully!{reset}")

            # Show the inserted data
            print(f"\n{yellow}Inserted row:{reset}")
            cursor.execute(f"SELECT * FROM {t_n} WHERE rowid = last_insert_rowid()")
            print(cursor.fetchone())

        except Exception as e:
            print(f"{red}Error inserting data: {e}{reset}")
            conn.rollback()

        again = input(f"\n{yellow}Insert another row? (y/n): {reset}")
        if again.lower() != "y":
            break


def show_databases():
    clear()
    """Show all available .db files in current directory"""
    databases = sorted([f for f in os.listdir() if f.endswith(".db")])
    if not databases:
        print(f"{red}No databases found!{reset}")
        return None
    rows = [[i, db[:-3]] for i, db in enumerate(databases, 1)]
    print_table(rows, ["#", "Database"])
    return databases


def edit():
    global conn, cursor
    while True:
        # Show available databases
        databases = show_databases()
        if not databases:
            n_f = input(
                f"{yellow}Do you want to create a new database? (y/n) : {reset}"
            )
            if n_f == "y":
                create_db()
            break

        db_n = input(
            f"{yellow}- Write (..) to exit {blue}\nEnter the database name: {reset}"
        )
        if db_n == "..":
            break

        # Add .db extension if not present
        if not db_n.endswith(".db"):
            db_n = f"{db_n}.db"

        if os.path.exists(db_n):
            conn = sqlite3.connect(db_n)
            cursor = conn.cursor()
            while True:
                print("\n" + 40 * "=", "\nSelected database:", db_n, "\n")
                op = input(
                    f"""{SkyB}
1  - Show all database tables with their data
2  - Table names
3  - Show a specific table
4  - Drop a table
5  - Add a new table
6  - Rename a table
7  - Show a specific column
8  - Add a new column
9  - Rename a column
10 - Search for data
11 - Update data
12 - Delete data
13 - Insert new data
14 - EXIT

Choose : {reset}"""
                )
                if op == "1":
                    show_tables()
                elif op == "2":
                    show_names()
                elif op == "3":
                    show_table()
                elif op == "4":
                    delete_table()
                elif op == "5":
                    create_t()
                elif op == "6":
                    rename_t()
                elif op == "7":
                    show_c()
                elif op == "8":
                    add_c()
                elif op == "9":
                    rename_c()
                elif op == "10":
                    search()
                elif op == "11":
                    change_data()
                elif op == "12":
                    delete_data()
                elif op == "13":
                    insert_d()
                elif op == "14":
                    conn.close()
                    break
            break
        else:
            n_f = input(
                f"{yellow}There is no database with this name, Do you want to create a new one? (y/n) : {reset}"
            )
            if n_f == "y":
                create_db()
            else:
                break


while True:
    clear()
    options = input(
        f"""{blue}
1 - Create a database
2 - Manage a database
Choose : {reset}"""
    )
    if options == "1":
        create_db()
    elif options == "2":
        edit()
