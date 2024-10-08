# System Monitor Application

[![Windows](https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white)](#)
[![GitHub Release](https://img.shields.io/github/v/release/Lixetron/system-monitor)](releases/latest)
[![GitHub License](https://img.shields.io/github/license/Lixetron/system-monitor)](LICENSE)

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

### GUI Features

- **Dynamic Update**: Enable or disable real-time updates by clicking the "Enable Dynamic Update" button. When dynamic updates are enabled, data will be refreshed every second.
- **Manual Update**: If dynamic updates are disabled, you can manually refresh the data by clicking the "Manual Update" button.
- **Kill Process**: Select a process from the list and click "Kill Process" to terminate it.
- **Save Log**: Save the current system statistics and list of running processes to a log file by selecting "File > Save Log As..." from the menu.

### Running the Application

The application has been packaged into a standalone `exe` file using PyInstaller. This means you can run it without needing to install Python or any dependencies. Simply download the `exe` file and run it.

If you'd like to modify the code or contribute to the project, follow the steps below to set up the development environment.

## How to Run the Application from Source

### Prerequisites

- Python 3.x installed on your system
- Clone the repository to your local machine

### Steps to Run

1. Install the required dependencies using pip as mentioned above.

  ```bash
  pip install psutil pynvml
  ```
   
2. Run the Python script:

  ```bash
  python monitor.py
  ```

Once started, the application will display system usage statistics and a list of running processes. You can sort the processes by clicking on the column headers.

### Requirements for Development

To modify or contribute to the project, you will need the following Python packages installed:

- `psutil`: for gathering system statistics
- `platform`: for retrieving OS and CPU information
- `tkinter`: for the graphical user interface (usually included with Python installations)
- `pynvml`: for retrieving GPU information using NVIDIA's NVML library (optional, only needed for GPU monitoring)

You can install the required packages using `pip`:

### GPU Monitoring

If you have an NVIDIA GPU and have the `pynvml` library installed, the application will display information about your GPU, including total, used, and available memory.

### Building the Application

If you'd like to build the `exe` file yourself using PyInstaller, follow these steps (for Windows):

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Build the executable:

```bash
pyinstaller --onefile monitor.py
```

This will create a standalone `exe` file that can be distributed and run on any compatible Windows system.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
