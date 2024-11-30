# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 22:31:03 2023

@author: Zhipeng Yin
"""

from os import chdir
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def parse_peak_file(filename):
    peak_data = []
    temp_peaks = []
    current_scan = None

    with open(filename, 'r') as file:
        lines = file.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith('----------'):
                current_scan = int(line.strip('-'))
                for peak in temp_peaks:
                    peak['scan'] = current_scan
                    peak_data.append(peak)
                temp_peaks = []
            else:
                data = line.split()
                if len(data) == 6:
                    mz1, intensity1, mz2, intensity2, mz_diff, intensity_ratio = map(float, data)
                    temp_peaks.append({
                        'scan': None,
                        'mz1': mz1,
                        'intensity1': intensity1,
                        'mz2': mz2,
                        'intensity2': intensity2,
                        'mz_diff': mz_diff,
                        'intensity_ratio': intensity_ratio
                    })
    return peak_data

def group_peaks_by_mz(peak_data, mz_tolerance):
    grouped_peaks = defaultdict(list)
    for peak in peak_data:
        matched = False
        for mz_group in grouped_peaks:
            if abs(peak['mz1'] - mz_group) <= mz_tolerance:
                grouped_peaks[mz_group].append(peak)
                matched = True
                break
        if not matched:
            grouped_peaks[peak['mz1']].append(peak)
    return grouped_peaks

def calculate_noise_level(peak_data):
    num_scans1 = 2
    num_scans2 = 2
    noise_intensity = []
    for peak in peak_data[:num_scans1]:
        noise_intensity.append(peak['intensity1'])
    for peak in peak_data[-num_scans2:]:
        noise_intensity.append(peak['intensity1'])
    return sum(noise_intensity) / len(noise_intensity)

def calculate_sn_ratio(intensities, noise_level):
    sorted_intensities = sorted(intensities, reverse=True)
    max_intensity = (sorted_intensities[0] + sorted_intensities[1]) / 2
    return max_intensity / noise_level

def filter_groups(grouped_peaks, min_size, sn_threshold):
    filtered_peaks = {}
    for mz_group, peaks in grouped_peaks.items():
        if len(peaks) >= min_size:
            intensities = [peak['intensity1'] for peak in peaks]
            noise_level = calculate_noise_level(peaks)
            sn_ratio = calculate_sn_ratio(intensities, noise_level)
            if sn_ratio > sn_threshold:
                filtered_peaks[mz_group] = peaks
    return filtered_peaks

def plot_group(ax, mz_group, peaks, max_scan):
    ax.clear()
    max_intensity_peak = max(peaks, key=lambda x: x['intensity1'])
    mz_highest_intensity = max_intensity_peak['mz1']
    scans = [peak['scan'] for peak in peaks]
    intensity1 = [peak['intensity1'] for peak in peaks]
    intensity2 = [peak['intensity2'] for peak in peaks]
    
    ax.plot(scans, intensity1, label=f"m/z1 ~ {mz_highest_intensity:.6f}", marker='o')
    ax.plot(scans, intensity2, label="m/z2", marker='x')
    ax.set_xlabel("Scan Number")
    ax.set_ylabel("Intensity")
    ax.set_title(f"Intensity vs Scan Number - Group m/z1 ~ {mz_group:.6f}")
    ax.legend()
    ax.grid(True)
    ax.set_xlim(0, max_scan)
    
    canvas.draw()

def plot_groups(filtered_peaks, max_scan):
    global mz_groups, current_plot_index
    mz_groups = list(filtered_peaks.keys())
    current_plot_index.set(0)
    if mz_groups:
        plot_group(ax, mz_groups[0], filtered_peaks[mz_groups[0]], max_scan)

def browse_input_file():
    filename = filedialog.askopenfilename(title="Select Input File", filetypes=[("Text files", "*.txt")])
    entry_input_file.delete(0, tk.END)
    entry_input_file.insert(0, filename)

def browse_output_file():
    filename = filedialog.asksaveasfilename(title="Select Output File", defaultextension=".txt")
    entry_output_file.delete(0, tk.END)
    entry_output_file.insert(0, filename)

def browse_save_folder():
    folder = filedialog.askdirectory(title="Select Folder to Save Plots")
    entry_save_folder.delete(0, tk.END)
    entry_save_folder.insert(0, folder)

def on_start():
    global filtered_peaks, max_scan
    input_file = entry_input_file.get()
    output_file = entry_output_file.get()
    mz_tolerance = float(entry_mz_tolerance.get())
    sn_threshold = float(entry_sn_threshold.get())
    
    if input_file and output_file and mz_tolerance and sn_threshold:
        peak_data = parse_peak_file(input_file)
        grouped_peaks = group_peaks_by_mz(peak_data, mz_tolerance)
        filtered_peaks = filter_groups(grouped_peaks, min_size=5, sn_threshold=sn_threshold)
        max_scan = max(peak['scan'] for peak in peak_data)
        plot_groups(filtered_peaks, max_scan)
        
        result_list = pd.DataFrame(list(filtered_peaks.keys()), columns=['m/z'])
        result_list.to_csv(output_file, index=False)
        
        messagebox.showinfo("Success", "File processed successfully!")
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields.")

def plot_current_group():
    index = current_plot_index.get()
    mz_group = mz_groups[index]
    peaks = filtered_peaks[mz_group]
    plot_group(ax, mz_group, peaks, max_scan)

def next_plot():
    if current_plot_index.get() < len(mz_groups) - 1:
        current_plot_index.set(current_plot_index.get() + 1)
        plot_current_group()

def previous_plot():
    if current_plot_index.get() > 0:
        current_plot_index.set(current_plot_index.get() - 1)
        plot_current_group()

def save_all_plots():
    folder = entry_save_folder.get()
    if folder:
        for index, mz_group in enumerate(mz_groups):
            peaks = filtered_peaks[mz_group]
            fig, ax = plt.subplots(figsize=(12, 8))
            plot_group(ax, mz_group, peaks, max_scan)
            fig.savefig(f"{folder}/plot_{index + 1}.png")
            plt.close(fig)
        messagebox.showinfo("Success", "All plots saved successfully!")
    else:
        messagebox.showwarning("Input Error", "Please specify a folder to save the plots.")

# Create main window
app = tk.Tk()
app.title("LCMS Data Process 3")
app.geometry("600x750")
app.configure(bg="#e0e0e0")

style = ttk.Style(app)
style.theme_use("clam")
style.configure("TButton", padding=5, relief="flat", background="#333333", foreground="white", font=("Arial", 16))
style.configure("TLabel", background="#e0e0e0", font=("Arial", 16))
style.configure("TEntry", padding=5, font=("Arial", 16))

# Input fields and buttons
ttk.Label(app, text="Input File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_input_file = ttk.Entry(app, width=50)
entry_input_file.grid(row=0, column=1, padx=10, pady=10)
ttk.Button(app, text="Browse", command=browse_input_file).grid(row=0, column=2, padx=10, pady=10)

ttk.Label(app, text="Output File:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_output_file = ttk.Entry(app, width=50)
entry_output_file.grid(row=1, column=1, padx=10, pady=10)
ttk.Button(app, text="Browse", command=browse_output_file).grid(row=1, column=2, padx=10, pady=10)

ttk.Label(app, text="m/z Tolerance:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_mz_tolerance = ttk.Entry(app, width=50)
entry_mz_tolerance.grid(row=2, column=1, padx=10, pady=10)

ttk.Label(app, text="S/N Ratio Threshold:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
entry_sn_threshold = ttk.Entry(app, width=50)
entry_sn_threshold.grid(row=3, column=1, padx=10, pady=10)

ttk.Button(app, text="Start", command=on_start).grid(row=4, column=1, padx=10, pady=10)

ttk.Label(app, text="Save Plots Folder:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
entry_save_folder = ttk.Entry(app, width=50)
entry_save_folder.grid(row=5, column=1, padx=10, pady=10)
ttk.Button(app, text="Browse", command=browse_save_folder).grid(row=5, column=2, padx=10, pady=10)
ttk.Button(app, text="Save All Plots", command=save_all_plots).grid(row=6, column=1, padx=10, pady=10)

# Plot area
figure, ax = plt.subplots(figsize=(12, 8))
canvas = FigureCanvasTkAgg(figure, master=app)
canvas.get_tk_widget().grid(row=7, column=0, columnspan=3, padx=10, pady=10)

# Navigation buttons
current_plot_index = tk.IntVar(value=0)
ttk.Button(app, text="Previous", command=previous_plot).grid(row=8, column=0, padx=10, pady=10)
ttk.Button(app, text="Next", command=next_plot).grid(row=8, column=2, padx=10, pady=10)

app.mainloop()
