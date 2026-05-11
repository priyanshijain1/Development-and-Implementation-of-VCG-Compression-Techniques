import tkinter as tk
from tkinter import ttk, messagebox
import wfdb
import numpy as np
import pywt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import GWO
import os

# Wavelet Compression & Decompression 
def wavelet_compress(data, wavelet='db4', level=3, threshold=0.1):
    coeffs = pywt.wavedec(data, wavelet, level=level)
    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], threshold, mode='hard')
    return coeffs

def wavelet_decompress(coeffs, wavelet='db4'):
    return pywt.waverec(coeffs, wavelet)


# Metrics Calculations
def compressionRatio(original_signal, compressed_coeffs):
    original_size = len(original_signal)
    non_zero_elements = sum(np.count_nonzero(c) for c in compressed_coeffs)
    
    if non_zero_elements == 0:
        return float('inf')
    return original_size / non_zero_elements

def mse(original, decompressed):
    return np.mean((original - decompressed) ** 2)

def psnr(original, decompressed):
    mse_val = mse(original, decompressed)
    return 20 * np.log10(np.max(np.abs(original)) / np.sqrt(mse_val)) if mse_val != 0 else float('inf')

def prd(original, decompressed):
    num = np.sum((original - decompressed) ** 2)
    den = np.sum(original ** 2)
    return np.sqrt(num / den) * 100


# GWO Optimization (Optimizes Threshold)
def gwo_optimize(data, wavelet, level=3):
    def obj_function(params):
        threshold = params[0]
        
        coeffs = wavelet_compress(data, wavelet=wavelet, level=level, threshold=threshold)
        decompressed = wavelet_decompress(coeffs, wavelet)
        compare_data = data
        
        if len(decompressed) > len(compare_data):
            decompressed = decompressed[:len(compare_data)]
        elif len(decompressed) < len(compare_data):
            compare_data = compare_data[:len(decompressed)]
            
        current_prd = prd(compare_data, decompressed)
        current_cr = compressionRatio(compare_data, coeffs)
        
        #Minimizing PRD (distortion) & maximizing CR
        fitness = (0.7 * current_prd) + (0.3 * (1 / current_cr))
        if current_prd > 5.0:
            fitness += 1000 
            
        return fitness

    lb, ub = [0.01], [1.5]
    dim, swarm_size, max_iter = 1, 10, 20
    result = GWO.GWO(obj_function, lb, ub, dim, swarm_size, max_iter)
    return result.bestIndividual[0] 

# Signal Processing 
def process_signal(file_path, signal_choice, wavelet):
    record_name, _ = os.path.splitext(file_path)
    hea_file = record_name + ".hea"
    dat_file = record_name + ".dat"

    if not os.path.exists(hea_file) or not os.path.exists(dat_file):
        messagebox.showerror("Error", f"Required .hea or .dat file not found: {hea_file}")
        return []

    try:
        record = wfdb.rdrecord(record_name)
        vcg_data = record.p_signal
        if vcg_data is None:
            messagebox.showerror("Error", "Invalid signal data in the file.")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
        return []

    components = {"VX": vcg_data[:, 0], "VY": vcg_data[:, 1], "VZ": vcg_data[:, 2]}
    results = []
    
    level = 3

    for name, signal in components.items():
        if signal_choice == name or signal_choice == "All":
            
            # 1. GWO finds the optimal threshold for this specific signal
            best_threshold = gwo_optimize(signal, wavelet=wavelet, level=level)
            
            # 2. Compress the signal using that threshold
            compressed_coeffs = wavelet_compress(signal, wavelet=wavelet, level=level, threshold=best_threshold)
            
            # 3. Decompress to check quality
            decompressed = wavelet_decompress(compressed_coeffs, wavelet=wavelet)
            
            if len(decompressed) > len(signal):
                decompressed = decompressed[:len(signal)]
            elif len(decompressed) < len(signal):
                signal = signal[:len(decompressed)]
            
            current_mse = mse(signal, decompressed)
            current_psnr = psnr(signal, decompressed)
            current_prd = prd(signal, decompressed)
            current_cr = compressionRatio(signal, compressed_coeffs)
            
            results.append((name, signal, decompressed, current_mse, current_psnr, current_prd, current_cr))

    return results

