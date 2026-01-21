#!/usr/bin/env python3
"""
Toribot Controller - Terminal User Interface for managing both bots
Allows starting/stopping toribot and ostobotti with only one running at a time
"""

import os
import sys
import time
import subprocess
import signal
from datetime import datetime

# ANSI color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ToribotController:
    def __init__(self):
        self.running_process = None
        self.running_bot = None
        self.log_lines = []
        self.max_log_lines = 100
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """Print application header"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("=" * 60)
        print("        🤖 TORIBOT CONTROLLER 🤖")
        print("=" * 60)
        print(f"{Colors.ENDC}")
        
        if self.running_bot:
            status = f"{Colors.GREEN}RUNNING{Colors.ENDC}"
            print(f"Status: {status} | Active Bot: {Colors.BOLD}{self.running_bot}{Colors.ENDC}")
        else:
            status = f"{Colors.YELLOW}IDLE{Colors.ENDC}"
            print(f"Status: {status} | No bot running")
        
        print(f"{Colors.CYAN}{'=' * 60}{Colors.ENDC}\n")
    
    def print_menu(self):
        """Print main menu"""
        print(f"{Colors.BOLD}Main Menu:{Colors.ENDC}")
        print(f"  {Colors.GREEN}1.{Colors.ENDC} Start Toribot (Free Items - Annataan)")
        print(f"  {Colors.GREEN}2.{Colors.ENDC} Start Ostobotti (Wanted/Buying - Ostetaan)")
        print(f"  {Colors.YELLOW}3.{Colors.ENDC} Stop Running Bot")
        print(f"  {Colors.BLUE}4.{Colors.ENDC} View Logs (Last 20 lines)")
        print(f"  {Colors.BLUE}5.{Colors.ENDC} View Status")
        print(f"  {Colors.BLUE}6.{Colors.ENDC} Open Web GUI")
        print(f"  {Colors.RED}0.{Colors.ENDC} Exit")
        print()
    
    def start_bot(self, bot_name):
        """Start a bot process"""
        if self.running_process:
            print(f"{Colors.RED}Error: {self.running_bot} is already running!{Colors.ENDC}")
            print(f"{Colors.YELLOW}Please stop it first (option 3){Colors.ENDC}")
            return False
        
        bot_file = "toribot.py" if bot_name == "Toribot" else "ostobotti.py"
        
        if not os.path.exists(bot_file):
            print(f"{Colors.RED}Error: {bot_file} not found!{Colors.ENDC}")
            return False
        
        try:
            print(f"{Colors.CYAN}Starting {bot_name}...{Colors.ENDC}")
            
            # Start bot in subprocess
            self.running_process = subprocess.Popen(
                [sys.executable, bot_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.running_bot = bot_name
            
            # Wait a moment and check if it started successfully
            time.sleep(2)
            
            if self.running_process.poll() is None:
                print(f"{Colors.GREEN}✓ {bot_name} started successfully!{Colors.ENDC}")
                port = "8788" if bot_name == "Toribot" else "8789"
                print(f"{Colors.CYAN}Web GUI available at: http://127.0.0.1:{port}{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.RED}✗ {bot_name} failed to start{Colors.ENDC}")
                self.running_process = None
                self.running_bot = None
                return False
                
        except Exception as e:
            print(f"{Colors.RED}Error starting bot: {e}{Colors.ENDC}")
            self.running_process = None
            self.running_bot = None
            return False
    
    def stop_bot(self):
        """Stop the running bot"""
        if not self.running_process:
            print(f"{Colors.YELLOW}No bot is currently running{Colors.ENDC}")
            return False
        
        try:
            print(f"{Colors.CYAN}Stopping {self.running_bot}...{Colors.ENDC}")
            
            # Send SIGINT (Ctrl+C) for graceful shutdown
            self.running_process.send_signal(signal.SIGINT)
            
            # Wait for process to terminate (max 10 seconds)
            try:
                self.running_process.wait(timeout=10)
                print(f"{Colors.GREEN}✓ {self.running_bot} stopped successfully{Colors.ENDC}")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown failed
                self.running_process.kill()
                self.running_process.wait()
                print(f"{Colors.YELLOW}⚠ {self.running_bot} force-stopped{Colors.ENDC}")
            
            self.running_process = None
            self.running_bot = None
            return True
            
        except Exception as e:
            print(f"{Colors.RED}Error stopping bot: {e}{Colors.ENDC}")
            return False
    
    def view_logs(self, num_lines=20):
        """View recent log output"""
        if not self.running_process:
            print(f"{Colors.YELLOW}No bot is currently running{Colors.ENDC}")
            return
        
        print(f"{Colors.BOLD}Last {num_lines} log lines from {self.running_bot}:{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-' * 60}{Colors.ENDC}")
        
        try:
            # Read available output (limited to prevent blocking)
            lines_read = 0
            max_reads = 100  # Prevent infinite loop
            while lines_read < max_reads:
                line = self.running_process.stdout.readline()
                if not line:
                    break
                self.log_lines.append(line.strip())
                if len(self.log_lines) > self.max_log_lines:
                    self.log_lines.pop(0)
                lines_read += 1
        except:
            pass
        
        # Display last N lines
        for line in self.log_lines[-num_lines:]:
            print(line)
        
        print(f"{Colors.CYAN}{'-' * 60}{Colors.ENDC}")
    
    def view_status(self):
        """View detailed status"""
        print(f"{Colors.BOLD}System Status:{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-' * 60}{Colors.ENDC}")
        
        # Running bot status
        if self.running_bot:
            print(f"  Active Bot: {Colors.GREEN}{self.running_bot}{Colors.ENDC}")
            print(f"  PID: {self.running_process.pid}")
            
            port = "8788" if self.running_bot == "Toribot" else "8789"
            bot_type = "Free Items (Annataan)" if self.running_bot == "Toribot" else "Wanted/Buying (Ostetaan)"
            
            print(f"  Type: {bot_type}")
            print(f"  Web GUI: http://127.0.0.1:{port}")
            
            # Check if process is still alive
            if self.running_process.poll() is None:
                print(f"  Status: {Colors.GREEN}Running{Colors.ENDC}")
            else:
                print(f"  Status: {Colors.RED}Terminated{Colors.ENDC}")
                self.running_process = None
                self.running_bot = None
        else:
            print(f"  Active Bot: {Colors.YELLOW}None{Colors.ENDC}")
        
        print()
        
        # Check for data files
        print(f"{Colors.BOLD}Data Files:{Colors.ENDC}")
        
        files_to_check = [
            ("products.json", "Toribot products"),
            ("ostobotti_products.json", "Ostobotti products"),
            ("settings.json", "Toribot settings"),
            ("ostobotti_settings.json", "Ostobotti settings")
        ]
        
        for filename, description in files_to_check:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                mtime = datetime.fromtimestamp(os.path.getmtime(filename))
                print(f"  {Colors.GREEN}✓{Colors.ENDC} {description}: {size} bytes (modified: {mtime.strftime('%Y-%m-%d %H:%M')})")
            else:
                print(f"  {Colors.YELLOW}✗{Colors.ENDC} {description}: Not found")
        
        print(f"{Colors.CYAN}{'-' * 60}{Colors.ENDC}")
    
    def open_gui(self):
        """Open web GUI in browser"""
        if not self.running_bot:
            print(f"{Colors.YELLOW}No bot is currently running. Please start a bot first.{Colors.ENDC}")
            return
        
        port = "8788" if self.running_bot == "Toribot" else "8789"
        url = f"http://127.0.0.1:{port}"
        
        print(f"{Colors.CYAN}Opening web GUI: {url}{Colors.ENDC}")
        
        # Try to open in browser
        try:
            import webbrowser
            webbrowser.open(url)
            print(f"{Colors.GREEN}✓ Browser opened{Colors.ENDC}")
        except:
            print(f"{Colors.YELLOW}Could not open browser automatically.{Colors.ENDC}")
            print(f"Please open manually: {url}")
    
    def run(self):
        """Main application loop"""
        try:
            while True:
                self.clear_screen()
                self.print_header()
                self.print_menu()
                
                choice = input(f"{Colors.BOLD}Enter your choice: {Colors.ENDC}").strip()
                
                if choice == "1":
                    self.start_bot("Toribot")
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
                
                elif choice == "2":
                    self.start_bot("Ostobotti")
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
                
                elif choice == "3":
                    self.stop_bot()
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
                
                elif choice == "4":
                    self.view_logs()
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
                
                elif choice == "5":
                    self.view_status()
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
                
                elif choice == "6":
                    self.open_gui()
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
                
                elif choice == "0":
                    if self.running_process:
                        print(f"{Colors.YELLOW}Stopping running bot before exit...{Colors.ENDC}")
                        self.stop_bot()
                    print(f"{Colors.GREEN}Goodbye!{Colors.ENDC}")
                    break
                
                else:
                    print(f"{Colors.RED}Invalid choice. Please try again.{Colors.ENDC}")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrupted by user{Colors.ENDC}")
            if self.running_process:
                print(f"{Colors.YELLOW}Stopping running bot...{Colors.ENDC}")
                self.stop_bot()
        
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
            if self.running_process:
                self.stop_bot()


def main():
    """Entry point"""
    print(f"{Colors.BOLD}{Colors.CYAN}Toribot Controller Starting...{Colors.ENDC}\n")
    
    # Check if bot files exist
    if not os.path.exists("toribot.py") or not os.path.exists("ostobotti.py"):
        print(f"{Colors.RED}Error: Bot files not found!{Colors.ENDC}")
        print("Please run this script from the toribot directory")
        sys.exit(1)
    
    controller = ToribotController()
    controller.run()


if __name__ == "__main__":
    main()
