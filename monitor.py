import psutil
import tkinter as tk
from tkinter import ttk, filedialog
import os
import datetime
import threading

output_file = ""  # Глобальная переменная для пути сохранения файла
dynamic_update_enabled = False  # Флаг для отслеживания состояния динамического обновления
current_sort_column = 'PID'  # Колонка, по которой сортируем в данный момент
current_sort_order = 'asc'  # Порядок сортировки: 'asc' или 'desc'


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def sort_processes(processes):
    global current_sort_column, current_sort_order
    if current_sort_column == 'PID':
        processes.sort(key=lambda x: int(x[0]), reverse=(current_sort_order == 'desc'))
    else:
        index = {'Name': 1, 'Memory%': 2, 'CPU%': 3}[current_sort_column]
        processes.sort(key=lambda x: x[index], reverse=(current_sort_order == 'desc'))
    return processes


def update_treeview(tree, processes):
    selected_item = tree.selection()
    selected_pid = None
    if selected_item:
        selected_pid = tree.item(selected_item, 'values')[0]

    for row in tree.get_children():
        tree.delete(row)

    for pid, name, memory_percent, cpu_percent in processes:
        tree.insert('', 'end', values=(pid, name, f"{memory_percent:.2f}", f"{cpu_percent:.2f}"))

    if selected_pid:
        for row in tree.get_children():
            if tree.item(row, 'values')[0] == selected_pid:
                tree.selection_set(row)
                break


def fetch_system_usage():
    cpu_usage = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    return cpu_usage, memory_info, disk_usage, net_io


def fetch_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
        try:
            processes.append(
                (proc.info['pid'], proc.info['name'], proc.info['memory_percent'], proc.info['cpu_percent']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes


def update_system_info():
    cpu_usage, memory_info, disk_usage, net_io = fetch_system_usage()

    label_cpu.config(text=f"CPU Usage: {cpu_usage}%")
    label_memory.config(text=f"Memory Usage: {memory_info.percent}%")
    label_disk.config(text=f"Disk Usage: {disk_usage.percent}%")
    label_network.config(
        text=f"Network: Sent = {net_io.bytes_sent / (1024 * 1024):.2f} MB, Received = {net_io.bytes_recv / (1024 * 1024):.2f} MB")


def refresh_data():
    processes = fetch_processes()
    processes = sort_processes(processes)
    update_treeview(tree, processes)


def print_system_usage():
    global dynamic_update_enabled

    update_system_info()
    refresh_data()

    if dynamic_update_enabled:
        root.after(1000, print_system_usage)  # Планируем следующее обновление через 1 секунду


def toggle_dynamic_update():
    global dynamic_update_enabled
    dynamic_update_enabled = not dynamic_update_enabled
    if dynamic_update_enabled:
        label_update_status.config(text="Dynamic update: ON", foreground="green")
        btn_toggle_update.config(text="Disable Dynamic Update\n(Enabled)")
        btn_manual_update.config(state=tk.DISABLED)  # Блокируем кнопку ручного обновления
        threading.Thread(target=print_system_usage).start()  # Начать динамическое обновление в отдельном потоке
    else:
        label_update_status.config(text="Dynamic update: OFF", foreground="red")
        btn_toggle_update.config(text="Enable Dynamic Update\n(Disabled)")
        btn_manual_update.config(state=tk.NORMAL)  # Разблокируем кнопку ручного обновления


def manual_update():
    if dynamic_update_enabled:
        return  # Игнорируем ручное обновление, если включено динамическое
    update_system_info()  # Обновляем системную информацию
    refresh_data()  # Выполняем ручное обновление данных


def save_to_file():
    global output_file
    if not output_file:
        output_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not output_file:
            return  # Если пользователь отменил выбор файла, выходим из функции

    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_file, 'a') as f:
        f.write(f"=== Data saved at {current_datetime} ===\n")
        f.write(label_cpu.cget("text") + "\n")
        f.write(label_memory.cget("text") + "\n")
        f.write(label_disk.cget("text") + "\n")
        f.write(label_network.cget("text") + "\n")

        f.write("\nRunning Processes:\n")
        f.write(f"{'PID':>6} {'Name':<25} {'Memory%':>8} {'CPU%':>8}\n")
        for row_id in tree.get_children():
            row = tree.item(row_id)['values']
            f.write(f"{row[0]:>6} {row[1]:<25} {row[2]:>8} {row[3]:>8}\n")


def sort_column(tree, col_id):
    global current_sort_column, current_sort_order
    if current_sort_column == col_id:
        current_sort_order = 'desc' if current_sort_order == 'asc' else 'asc'
    else:
        current_sort_column = col_id
        current_sort_order = 'asc'

    data = [(tree.set(child, col_id), child) for child in tree.get_children('')]
    if current_sort_column == 'PID':
        data.sort(key=lambda x: int(x[0]), reverse=(current_sort_order == 'desc'))
    else:
        data.sort(reverse=(current_sort_order == 'desc'))

    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)

    update_column_headings(tree)


