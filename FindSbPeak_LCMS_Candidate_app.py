import pandas as pd
import numpy as np
from pyteomics import mzml
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def MS_identifier(mzdata, chg, dev):
    data = mzdata.values
    mz_num = data.shape[0]
    tdelta = 2.000398 / chg
    minimass = 121.0 / chg
    candidates = {}

    for mz_i in range(mz_num):
        for mz_j in range(mz_i, mz_num):
            mdelta = round(data[mz_j, 0] - data[mz_i, 0], 6)
            iratio = round(data[mz_j, 1] / data[mz_i, 1], 3)
            just1 = abs(mdelta - tdelta) <= dev
            just2 = data[mz_i, 0] > minimass
            just3 = abs(iratio - 0.75) <= 0.35
            just4=abs(round(data[mz_i,0])-data[mz_i,0])<=0.20
            just5 = data[mz_i, 1] > 100000

            if just1 and just2 and just3 and just4 and just5:
                temp = [
                    str(data[mz_i, 0]),
                    str(int(data[mz_i, 1])),
                    str(data[mz_j, 0]),
                    str(int(data[mz_j, 1])),
                    str(mdelta),
                    str(iratio)
                ]
                candidates[data[mz_i, 0]] = temp

    return sorted(candidates.items(), key=lambda d: d[0])

def process_spectrum(spectrum_data, chg, dev):
    mz = pd.DataFrame(spectrum_data["m/z array"], columns=["mz"])
    intensity = pd.DataFrame(spectrum_data["intensity array"], columns=["intensity"])
    mzdata = pd.concat([mz, intensity], axis=1)
    return MS_identifier(mzdata, chg, dev)

def process_mzml_file(input_file, output_file, chg, dev, start, end, update_progress):
    data = mzml.read(input_file)
    spectra = list(data)

    if end is None:
        end = len(spectra)
    spectra = spectra[start:end]
    total_spectra = len(spectra)

    with open(output_file, "a") as output:
        for i, spectrum in enumerate(spectra, start=1):
            candidates = process_spectrum(spectrum, chg, dev)
            for can_i in candidates:
                line = "    ".join(can_i[1])
                output.write(line + "\n")
            output.write(f"----------{i + start}-------------\n")

            # Update progress
            update_progress(i, total_spectra)

def run_program(input_file, output_file, chg, dev, start, end):
    try:
        process_mzml_file(
            input_file, output_file, chg, dev, start, end,
            update_progress=update_progress
        )
        messagebox.showinfo("Success", "Processing completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_input_file():
    filename = filedialog.askopenfilename(title="Select Input mzML File", filetypes=[("mzML files", "*.mzML")])
    entry_input_file.delete(0, tk.END)
    entry_input_file.insert(0, filename)
    if filename:
        update_file_info(filename)

def browse_output_file():
    filename = filedialog.asksaveasfilename(title="Select Output File", defaultextension=".txt")
    entry_output_file.delete(0, tk.END)
    entry_output_file.insert(0, filename)

def update_file_info(file_path):
    try:
        spectra = list(mzml.read(file_path))
        total_spectra = len(spectra)
        acquisition_time = spectra[-1].get('scanList', {}).get('scan', [{}])[0].get('startTime', "Unknown")
        label_file_info.config(
            text=f"Spectra: {total_spectra} | Last Acquisition Time: {acquisition_time}"
        )
    except Exception as e:
        label_file_info.config(text="Error reading file: " + str(e))

def on_start():
    input_file = entry_input_file.get()
    output_file = entry_output_file.get()
    chg = int(entry_charge.get())
    dev = float(entry_deviation.get())
    start = int(entry_start.get())
    end = entry_end.get()
    end = int(end) if end else None

    if input_file and output_file and chg and dev is not None and start is not None:
        # Reset progress bar to 0 before starting
        progress_bar["value"] = 0
        progress_bar.update()

        # Run the processing directly without threading
        run_program(input_file, output_file, chg, dev, start, end)
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields.")

def update_progress(current, total):
    # Calculate progress percentage and update the progress bar
    progress = (current / total) * 100
    progress_bar["value"] = progress
    progress_bar.update_idletasks()

# Set up the main window
app = tk.Tk()
app.title("LCMS Data Process 1")
app.geometry("500x450")
app.configure(bg="#e0e0e0")

# Custom style with larger font and compact layout
style = ttk.Style(app)
style.theme_use("clam")
style.configure("TButton", padding=3, relief="flat", background="#333333", foreground="white", font=("Arial", 10))
style.configure("TLabel", background="#e0e0e0", font=("Arial", 10))
style.configure("TEntry", padding=3, font=("Arial", 10))

# Layout setup
ttk.Label(app, text="Input mzML File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
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

ttk.Label(app, text="Start Spectrum Index:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
entry_start = ttk.Entry(app, width=20)
entry_start.grid(row=4, column=1, padx=5, pady=5, sticky="w")

ttk.Label(app, text="End Spectrum Index:").grid(row=5, column=0, padx=5, sticky="e")
entry_end = ttk.Entry(app, width=20)
entry_end.grid(row=5, column=1, padx=5, pady=5, sticky="w")

# File info label
label_file_info = ttk.Label(app, text="Spectra: 0 | Last Acquisition Time: N/A")
label_file_info.grid(row=6, column=0, columnspan=3, pady=5)

# Start button
ttk.Button(app, text="Start Processing", command=on_start).grid(row=7, column=0, columnspan=3, pady=10)

# Progress bar at the bottom of the window
progress_bar = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

app.mainloop()
