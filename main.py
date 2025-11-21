import concurrent.futures, tls_client, colorama, datetime, requests, random, base64, string, ctypes, copy, json, re, os, time

from colorama           import Fore
from datetime           import datetime


def set_console_size():
    try:
        os.system('mode con: cols=100 lines=30')
    except:
        pass

set_console_size()
try:
    codes = open("data/codes.txt", "r").read().splitlines()
    codes = [c for c in codes if c.strip()]
except FileNotFoundError:
    print(f"{Fore.RED}Error: data/codes.txt not found!{Fore.RESET}")
    input("Press enter to exit...")
    exit()

try:
    proxies = open("data/proxies.txt", "r").read().splitlines()
    proxies = [p for p in proxies if p.strip()]
except FileNotFoundError:
    print(f"{Fore.RED}Error: data/proxies.txt not found!{Fore.RESET}")
    input("Press enter to exit...")
    exit()

if not codes:
    print(f"{Fore.RED}Error: No codes found in data/codes.txt!{Fore.RESET}")
    input("Press enter to exit...")
    exit()

if not proxies:
    print(f"{Fore.RED}Error: No proxies found in data/proxies.txt!{Fore.RESET}")
    input("Press enter to exit...")
    exit()

colorama.init()

valid = 0
invalid = 0
fail = 0
start_time = None

def title_worker():
    global valid, invalid, fail
    ctypes.windll.kernel32.SetConsoleTitleW(f'Discord Promo Checker @Beatsbyluca ~ Valid : {valid} | Invalid: {invalid} | Failed : {fail}')

def log(text):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f' {Fore.LIGHTBLACK_EX}[{current_time}] ({Fore.CYAN}+{Fore.LIGHTBLACK_EX}){Fore.RESET} {text}')

def error(text):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f' {Fore.LIGHTBLACK_EX}[{current_time}] ({Fore.CYAN}-{Fore.LIGHTBLACK_EX}){Fore.RESET} {text}')

def failed(text):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f' {Fore.LIGHTBLACK_EX}[{current_time}] ({Fore.CYAN}!{Fore.LIGHTBLACK_EX}){Fore.RESET} {text}')

base_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
}

def check(code: str):
    global valid, invalid, fail
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        proxy = random.choice(proxies)
        headers = copy.copy(base_headers)
        code = code.strip()
        if "https://" in code or "http://" in code:
            gift = code.split("/")[-1]
        elif "/" in code:
            gift = code.split("/")[-1]
        else:
            gift = code
        
        if "/" in code:
            base_url = "/".join(code.split("/")[:-1])
            display_code = f"{base_url}/{gift[:10]}***"
        else:
            display_code = code[:10] + "***"
        
        print(f" {Fore.LIGHTBLACK_EX}[{current_time}] ({Fore.CYAN}~{Fore.LIGHTBLACK_EX}){Fore.WHITE} Checking: {Fore.LIGHTBLACK_EX}{display_code}{Fore.RESET}")
        
        session = tls_client.Session(client_identifier="chrome_111", random_tls_extension_order=True)
        response = session.get(f"https://discord.com/api/v9/entitlements/gift-codes/{gift}?country_code=DE&with_application=false&with_subscription_plan=true", headers = headers, proxy=f"http://{proxy}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                short_code = code[:10] + "***"
                
                interval_count = response_json.get("subscription_trial", {}).get("interval_count", "Unknown")
                months = f"{interval_count} month{'s' if interval_count > 1 else ''}"
                
                expires_at = response_json.get("expires_at", "")
                if expires_at:
                    expire_date = datetime.fromisoformat(expires_at.replace("+00:00", ""))
                    now_date = datetime.now()
                    days_left = (expire_date - now_date).days
                    validity = f"{days_left} days"
                else:
                    validity = "Unknown"
                
                log(f"Valid {Fore.LIGHTBLACK_EX}- {short_code} |{Fore.RESET} Nitro: {Fore.LIGHTBLACK_EX}{months}{Fore.RESET} | Valid: {Fore.LIGHTBLACK_EX}{validity}{Fore.RESET}")
            except Exception as e:
                log(f"Valid {Fore.LIGHTBLACK_EX}- {code[:10]}*** | Error parsing: {e}{Fore.RESET}")
            
            valid += 1
            title_worker()
            with open("valid.txt", "a") as gifts:
                gifts.write(f"{code}\n")
        elif response.status_code == 429:
            failed("Failed to check, due to ratelimit")
            fail += 1
            title_worker()
        elif response.status_code == 404:
            error(f"Invalid {Fore.LIGHTBLACK_EX}- {code[:10]}***{Fore.RESET}")
            invalid += 1
            title_worker()
        else:
            failed(f"Failed to check {Fore.LIGHTBLACK_EX}- Status: {response.status_code}{Fore.RESET}")
            fail += 1
            title_worker()
    except Exception as e:
        failed(f"Error checking {Fore.LIGHTBLACK_EX}{code[:10] if len(code) >= 10 else code}***: {str(e)}{Fore.RESET}")
        fail += 1
        title_worker()

def main():
    global start_time
    title_worker()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    os.system("cls")
    
    print(f" {Fore.LIGHTBLACK_EX}[{current_time}] ({Fore.CYAN}!{Fore.LIGHTBLACK_EX}){Fore.RESET} Loaded {Fore.LIGHTBLACK_EX}{len(codes)}{Fore.RESET} codes and {Fore.LIGHTBLACK_EX}{len(proxies)}{Fore.RESET} proxies")
    
    threads = int(input(f" {Fore.LIGHTBLACK_EX}[{current_time}] ({Fore.CYAN}?{Fore.LIGHTBLACK_EX}){Fore.RESET} Enter threads: {Fore.LIGHTBLACK_EX}"))
    print(Fore.RESET, end='')
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as checker:
        for code in codes:
            checker.submit(check, code)
    
    elapsed_time = time.time() - start_time
    elapsed_str = f"{elapsed_time:.2f}s" if elapsed_time < 60 else f"{int(elapsed_time//60)}m {int(elapsed_time%60)}s"
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"\n {Fore.LIGHTBLACK_EX}[{current_time}] ({Fore.CYAN}!{Fore.LIGHTBLACK_EX}){Fore.RESET} Finished {Fore.LIGHTBLACK_EX}|{Fore.RESET} Valid: {Fore.LIGHTBLACK_EX}{valid}{Fore.RESET} {Fore.LIGHTBLACK_EX}|{Fore.RESET} Invalid: {Fore.LIGHTBLACK_EX}{invalid}{Fore.RESET} {Fore.LIGHTBLACK_EX}|{Fore.RESET} Failed: {Fore.LIGHTBLACK_EX}{fail}{Fore.RESET} {Fore.LIGHTBLACK_EX}|{Fore.RESET} Time: {Fore.LIGHTBLACK_EX}{elapsed_str}{Fore.RESET}")
    input(f" {Fore.LIGHTBLACK_EX}[{current_time}] ({Fore.CYAN}!{Fore.LIGHTBLACK_EX}){Fore.RESET} Press enter to exit{Fore.LIGHTBLACK_EX}...{Fore.RESET}")

main()