def update_column_headings(tree):
    columns = ['PID', 'Name', 'Memory%', 'CPU%']
    for col in columns:
        heading = col
        if col == current_sort_column:
            if current_sort_order == 'asc':
                heading += " ↑"
            else:
                heading += " ↓"
        tree.heading(col, text=heading, command=lambda _col=col: sort_column(tree, _col))


def kill_process():
    selected_item = tree.selection()
    if not selected_item:
        return

    pid = tree.item(selected_item, 'values')[0]
    try:
        pid = int(pid)  # Преобразуем PID к целочисленному типу
        if pid < 0:
            return

        proc = psutil.Process(pid)

        # Рекурсивно завершаем процесс и все его дочерние процессы
        for child in proc.children(recursive=True):
            child.terminate()
        proc.terminate()

        refresh_data()
    except ValueError:
        print(f"Invalid PID value: {pid}")
    except psutil.NoSuchProcess:
        print(f"Process with PID {pid} no longer exists.")
    except psutil.AccessDenied:
        print(f"Access to terminate process with PID {pid} denied.")


# Создание GUI
root = tk.Tk()
root.title("System Monitor")

# Фрейм с основными метками
frame_stats = ttk.Frame(root, padding="10")
frame_stats.grid(row=0, column=0, sticky="nsew")

label_cpu = ttk.Label(frame_stats, text="CPU Usage: ")
label_cpu.grid(row=0, column=0, sticky="w")

label_memory = ttk.Label(frame_stats, text="Memory Usage: ")
label_memory.grid(row=1, column=0, sticky="w")

label_disk = ttk.Label(frame_stats, text="Disk Usage: ")
label_disk.grid(row=2, column=0, sticky="w")

label_network = ttk.Label(frame_stats, text="Network: ")
label_network.grid(row=3, column=0, sticky="w")

# Фрейм с таблицей процессов
frame_processes = ttk.Frame(root, padding="10")
frame_processes.grid(row=0, column=1, sticky="nsew")

tree = ttk.Treeview(frame_processes, columns=('PID', 'Name', 'Memory%', 'CPU%'), show='headings')
tree.heading('PID', text='PID', command=lambda: sort_column(tree, 'PID'))
tree.heading('Name', text='Name', command=lambda: sort_column(tree, 'Name'))
tree.heading('Memory%', text='Memory%', command=lambda: sort_column(tree, 'Memory%'))
tree.heading('CPU%', text='CPU%', command=lambda: sort_column(tree, 'CPU%'))

tree.column('#0', stretch=tk.YES)
tree.column('#1', stretch=tk.YES)
tree.column('#2', stretch=tk.YES)
tree.column('#3', stretch=tk.YES)
tree.grid(row=0, column=0, sticky="nsew")

scrollbar = ttk.Scrollbar(frame_processes, orient="vertical", command=tree.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
tree.configure(yscrollcommand=scrollbar.set)

# Кнопка для включения/отключения динамического обновления
btn_toggle_update = ttk.Button(root, text="Enable Dynamic Update\n(Disabled)", command=toggle_dynamic_update)
btn_toggle_update.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

# Кнопка для ручного обновления данных
btn_manual_update = ttk.Button(root, text="Manual Update", command=manual_update)
btn_manual_update.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

# Кнопка для завершения процесса
btn_kill_process = ttk.Button(root, text="Kill Process", command=kill_process)
btn_kill_process.grid(row=1, column=2, sticky="ew", padx=10, pady=10)

# Метка для отображения состояния динамического обновления
label_update_status = ttk.Label(root, text="Dynamic update: OFF", foreground="red")
label_update_status.grid(row=2, column=0, columnspan=3, pady=5)

# Настройка растягиваемости и выравнивания элементов
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=1)

frame_stats.columnconfigure(0, weight=1)
frame_stats.rowconfigure(0, weight=1)
frame_stats.rowconfigure(1, weight=1)
frame_stats.rowconfigure(2, weight=1)
frame_stats.rowconfigure(3, weight=1)

frame_processes.columnconfigure(0, weight=1)
frame_processes.rowconfigure(0, weight=1)

# При запуске приложения сразу подтягиваем данные
print_system_usage()  # Обновление данных
update_column_headings(tree)  # Обновить заголовки столбцов

# Меню для выбора места сохранения лог-файла
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save Log As...", command=save_to_file)

# Запуск основного цикла GUI
root.mainloop()