# GUI Result Handling
def on_result():
    file_index = file_menu.current()
    if file_index == -1:
        messagebox.showwarning("No File Selected", "Please select a file.")
        return

    file_path = file_paths[file_index]
    signal_choice = signal_var.get()
    wavelet = wavelet_var.get()

    result_button.config(text="Processing...", state="disabled")
    root.update()

    results = process_signal(file_path, signal_choice, wavelet)

    result_button.config(text="Result", state="normal")

    if not results:
        messagebox.showwarning("No Data", "No results to display.")
        return

    for widget in graph_frame.winfo_children():
        widget.destroy()

    fig, axs = plt.subplots(len(results), 1, figsize=(12, 8))
    fig.subplots_adjust(hspace=0.5)

    if len(results) == 1:
        axs = [axs]

    for idx, (name, original, decompressed, mse_val, psnr_val, prd_val, cr_val) in enumerate(results):
        axs[idx].plot(original[:500], label=f"Original {name}", alpha=0.7)
        axs[idx].plot(decompressed[:500], label=f"Decompressed {name}", linestyle='--', alpha=0.7)
        axs[idx].set_title(f"{name} Component (CR: {cr_val:.2f}, PRD: {prd_val:.2f}%, PSNR: {psnr_val:.2f} dB)", fontsize=12)
        axs[idx].legend()
        axs[idx].grid(True)

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

    for item in result_table.get_children():
        result_table.delete(item)

    for name, _, _, mse_val, psnr_val, prd_val, cr_val in results:
        result_table.insert("", "end", values=(name, f"{mse_val:.6f}", f"{psnr_val:.2f}", f"{prd_val:.2f}%", f"{cr_val:.2f}"))

# GUI Layout Setup
root = tk.Tk()
root.title("Wavelet-GWO VCG Signal Compression Tool")
root.geometry("1200x900")

file_paths = [
    r"/home/bhoomika/Desktop/PR/patient_1/s0010_re",
    r"/home/bhoomika/Desktop/PR/patient_2/s0014lre",
    r"/home/bhoomika/Desktop/PR/patient_3/s0016lre"
]
file_names = [os.path.basename(fp) for fp in file_paths]

control_frame = tk.Frame(root, padx=10, pady=10)
control_frame.grid(row=0, column=0, sticky="nsw")

tk.Label(control_frame, text="Select File:").grid(row=0, column=0, pady=5, sticky="w")
file_var = tk.StringVar()
file_menu = ttk.Combobox(control_frame, textvariable=file_var, values=file_names, state="readonly", width=30)
file_menu.grid(row=0, column=1, padx=5, pady=5)
file_menu.set(file_names[0]) 

tk.Label(control_frame, text="Select Signal Component:").grid(row=1, column=0, pady=5, sticky="w")
signal_var = tk.StringVar(value="All")
signal_menu = ttk.Combobox(control_frame, textvariable=signal_var, values=["VX", "VY", "VZ", "All"], state="readonly", width=30)
signal_menu.grid(row=1, column=1, padx=5, pady=5)

tk.Label(control_frame, text="Select Wavelet:").grid(row=2, column=0, pady=5, sticky="w")
wavelet_var = tk.StringVar(value="db4") # db4 is generally better for ECG/VCG than db2
wavelet_menu = ttk.Combobox(control_frame, textvariable=wavelet_var,
                             values=["db2", "db4", "db6", "db8", "db10", "sym4", "coif2"], state="readonly", width=30)
wavelet_menu.grid(row=2, column=1, padx=5, pady=5)

result_button = tk.Button(control_frame, text="Result", command=on_result, bg="lightblue", font=("Arial", 10, "bold"))
result_button.grid(row=3, column=0, columnspan=2, pady=20, ipadx=20)

graph_frame = tk.Frame(root, relief="ridge", borderwidth=2, bg="white")
graph_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

table_frame = tk.Frame(root, relief="ridge", borderwidth=2)
table_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0, 10))

# Updated Table Columns
columns = ("Signal", "MSE", "PSNR (dB)", "PRD (%)", "CR")
result_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=4)

for col in columns:
    result_table.heading(col, text=col)
    result_table.column(col, anchor="center", width=120)

result_table.pack(expand=True, fill="both")

# Ensure the window resizes nicely
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=3)
root.rowconfigure(1, weight=1)

root.mainloop()