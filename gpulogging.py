import psutil
import subprocess
import time
import csv
from datetime import datetime
import os
games_eng = ['C:\\Program Files (x86)\\Steam\\steamapps','C:\\XboxGames','C:\\Program Files\\EA Games']


def get_gpu_data():
    try:
        output = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu,utilization.gpu', '--format=csv,noheader,nounits'])
        output = output.decode('utf-8').strip()
        temp, utilization = map(int, output.split(', '))
        return temp, utilization
    except Exception as e:
        return None, None

# Function to get the game process using the most GPU
def get_top_gpu_process():
    try:
        # Get all processes that might be using the GPU
        output = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,process_name,used_gpu_memory', '--format=csv,noheader,nounits'])
        processes = output.decode('utf-8').strip().split('\n')

        if processes and processes[0]:
            for process in processes:
                pid, full_path, gpu_memory = process.split(', ')
                process_name = os.path.basename(full_path)

                # Check if the process name contains any of the game paths
                for game_path in games_eng:
                    if game_path in full_path:
                        # Return the base name of the game
                        game_name = os.path.basename(full_path).replace(".exe", "")
                        return game_name, gpu_memory
            return "N/A", 0
        else:
            return "N/A", 0
    except Exception as e:
        return "N/A", 0

# Function to log data
def log_data(file_name):
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow([
                'Timestamp', 'CPU_Usage', 'Memory_Usage', 'RAM_Total', 'RAM_Available',
                'RAM_Used', 'RAM_Percentage', 'Disk_Usage', 'GPU_Temperature', 'GPU_Usage',
                'Bytes_Sent', 'Bytes_Received', 'Top_GPU_Process', 'GPU_Memory_Used_by_Top_Process'
            ])

        while True:
            # Get the current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)

            # Get Memory (RAM) usage
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            ram_total = memory_info.total
            ram_available = memory_info.available
            ram_used = memory_info.used
            ram_percentage = memory_info.percent

            # Get Disk usage
            disk_usage = psutil.disk_usage('/').percent

            # Get GPU data
            gpu_temp, gpu_usage = get_gpu_data()

            # Get the top GPU-consuming process
            top_process, top_process_gpu_memory = get_top_gpu_process()

            # Get Network statistics
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent
            bytes_received = net_io.bytes_recv

            # Write data to CSV
            writer.writerow([
                timestamp, cpu_usage, memory_usage, ram_total, ram_available,
                ram_used, ram_percentage, disk_usage, gpu_temp, gpu_usage,
                bytes_sent, bytes_received, top_process, top_process_gpu_memory
            ])

            # Flush the file to ensure data is written
            file.flush()
            print(top_process , "at ", timestamp)
            print([
                timestamp, cpu_usage, memory_usage, ram_total, ram_available,
                ram_used, ram_percentage, disk_usage, gpu_temp, gpu_usage,
                bytes_sent, bytes_received, top_process, top_process_gpu_memory
            ])
            # Adjust sleep time based on whether a GPU-intensive task is running
            if top_process == "N/A":
                time.sleep(10)
            else:
                time.sleep(2)

file_path = r'C:\Users\mohda\Documents\Python Scripts\gpu_logging\system_usage_log.csv'

# Start logging data
log_data(file_path)