import os
import math
import csv
import threading
import time
from tqdm import tqdm
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, Toplevel, Scrollbar, filedialog, simpledialog, scrolledtext
from tkinter import ttk
import subprocess

# Memoization cache for previously checked primes
prime_cache = {}

# Global variables for controlling the prime number generation thread
prime_thread = None
stop_prime_generation = False
generated_primes = []
start_time = None
time_remaining_label = None  # Label to show time remaining

# Create logs folder if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create reports folder if it doesn't exist
if not os.path.exists('reports'):
    os.makedirs('reports')

# Function to check if a number is prime
def is_prime(num):
    if num in prime_cache:
        return prime_cache[num]

    if num <= 1:
        prime_cache[num] = False
        return False
    elif num == 2:
        prime_cache[num] = True
        return True
    elif num % 2 == 0:
        prime_cache[num] = False
        return False

    for i in range(3, int(math.sqrt(num)) + 1, 2):
        if num % i == 0:
            prime_cache[num] = False
            return False

    prime_cache[num] = True
    return True

# Function to generate all prime numbers up to a given limit
def generate_primes_up_to(n, progress_callback=None, count_callback=None, time_callback=None):
    primes = []
    for i in tqdm(range(2, n + 1), desc="Generating primes", unit="number", ncols=100):
        if stop_prime_generation:
            return primes
        if is_prime(i):
            primes.append(i)
        if progress_callback:
            progress_callback(i, n)  # Update progress
        if count_callback:
            count_callback(len(primes))  # Update prime count
        if time_callback:
            time_callback(i, n)  # Estimate time remaining
    return primes

# Function to generate a timestamped filename for CSV or PDF
def get_timestamped_filename(base_name, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"

# Function to export primes to a CSV file
def export_to_csv(primes):
    try:
        filename = get_timestamped_filename("primes", ".csv")
        filepath = os.path.join('reports', filename)

        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Prime Numbers"])
            for prime in primes:
                writer.writerow([prime])
        return filepath
    except Exception as e:
        return None

# Function to export primes to a PDF file in table format
def export_to_pdf(primes):
    try:
        filename = get_timestamped_filename("primes", ".pdf")
        filepath = os.path.join('reports', filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        data = [["Prime Numbers"]]
        for prime in primes:
            data.append([str(prime)])

        table = Table(data)
        table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))

        doc.build([table])
        return filepath
    except Exception as e:
        return None

# Function to update progress bar and live prime count
def update_progress(current, total):
    progress.set((current / total) * 100)
    progress_label.config(text=f"Progress: {int((current / total) * 100)}%")

# Update live count of prime numbers found
def update_prime_count(count):
    prime_count_label.config(text=f"Prime Count: {count}")

# Estimate and update time remaining
def update_time_remaining(current, total):
    if current > 1:
        elapsed_time = time.time() - start_time
        estimated_total_time = (elapsed_time / current) * total
        time_remaining = estimated_total_time - elapsed_time
        minutes, seconds = divmod(time_remaining, 60)
        time_remaining_label.config(text=f"Time Remaining: {int(minutes)}m {int(seconds)}s")
    else:
        time_remaining_label.config(text="Time Remaining: Calculating...")

# Function to check if a number is prime (GUI part)
def check_prime():
    try:
        num = int(entry_number.get())
        if num <= 1:
            result_label.config(text=f"{num} is Not a Prime Number")
        elif is_prime(num):
            result_label.config(text=f"{num} is a Prime Number")
        else:
            result_label.config(text=f"{num} is Not a Prime Number")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# Function to generate and display primes up to a limit (GUI part)
def generate_primes():
    global prime_thread, stop_prime_generation, generated_primes, start_time
    try:
        limit = int(entry_limit.get())

        # Prevent starting a new process if one is already running
        if prime_thread and prime_thread.is_alive():
            messagebox.showwarning("Process Running", "Prime number generation is already running. Please wait for it to complete.")
            return

        # Disable the "Generate Primes" button during the process
        button_generate.config(state=tk.DISABLED)
        button_export_csv.config(state=tk.DISABLED)
        button_export_pdf.config(state=tk.DISABLED)
        stop_prime_generation = False

        # Start the timer for time remaining calculation
        start_time = time.time()
        result_label.config(text="Generating primes... please wait.")
        progress_bar.start()

        # Start the prime generation in a separate thread to prevent blocking the GUI
        prime_thread = threading.Thread(target=run_prime_generation, args=(limit,))
        prime_thread.start()

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# Function to run prime generation in the background
def run_prime_generation(limit):
    global generated_primes
    primes = generate_primes_up_to(limit, progress_callback=update_progress, count_callback=update_prime_count, time_callback=update_time_remaining)
    generated_primes = primes

    # After prime generation, update the GUI
    result_label.config(text=f"Prime numbers up to {limit}: {primes[:10]}...")  # Show first 10 primes
    progress_bar.stop()

    # Log the prime generation request
    log_prime_request(limit, len(primes))

    # Re-enable the "Generate Primes" button and reset the UI
    button_generate.config(state=tk.NORMAL)
    button_export_csv.config(state=tk.NORMAL)
    button_export_pdf.config(state=tk.NORMAL)
    time_remaining_label.config(text="Time Remaining: Done")
    progress.set(100)

