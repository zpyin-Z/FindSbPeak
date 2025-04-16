# -*- coding: utf-8 -*-
"""
FT-ICR MS Data Processor - Compact and Neutral-Themed GUI
Refined layout with larger font, reduced padding, and neutral color scheme.
"""

import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Mass spectrometry data identifier function
def MS_identifier(ifile, chg, dev, ofile):
    data = pd.read_table(ifile, sep='\t').values
    mz_num = data.shape[0]
    tdelta = 2.000398 / chg
    minimass = 121.0 / chg
    candidates = {}
    for mz_i in range(mz_num):
        for mz_j in range(mz_i, mz_num):
            mdelta = round(data[mz_j, 0] - data[mz_i, 0], 6)
            iratio = round(data[mz_j, 1] / data[mz_i, 1], 3)
            just4=abs(round(data[mz_i,0])-data[mz_i,0])<=0.20
            if abs(mdelta - tdelta) <= dev and data[mz_i, 0] > minimass and abs(iratio - 0.75) <= 0.25 and just4:
                candidates[data[mz_i, 0]] = [str(data[mz_i, 0]), str(int(data[mz_i, 1])),
                                             str(data[mz_j, 0]), str(int(data[mz_j, 1])),
                                             str(mdelta), str(iratio)]
    with open(ofile, "w") as output:
        for _, values in sorted(candidates.items()):
            output.write("    ".join(values) + "\n")
    print("Processing complete.")

# Program runner with error handling
def run_program(ifile, chg, dev, ofile):
    try:
        MS_identifier(ifile, chg, dev, ofile)
        messagebox.showinfo("Success", "Processing completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Functions to browse files and insert paths into the entry fields
def browse_input_file():
    filename = filedialog.askopenfilename(title="Select Input File")
    if filename:
        entry_input_file.delete(0, tk.END)
        entry_input_file.insert(0, filename)

def browse_output_file():
    filename = filedialog.asksaveasfilename(title="Select Output File", defaultextension=".txt")
    if filename:
        entry_output_file.delete(0, tk.END)
        entry_output_file.insert(0, filename)

# Main window setup and widget configuration
app = tk.Tk()
app.title("MS Data Process")
app.geometry("450x220")
app.configure(bg="#e0e0e0")

# Custom style with larger font and compact layout
style = ttk.Style(app)
style.theme_use("clam")
style.configure("TButton", padding=3, relief="flat", background="#333333", foreground="white", font=("Arial", 10))
style.configure("TLabel", background="#e0e0e0", font=("Arial", 10))
style.configure("TEntry", padding=3, font=("Arial", 10))

# GUI Layout
ttk.Label(app, text="Input File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_input_file = ttk.Entry(app, width=40)
entry_input_file.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(app, text="Browse", command=browse_input_file).grid(row=0, column=2, padx=5, pady=5)

ttk.Label(app, text="Output File:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_output_file = ttk.Entry(app, width=40)
entry_output_file.grid(row=1, column=1, padx=5, pady=5)
ttk.Button(app, text="Browse", command=browse_output_file).grid(row=1, column=2, padx=5, pady=5)

ttk.Label(app, text="Charge:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_charge = ttk.Entry(app, width=20)
entry_charge.grid(row=2, column=1, padx=5, pady=5, sticky="w")

ttk.Label(app, text="Deviation:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
entry_deviation = ttk.Entry(app, width=20)
entry_deviation.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Start button with centralized placement
ttk.Button(app, text="Start Processing", command=lambda: run_program(
    entry_input_file.get(),
    int(entry_charge.get() or 1),  # Default to 1 if empty
    float(entry_deviation.get() or 0.1),  # Default to 0.1 if empty
    entry_output_file.get())
).grid(row=4, column=0, columnspan=3, pady=10)

app.mainloop()
