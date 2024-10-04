# System Monitor Application

This Python application is a system monitoring tool with a graphical user interface (GUI) built using `tkinter`. It provides real-time information on CPU, memory, disk, network usage, and active processes. The application also supports monitoring GPU statistics using NVIDIA Management Library (NVML) and allows for process termination.

## Features

- Displays system information:
  - CPU usage
  - Memory usage
  - Disk usage
  - Network usage
  - GPU usage (if available)
  - Operating system details
- Lists currently running processes with sortable columns (PID, Name, Memory%, CPU%)
- Dynamic updates of system and process data every second
- Manual process killing by selecting a process from the list
- Saving system information and processes to a log file
- Option to enable or disable dynamic updates

## Running the Application

The application has been packaged into a standalone `exe` file using PyInstaller. This means you can run it without needing to install Python or any dependencies. Simply download the `exe` file and run it.

If you'd like to modify the code or contribute to the project, follow the steps below to set up the development environment.

## Requirements for Development

To modify or contribute to the project, you will need the following Python packages installed:

- `psutil`: for gathering system statistics
- `platform`: for retrieving OS and CPU information
- `tkinter`: for the graphical user interface (usually included with Python installations)
- `pynvml`: for retrieving GPU information using NVIDIA's NVML library (optional, only needed for GPU monitoring)

You can install the required packages using `pip`:

```bash
pip install psutil pynvml
