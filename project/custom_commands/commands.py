import os
import platform
import subprocess
from port_scanner.scanner import scan_ports
from debugging_monitoring.monitor import connect_to_service

def execute_command(command_name, *args):
    """Execute a custom command based on the name provided."""
    try:
        commands = {
            "get_os_info": get_os_info,
            "list_files": list_files,
            "run_shell": run_shell_command,
            "port_scan": port_scan_command,
            "network_monitor": network_monitor_command
        }

        if command_name in commands:
            return commands[command_name](*args)
        else:
            print(f"Command '{command_name}' not found.")
            return None
    except Exception as e:
        print(f"Error executing command '{command_name}': {e}")
        return None


def get_os_info():
    """Retrieve operating system information."""
    return {
        "OS": platform.system(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor()
    }


def list_files(directory="."):
    """List files in the specified directory."""
    try:
        return os.listdir(directory)
    except Exception as e:
        print(f"Error listing files: {e}")
        return None


def run_shell_command(command):
    """Run a shell command."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        print(f"Error running shell command: {e}")
        return None


def port_scan_command(target, port_range_start=1, port_range_end=1000):
    """Run the port scanning functionality."""
    print(f"Running port scan on {target} for ports {port_range_start}-{port_range_end}...")
    open_ports = scan_ports(target, (int(port_range_start), int(port_range_end)))
    return open_ports


def network_monitor_command(target, port, message=""):
    """Run the network monitoring functionality."""
    print(f"Monitoring network on {target}:{port}...")
    response = connect_to_service(target, int(port), message)
    return response


if __name__ == "__main__":
    print("Available commands: get_os_info, list_files, run_shell, port_scan, network_monitor")
    command = input("Enter a command name: ").strip()
    args = input("Enter arguments (if any, separated by space): ").split()
    
    result = execute_command(command, *args)
    if result:
        print(f"Result:\n{result}")
    else:
        print("No result returned.")
