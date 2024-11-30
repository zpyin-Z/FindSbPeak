# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 08:52:01 2021

@author: Zhipeng Yin
"""

from os import chdir
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def process_file(input_file, output_file, deviation):
    try:
        with open(input_file, "r") as data, open(output_file, "a") as outputlite:
            lines = data.readlines()
            for f in lines:
                line0 = f
                if line0.startswith("-"):
                    outputlite.write(line0)
                else:
                    line = line0.split("    ")
                    x = float(line[4])
                    xr = abs(2.000398 - x)
                    if xr <= deviation:
                        outputlite.write(line0)
        messagebox.showinfo("Success", "File processed successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_input_file():
    filename = filedialog.askopenfilename(title="Select Input File", filetypes=[("Text files", "*.txt")])
    entry_input_file.delete(0, tk.END)
    entry_input_file.insert(0, filename)

def browse_output_file():
    filename = filedialog.asksaveasfilename(title="Select Output File", defaultextension=".txt")
    entry_output_file.delete(0, tk.END)
    entry_output_file.insert(0, filename)

def on_start():
    input_file = entry_input_file.get()
    output_file = entry_output_file.get()
    deviation = float(entry_deviation.get())
    
    if input_file and output_file and deviation is not None:
        process_file(input_file, output_file, deviation)
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields.")

# Create main window
app = tk.Tk()
app.title("LCMS Data Process 2")
app.geometry("500x200")
app.configure(bg="#e0e0e0")

# Style customization
style = ttk.Style(app)
style.theme_use("clam")
style.configure("TButton", padding=5, relief="flat", background="#333333", foreground="white", font=("Arial", 10))
style.configure("TLabel", background="#e0e0e0", font=("Arial", 10))
style.configure("TEntry", padding=5, font=("Arial", 10))

# Layout configuration
ttk.Label(app, text="Input File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_input_file = ttk.Entry(app, width=50)
entry_input_file.grid(row=0, column=1, padx=10, pady=10)
ttk.Button(app, text="Browse", command=browse_input_file).grid(row=0, column=2, padx=10, pady=10)

ttk.Label(app, text="Output File:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_output_file = ttk.Entry(app, width=50)
entry_output_file.grid(row=1, column=1, padx=10, pady=10)
ttk.Button(app, text="Browse", command=browse_output_file).grid(row=1, column=2, padx=10, pady=10)

ttk.Label(app, text="Deviation:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_deviation = ttk.Entry(app, width=50)
entry_deviation.grid(row=2, column=1, padx=10, pady=10)

ttk.Button(app, text="Start", command=on_start).grid(row=3, column=0, columnspan=3, padx=10, pady=20)

# Run the application
app.mainloop()
