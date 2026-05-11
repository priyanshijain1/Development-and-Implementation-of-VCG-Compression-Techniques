import tkinter as tk
from tkinter import ttk, messagebox
import wfdb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.fftpack import fft, ifft

# Compression methods
def fft_compress(data, threshold_percentage):
    fft_signal = fft(data)
    magnitude_spectrum = np.abs(fft_signal)
    threshold = np.max(magnitude_spectrum) * (threshold_percentage / 100)
    mask = magnitude_spectrum > threshold
    compressed_fft = fft_signal * mask
    return compressed_fft, mask

def fft_decompress(compressed_fft):
    return np.real(ifft(compressed_fft))

# Metrics calculation
def calculate_metrics(original, compressed_fft, decompressed, mask):
    mse = np.mean((original - decompressed) ** 2)
    psnr = 20 * np.log10(np.max(np.abs(original)) / np.sqrt(mse)) if mse != 0 else float('inf')
    original_size = original.nbytes
    compressed_size = (np.sum(mask) * 2 * 8) + mask.nbytes
    cr = original_size / compressed_size
    return mse, psnr, cr

def process_signal(file_path, signal_choice, compression_method, threshold):
    try:
        record = wfdb.rdrecord(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
        return []

    vcg_data = record.p_signal
    vx, vy, vz = vcg_data[:, 0], vcg_data[:, 1], vcg_data[:, 2]
    components = {"VX": vx, "VY": vy, "VZ": vz}

    results = []
    for name, signal in components.items():
        if signal_choice == name or signal_choice == "All":
            if compression_method == "FFT":
                compressed, mask = fft_compress(signal, threshold)
                decompressed = fft_decompress(compressed)
                metrics = calculate_metrics(signal, compressed, decompressed, mask)
                results.append((name, signal, decompressed, metrics))
    return results

def on_result():
    file_index = file_menu.current()
    if file_index == -1:
        messagebox.showwarning("No File Selected", "Please select a file.")
        return

    file_path = file_paths[file_index]
    signal_choice = signal_var.get()
    compression_method = compression_method_var.get()
    try:
        threshold = float(threshold_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Threshold must be a number.")
        return

    results = process_signal(file_path, signal_choice, compression_method, threshold)

    if not results:
        messagebox.showwarning("No Data", "No results to display. Please check your selection.")
        return

    total_cr, total_mse, total_psnr = 0, 0, 0
    metrics_count = len(results)

    # Clear previous graph and metrics
    for widget in graph_frame.winfo_children():
        widget.destroy()

    for widget in metrics_frame.winfo_children():
        widget.destroy()

    fig, axs = plt.subplots(metrics_count, 1, figsize=(12, 8))
    fig.subplots_adjust(hspace=0.5)

    for idx, (name, original, decompressed, metrics) in enumerate(results):
        mse, psnr, cr = metrics
        total_mse += mse
        total_psnr += psnr
        total_cr += cr

        axs[idx].plot(original[:500], label=f"Original {name}", alpha=0.7)
        axs[idx].plot(decompressed[:500], label=f"Decompressed {name}", linestyle='--', alpha=0.7)
        axs[idx].set_title(f"{name} Component (MSE: {mse:.6f}, PSNR: {psnr:.2f} dB, CR: {cr:.2f})", fontsize=12)
        axs[idx].legend()
        axs[idx].grid(True)

    avg_mse = total_mse / metrics_count
    avg_psnr = total_psnr / metrics_count
    avg_cr = total_cr / metrics_count

    # Display graph
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

    # Display metrics in a styled box
    metrics_text = (
        f"Average Metrics Across VX, VY, VZ Components:\n\n"
        f"Average Compression Ratio (CR): {avg_cr:.2f}\n"
        f"Average Mean Squared Error (MSE): {avg_mse:.6f}\n"
        f"Average Peak Signal-to-Noise Ratio (PSNR): {avg_psnr:.2f} dB"
    )

    metrics_box = tk.Label(
        metrics_frame,
        text=metrics_text,
        justify="left",
        bg="wheat",
        font=("Arial", 14),
        relief="solid",
        wraplength=400,
        padx=15,
        pady=15,
    )
    metrics_box.pack(expand=True, fill="both", padx=10, pady=10)

# Tkinter GUI
root = tk.Tk()
root.title("VCG Signal Compression Tool")
root.geometry("1200x800")
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# File paths
file_paths = [
    r"/home/bhoomika/Desktop/PR/patient_1/s0010_re",
    r"/home/bhoomika/Desktop/PR/patient_2/s0014lre",
    r"/home/bhoomika/Desktop/PR/patient_3/s0016lre"
]
file_names = [fp.split("\\")[-1] for fp in file_paths]

# UI Components
control_frame = tk.Frame(root, padx=10, pady=10)
control_frame.grid(row=0, column=0, sticky="nsw")

file_label = tk.Label(control_frame, text="Select File:", font=("Arial", 12))
file_label.grid(row=0, column=0, sticky="w")
file_var = tk.StringVar()
file_menu = ttk.Combobox(control_frame, textvariable=file_var, values=file_names, state="readonly", width=30)
file_menu.grid(row=0, column=1, padx=5, pady=5)

signal_label = tk.Label(control_frame, text="Select Signal Component:", font=("Arial", 12))
signal_label.grid(row=1, column=0, sticky="w")
signal_var = tk.StringVar(value="All")
signal_menu = ttk.Combobox(control_frame, textvariable=signal_var, values=["VX", "VY", "VZ", "All"], state="readonly", width=30)
signal_menu.grid(row=1, column=1, padx=5, pady=5)

compression_label = tk.Label(control_frame, text="Compression Method:", font=("Arial", 12))
compression_label.grid(row=2, column=0, sticky="w")
compression_method_var = tk.StringVar(value="FFT")
compression_menu = ttk.Combobox(control_frame, textvariable=compression_method_var, values=["FFT"], state="readonly", width=30)
compression_menu.grid(row=2, column=1, padx=5, pady=5)

threshold_label = tk.Label(control_frame, text="Set Compression Threshold (%):", font=("Arial", 12))
threshold_label.grid(row=3, column=0, sticky="w")
threshold_entry = tk.Entry(control_frame, width=10)
threshold_entry.grid(row=3, column=1, padx=5, pady=5)

result_button = tk.Button(control_frame, text="Result", command=on_result, font=("Arial", 12), bg="lightblue")
result_button.grid(row=4, column=0, columnspan=2, pady=10)

# Metrics Frame under Result Button
metrics_frame = tk.Frame(control_frame, relief="ridge", borderwidth=2, bg="white")
metrics_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

# Graph Frame
graph_frame = tk.Frame(root, relief="ridge", borderwidth=2, bg="white")
graph_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

root.mainloop()