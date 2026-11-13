import pyautogui
import time
import keyboard
import win32api, win32con
import tkinter as tk
from tkinter import ttk
import threading
import os

class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SR_BOT")
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        
        # Bot state
        self.running = False
        self.bot_thread = None
        self.plane_spot = 0
        
        # Spot coordinates
        self.spot_coordinates = [
            [1015, 1300],
            [1095, 1300],
            [1180, 1300],
            [1260, 1300],
            [1340, 1300],
            [1415, 1300]
        ]
        
        self.region = (100, 90, 1800, 1100)

        self.style = ttk.Style()
        self.style.configure("Selected.TButton", background="green")
        
        self.setup_gui()
    
    def setup_gui(self):
        # Title
        title_label = ttk.Label(self.root, text="SpeedService", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Plane spot selection label
        spot_label = ttk.Label(self.root, text="Select Plane Spot (1-6):")
        spot_label.pack(pady=5)
        
        # Plane spot buttons frame
        spots_frame = ttk.Frame(self.root)
        spots_frame.pack(pady=10)
        
        # Create 6 spot buttons
        self.spot_buttons = []
        for i in range(6):
            btn = ttk.Button(spots_frame, text=str(i+1), 
                           command=lambda idx=i: self.select_spot(idx))
            btn.grid(row=0, column=i, padx=5)
            self.spot_buttons.append(btn)
        
        # Update the initially selected spot
        self.update_spot_buttons()
        
        # Current spot display
        self.current_spot_var = tk.StringVar(value=f"Current Spot: {self.plane_spot + 1}")
        current_spot_label = ttk.Label(self.root, textvariable=self.current_spot_var, font=("Arial", 12))
        current_spot_label.pack(pady=10)
        
        # Control buttons frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=20)
        
        # Start button
        self.start_button = ttk.Button(control_frame, text="Start Bot", command=self.start_bot)
        self.start_button.grid(row=0, column=0, padx=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Status: Stopped")
        status_label = ttk.Label(self.root, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(pady=5)
        
        # Instruction label
        instruction_label = ttk.Label(self.root, text="Press Q to stop bot", font=("Arial", 9), foreground="gray")
        instruction_label.pack(pady=10)
    
    def select_spot(self, spot_index):
        self.plane_spot = spot_index
        self.current_spot_var.set(f"Current Spot: {self.plane_spot + 1}")
        self.update_spot_buttons()
    
    def update_spot_buttons(self):
        for i, btn in enumerate(self.spot_buttons):
            if i == self.plane_spot:
                btn.configure(style="Selected.TButton")
                btn.state(['pressed', 'disabled'])
            else:
                btn.configure(style="TButton")  
                btn.state(['!disabled'])
    
    def click(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0) 
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    
    def bot_loop(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(script_dir, 'assets', 'qs_1440p.png')
        while self.running and not keyboard.is_pressed('q'):
            x, y = self.spot_coordinates[self.plane_spot]
            self.click(x, y)
            
            try:
                found = pyautogui.locateOnScreen(img_path, 
                                               confidence=0.80,
                                               grayscale=True,
                                               region=self.region)
                if found:
                    center = pyautogui.center(found)
                    self.click(center.x, center.y)
            except:
                pass
            
            time.sleep(0.08)
        
        # If loop exits, stop the bot
        if self.running:
            self.stop_bot()
    
    def start_bot(self):
        if not self.running:
            self.running = True
            self.status_var.set("Status: Running")
            self.start_button.config(state="disabled")
            
            # Disable spot selection while bot is running
            for btn in self.spot_buttons:
                btn.config(state="disabled")
            
            # Start bot in a separate thread
            self.bot_thread = threading.Thread(target=self.bot_loop)
            self.bot_thread.daemon = True
            self.bot_thread.start()
    
    def stop_bot(self):
        if self.running:
            self.running = False
            self.status_var.set("Status: Stopped")
            self.start_button.config(state="normal")
            
            # Re-enable spot selection
            self.update_spot_buttons()
    
    def on_closing(self):
        self.stop_bot()
        self.root.destroy()

# Create and run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = BotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()