import psutil
import tkinter as tk
from tkinter import ttk
import os

output_file = "system_monitor_log.txt"


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_system_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()

    # Обновление интерфейса
    clear_console()
    label_cpu.config(text=f"CPU Usage: {cpu_usage}%")
    label_memory.config(text=f"Memory Usage: {memory_info.percent}%")
    label_disk.config(text=f"Disk Usage: {disk_usage.percent}%")
    label_network.config(
        text=f"Network: Sent = {net_io.bytes_sent / (1024 * 1024):.2f} MB, Received = {net_io.bytes_recv / (1024 * 1024):.2f} MB")

    # Очистка и заполнение таблицы процессов
    tree.delete(*tree.get_children())
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
        try:
            processes.append(
                (proc.info['pid'], proc.info['name'], proc.info['memory_percent'], proc.info['cpu_percent']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Сортировка процессов по PID (по умолчанию)
    processes.sort(key=lambda x: int(x[0]))  # Преобразуем PID в целое число для корректной сортировки

    for pid, name, memory_percent, cpu_percent in processes:
        tree.insert('', 'end', values=(pid, name, f"{memory_percent:.2f}", f"{cpu_percent:.2f}"))


def save_to_file():
    with open(output_file, 'a') as f:
        f.write("\n\n=== Data saved at this moment ===\n")
        f.write(label_cpu.cget("text") + "\n")
        f.write(label_memory.cget("text") + "\n")
        f.write(label_disk.cget("text") + "\n")
        f.write(label_network.cget("text") + "\n")

        f.write("\nRunning Processes:\n")
        f.write(f"{'PID':>6} {'Name':<25} {'Memory%':>8} {'CPU%':>8}\n")
        for row_id in tree.get_children():
            row = tree.item(row_id)['values']
            f.write(f"{row[0]:>6} {row[1]:<25} {row[2]:>8} {row[3]:>8}\n")


# Функции сортировки по столбцам
def sort_column(col_id):
    # Получаем текущее состояние сортировки столбца
    current_sort_order = tree.heading(col_id)['command']

    # Определяем порядок сортировки (по возрастанию или убыванию)
    if current_sort_order == 'ascending':
        tree.heading(col_id, command=lambda: sort_column_desc(col_id))
    else:
        tree.heading(col_id, command=lambda: sort_column_asc(col_id))

    # Сортируем элементы по столбцу
    items = tree.get_children('')
    if col_id == 'PID':
        items = sorted(items, key=lambda x: int(tree.set(x, col_id)))
    else:
        items = sorted(items, key=lambda x: tree.set(x, col_id))

    for index, item in enumerate(items):
        tree.move(item, '', index)


# Функции сортировки по возрастанию и убыванию для каждого столбца
def sort_column_asc(col_id):
    tree.heading(col_id, command=lambda: sort_column_desc(col_id))
    items = tree.get_children('')
    if col_id == 'PID':
        items = sorted(items, key=lambda x: int(tree.set(x, col_id)))
    else:
        items = sorted(items, key=lambda x: tree.set(x, col_id))
    for index, item in enumerate(items):
        tree.move(item, '', index)


def sort_column_desc(col_id):
    tree.heading(col_id, command=lambda: sort_column_asc(col_id))
    items = tree.get_children('')
    if col_id == 'PID':
        items = sorted(items, key=lambda x: int(tree.set(x, col_id)), reverse=True)
    else:
        items = sorted(items, key=lambda x: tree.set(x, col_id), reverse=True)
    for index, item in enumerate(items):
        tree.move(item, '', index)


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
tree.heading('PID', text='PID', command=lambda: sort_column('PID'))
tree.heading('Name', text='Name', command=lambda: sort_column('Name'))
tree.heading('Memory%', text='Memory%', command=lambda: sort_column('Memory%'))
tree.heading('CPU%', text='CPU%', command=lambda: sort_column('CPU%'))

tree.column('#0', stretch=tk.YES)
tree.column('#1', stretch=tk.YES)
tree.column('#2', stretch=tk.YES)
tree.column('#3', stretch=tk.YES)
tree.grid(row=0, column=0, sticky="nsew")

scrollbar = ttk.Scrollbar(frame_processes, orient="vertical", command=tree.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
tree.configure(yscrollcommand=scrollbar.set)

# Кнопка для обновления данных
btn_refresh = ttk.Button(root, text="Refresh", command=print_system_usage)
btn_refresh.grid(row=1, column=0, pady=10, sticky="ew")

# Кнопка для сохранения данных в файл
btn_save = ttk.Button(root, text="Save to File", command=save_to_file)
btn_save.grid(row=1, column=1, pady=10, sticky="ew")

# Настройка растягиваемости и выравнивания элементов
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

frame_stats.columnconfigure(0, weight=1)
frame_stats.rowconfigure(0, weight=1)
frame_stats.rowconfigure(1, weight=1)
frame_stats.rowconfigure(2, weight=1)
frame_stats.rowconfigure(3, weight=1)

frame_processes.columnconfigure(0, weight=1)
frame_processes.rowconfigure(0, weight=1)

# Запуск основного цикла GUI
root.mainloop()