# Function to log the prime generation request
def log_prime_request(limit, prime_count):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Requested Prime Generation Limit: {limit}, Generated Prime Count: {prime_count}, Date and Time: {timestamp}\n"
    
    log_filename = os.path.join("logs", "prime_generation_log.txt")
    with open(log_filename, "a") as log_file:
        log_file.write(log_entry)  # Each entry is added to a new line

# Function to export primes to CSV (GUI part)
def export_csv():
    if 'generated_primes' in globals():
        filepath = export_to_csv(generated_primes)
        if filepath:
            messagebox.showinfo("Export Successful", f"Prime numbers have been saved to {filepath}.")
        else:
            messagebox.showerror("Export Failed", "An error occurred while saving the file.")
    else:
        messagebox.showwarning("No Primes Generated", "Please generate prime numbers first.")

# Function to export primes to PDF (GUI part)
def export_pdf():
    if 'generated_primes' in globals():
        filepath = export_to_pdf(generated_primes)
        if filepath:
            messagebox.showinfo("Export Successful", f"Prime numbers have been saved to {filepath}.")
        else:
            messagebox.showerror("Export Failed", "An error occurred while saving the file.")
    else:
        messagebox.showwarning("No Primes Generated", "Please generate prime numbers first.")

# Function to show all the generated prime numbers in a new window
def list_reports():
    top = Toplevel(root)
    top.title("Generated Reports")

    report_listbox = tk.Listbox(top, width=100, height=20)
    report_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = Scrollbar(top, orient="vertical", command=report_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    report_listbox.config(yscrollcommand=scrollbar.set)

    reports_folder = 'reports'
    reports = [f for f in os.listdir(reports_folder) if f.endswith(('.csv', '.pdf'))]
    for report in reports:
        report_listbox.insert(tk.END, report)

    # Open the selected report
    def open_report():
        selected_report = report_listbox.get(report_listbox.curselection())
        report_path = os.path.join(reports_folder, selected_report)
        os.startfile(report_path)

    # Open button
    open_button = tk.Button(top, text="Open Report", command=open_report)
    open_button.pack(pady=10)

    # Delete button to remove selected report
    def delete_report():
        selected_report = report_listbox.get(report_listbox.curselection())
        report_path = os.path.join(reports_folder, selected_report)
        try:
            os.remove(report_path)
            report_listbox.delete(report_listbox.curselection())
            messagebox.showinfo("Success", "Report deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete report: {e}")

    delete_button = tk.Button(top, text="Delete Report", command=delete_report)
    delete_button.pack(pady=10)

# Function to show logs in a new window
# Function to show logs in a new window
def view_logs():
    top = Toplevel(root)
    top.title("Logs")

    # Create a resizable text box with scroll bar
    log_text = tk.Text(top, wrap=tk.WORD, height=20, width=80)
    log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)  # Allow expansion and resizing

    scrollbar = Scrollbar(top, orient="vertical", command=log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    log_text.config(yscrollcommand=scrollbar.set)

    # Open the log file and display the contents in the text box
    log_filename = os.path.join("logs", "prime_generation_log.txt")
    if os.path.exists(log_filename):
        with open(log_filename, "r") as log_file:
            logs = log_file.read()
        log_text.insert(tk.END, logs)

    # Make the window resizable
    top.grid_rowconfigure(0, weight=1)
    top.grid_columnconfigure(0, weight=1)

# Function to view generated prime numbers
def view_generated_primes():
    # Create a new window to display the generated prime numbers
    view_window = tk.Toplevel(root)
    view_window.title("Generated Prime Numbers")

    # Create a scrollable text area to display the prime numbers
    prime_text = scrolledtext.ScrolledText(view_window, width=50, height=20, wrap=tk.WORD, font=("Arial", 12))
    prime_text.pack(padx=10, pady=10)

    # Insert the generated prime numbers into the text area
    if generated_primes:  # Check if there are generated primes
        prime_text.insert(tk.END, "\n".join(map(str, generated_primes)))
    else:
        prime_text.insert(tk.END, "No prime numbers generated yet. Please generate prime numbers first.")

    # Disable editing in the text area
    prime_text.config(state=tk.DISABLED)


# Function to delete logs and reports
def delete_all_data():
    # Prompt for password before proceeding with deletion
    password = simpledialog.askstring("Password", "Enter the password to delete data:")

    if password != "Prime@123":
        messagebox.showerror("Incorrect Password", "The password you entered is incorrect.")
        return

    # Create a new window with checkboxes for deletion options
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Data Options")

    # Create checkboxes for logs and reports deletion
    var_logs = tk.BooleanVar()
    var_reports = tk.BooleanVar()

    checkbox_logs = tk.Checkbutton(delete_window, text="All Logs", variable=var_logs, font=("Arial", 12))
    checkbox_logs.pack(padx=10, pady=5)

    checkbox_reports = tk.Checkbutton(delete_window, text="All Reports", variable=var_reports, font=("Arial", 12))
    checkbox_reports.pack(padx=10, pady=5)

    # Delete button to confirm deletion
    delete_button = tk.Button(delete_window, text="Delete Permanently", font=("Arial", 12), bg="lightcoral", fg="black",
                               command=lambda: confirm_delete(var_logs.get(), var_reports.get(), delete_window))
    delete_button.pack(padx=10, pady=10)

# Function to confirm deletion and delete based on checkbox options
def confirm_delete(delete_logs_option, delete_reports_option, window):
    if not delete_logs_option and not delete_reports_option:
        messagebox.showwarning("No Data Selected", "Please select at least one option (logs or reports) to delete.")
        return
    
    # If "All Logs" checkbox is selected
    if delete_logs_option:
        delete_logs()

    # If "All Reports" checkbox is selected
    if delete_reports_option:
        delete_reports()

    messagebox.showinfo("Deletion Successful", "Selected data has been deleted permanently.")
    
    # Close the deletion window after completion
    window.destroy()

# Function to delete logs
def delete_logs():
    logs_folder = "logs"
    if os.path.exists(logs_folder):
        for filename in os.listdir(logs_folder):
            file_path = os.path.join(logs_folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error Deleting Log", f"Error deleting log file {filename}: {e}")
    else:
        messagebox.showwarning("No Logs Found", "No logs found to delete.")

# Function to delete reports
def delete_reports():
    reports_folder = "reports"
    if os.path.exists(reports_folder):
        for filename in os.listdir(reports_folder):
            file_path = os.path.join(reports_folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error Deleting Report", f"Error deleting report file {filename}: {e}")
    else:
        messagebox.showwarning("No Reports Found", "No reports found to delete.")

# Add the "Delete All Data" button to the main window
def add_delete_data_button(root):
    delete_button = tk.Button(root, text="Delete All Data", command=delete_all_data, font=("Arial", 12), bg="lightcoral", fg="black")
    delete_button.grid(row=9, column=0, columnspan=3, pady=10)

# Add the "View Generated Prime Numbers" button to the main window
def add_view_primes_button(root):
    view_button = tk.Button(root, text="View Generated Prime Numbers", command=view_generated_primes, font=("Arial", 12), bg="lightgreen", fg="black")
    view_button.grid(row=10, column=0, columnspan=3, pady=10)

# Main GUI setup
root = tk.Tk()
root.title("Prime Number Generator")

# Set the font and size for all widgets
font_style = ("Arial", 12)

# Check Prime
label_number = tk.Label(root, text="Enter a number to check prime:", font=font_style)
label_number.grid(row=0, column=0, pady=5)
entry_number = tk.Entry(root, font=font_style)
entry_number.grid(row=0, column=1, pady=5)
button_check = tk.Button(root, text="Check Prime", command=check_prime, font=font_style, bg='lightblue', fg='black')
button_check.grid(row=0, column=2, padx=5, pady=5)

# Result label for prime check
result_label = tk.Label(root, text="", font=font_style)
result_label.grid(row=1, column=0, pady=10, columnspan=3)

# Input for generating primes up to a limit
label_limit = tk.Label(root, text="Enter a limit to generate primes:", font=font_style)
label_limit.grid(row=2, column=0, pady=5)
entry_limit = tk.Entry(root, font=font_style)
entry_limit.grid(row=2, column=1, pady=5)

# Progress bar and labels
progress = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress, maximum=100)
progress_bar.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

progress_label = tk.Label(root, text="Progress: 0%", font=font_style)
progress_label.grid(row=4, column=0, columnspan=3)

time_remaining_label = tk.Label(root, text="Time Remaining: Calculating...", font=font_style)
time_remaining_label.grid(row=5, column=0, columnspan=3)

prime_count_label = tk.Label(root, text="Prime Count: 0", font=font_style)
prime_count_label.grid(row=6, column=0, columnspan=3)

# Buttons to generate primes, export data, and view reports
button_generate = tk.Button(root, text="Generate Primes", command=generate_primes, font=font_style, bg='lightgreen', fg='black')
button_generate.grid(row=7, column=0, padx=5, pady=5)

button_export_csv = tk.Button(root, text="Export to CSV", command=export_csv, font=font_style, bg='lightblue', fg='black')
button_export_csv.grid(row=7, column=1, padx=5, pady=5)

button_export_pdf = tk.Button(root, text="Export to PDF", command=export_pdf, font=font_style, bg='lightblue', fg='black')
button_export_pdf.grid(row=7, column=2, padx=5, pady=5)

# Buttons to view logs and reports
button_view_logs = tk.Button(root, text="View Logs", command=view_logs, font=font_style, bg='lightblue', fg='black')
button_view_logs.grid(row=8, column=0, padx=5, pady=5)

button_view_reports = tk.Button(root, text="View Reports", command=list_reports, font=font_style, bg='lightblue', fg='black')
button_view_reports.grid(row=8, column=1, padx=5, pady=5)

# Add the "Delete All Data" button to the interface
add_delete_data_button(root)

# Add the "View Generated Prime Numbers" button
add_view_primes_button(root)

root.mainloop()
