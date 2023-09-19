import tkinter as tk
from tkinter import filedialog,messagebox  
import csv
from tkinter import ttk

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        # Clear the previous table content, if any
        clear_table()
        
        # Read and display the CSV content in the table
        read_csv(file_path)

def clear_table():
    for row in table.get_children():
        table.delete(row)

def read_csv(file_path):
    try:
        with open(file_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            
            # If the table doesn't have columns yet, set them based on the CSV header
            if not table["columns"]:
                table["columns"] = header
                for col in header:
                    table.heading(col, text=col)
                    table.column(col, width=100)
            
            # Populate the table with CSV data
            for row_data in reader:
                table.insert("", "end", values=row_data)
    except FileNotFoundError:
        print("File not found.")
    except csv.Error as e:
        error_message = f"CSV Error: {e}"
        print(error_message)
        messagebox.showerror("CSV Error", error_message)
        clear_table()  # Clear the table if there's an error


def save_file():
    if table.get_children():
 
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode="w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write CSV header
                    header = [table.heading(col)["text"] for col in table["columns"]]
                    writer.writerow(header)
                    
                    # Write CSV data
                    for item in table.get_children():
                        row_data = [table.item(item, "values")[i] for i in range(len(header))]
                        writer.writerow(row_data)
            except csv.Error as e:
                print(f"CSV Error: {e}")
    else:
               messagebox.showinfo("No Data", "No data to save. Please upload a CSV file.")  # Show a message box


# Create the main application window
root = tk.Tk()
root.geometry("350x450")
root.title("CSV File Reader")

# Create a label
label = tk.Label(root, text="CSV File Reader", font=("Arial", 16))
label.pack(pady=10)

 
upload_button = tk.Button(root, text="Upload Soil CSV", command=open_file)
upload_button.pack(pady=5)
 
upload_button2 = tk.Button(root, text="Upload Chemical CSV", command=open_file)
upload_button2.pack(pady=5)
 
clear_button = tk.Button(root, text="Clear", command=clear_table)
clear_button.pack(pady=5)

# Create a frame for the table to make it 800x800
table_frame = tk.Frame(root, width=800, height=800)
table_frame.pack(padx=3, pady=3)

# Create a table to display CSV content within the frame
table = ttk.Treeview(table_frame, show="headings")   
 
table["columns"] = ("Email" ) 
table.heading("Email", text="Email")   
 
upload_button3 = tk.Button(root, text="Save CSV", command=save_file)
upload_button3.pack(pady=5)

table.pack(fill="both", expand=True)

# Start the Tkinter main loop
root.mainloop()
