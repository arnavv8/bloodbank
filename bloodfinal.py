import tkinter as tk
import tkinter.ttk as ttk
import mysql.connector


# Function to add donor data to the database
def add_donor():
    name = name_entry.get()
    blood_group = blood_group_var.get()
    contact = contact_entry.get()
    selected_blood_bank = blood_bank_var.get()

    # Retrieve the 'blood_bank_id' from the selected blood bank
    cursor.execute("SELECT id FROM blood_banks WHERE name = %s", (selected_blood_bank,))
    blood_bank_id = cursor.fetchone()[0]

    # Check if the donor already exists in the database (by name and contact)
    check_query = "SELECT * FROM donors WHERE name = %s AND contact = %s"
    cursor.execute(check_query, (name, contact))
    existing_donor = cursor.fetchone()

    if existing_donor:
        # Donor already exists, show an error message
        error_label.config(text="Donor with the same name and contact already exists!", fg="red")
    else:
        # Insert data into the 'donors' table
        insert_query = "INSERT INTO donors (name, blood_group, contact, blood_bank_id) VALUES (%s, %s, %s, %s)"
        values = (name, blood_group, contact, blood_bank_id)

        cursor.execute(insert_query, values)
        db.commit()

        # Clear the entered data
        name_entry.delete(0, tk.END)
        contact_entry.delete(0, tk.END)
        blood_bank_dropdown.set(blood_banks[0])
        blood_group_dropdown.set(blood_groups[0])

        error_label.config(text="")  # Clear any previous error message


# Function to delete a donor from the database
def delete_donor():
    selected_item = display_tree.focus()
    if selected_item:
        # Get the donor ID from the selected item in the Treeview
        donor_id = display_tree.item(selected_item, "values")[0]
        delete_query = "DELETE FROM donors WHERE id = %s"
        cursor.execute(delete_query, (donor_id,))
        db.commit()
        retrieve_donors()  # Refresh the displayed donor list
    else:
        error_label.config(text="Please select a donor to delete.", fg="red")


# Function to retrieve donors' data from the database based on selected criteria
def retrieve_donors():
    criteria = criteria_var.get()
    search_query = "SELECT donors.id, donors.name, donors.blood_group, donors.contact, blood_banks.name " \
                   "FROM donors INNER JOIN blood_banks ON donors.blood_bank_id = blood_banks.id " \
                   "WHERE donors.name LIKE %s OR donors.blood_group LIKE %s"
    search_term = f"%{criteria}%"

    cursor.execute(search_query, (search_term, search_term))
    donors_data = cursor.fetchall()

    # Clear the previous data in the Treeview
    display_tree.delete(*display_tree.get_children())

    for donor in donors_data:
        display_tree.insert("", tk.END, values=donor)


# Connect to the MySQL server and create a cursor object
db = mysql.connector.connect(
    host="localhost",
    user="youruser",
    password="password",
    database="database"
)
cursor = db.cursor()


# Add blood groups to the 'blood_groups' table
blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Create the 'blood_banks' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS blood_banks (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL
)
""")

# Create the 'donors' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    blood_group VARCHAR(3) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    blood_bank_id INT NOT NULL,
    FOREIGN KEY (blood_bank_id) REFERENCES blood_banks(id)
)
""")

# Create the main tkinter window
root = tk.Tk()
root.title("Blood Bank Management System")

# Styling options
bg_color = "#f0f0f0"
font_style = ("Helvetica", 12)

root.configure(bg=bg_color)

# Create labels and entry widgets for user input
name_label = tk.Label(root, text="Name:", bg=bg_color, font=font_style)
name_label.pack()
name_entry = tk.Entry(root, font=font_style)
name_entry.pack()

blood_group_label = tk.Label(root, text="Select Blood Group:", bg=bg_color, font=font_style)
blood_group_label.pack()
blood_group_var = tk.StringVar(root)
blood_group_var.set(blood_groups[0])  # Set a default value
blood_group_dropdown = ttk.Combobox(root, textvariable=blood_group_var, values=blood_groups)
blood_group_dropdown.pack(pady=10)

contact_label = tk.Label(root, text="Contact:", bg=bg_color, font=font_style)
contact_label.pack()
contact_entry = tk.Entry(root, font=font_style)
contact_entry.pack()

# Create a dropdown menu to select the blood bank for the donor
blood_bank_label = tk.Label(root, text="Select Blood Bank:", bg=bg_color, font=font_style)
blood_bank_label.pack()
blood_bank_var = tk.StringVar(root)
blood_bank_var.set("Blood Bank 1")  # Set a default value
blood_banks = ["Blood Bank 1", "Blood Bank 2", "Blood Bank 3"]  # Add your blood banks here
blood_bank_dropdown = ttk.Combobox(root, textvariable=blood_bank_var, values=blood_banks)
blood_bank_dropdown.pack(pady=10)

# Create a button to add donors to the database
add_button = tk.Button(root, text="Add Donor", bg="#4CAF50", fg="white", font=font_style, command=add_donor)
add_button.pack(pady=10)

# Create a dropdown menu to select criteria for donor retrieval
criteria_var = tk.StringVar(root)
criteria_var.set("")
criteria_label = tk.Label(root, text="Search by Name or Blood Group:", bg=bg_color, font=font_style)
criteria_label.pack()
criteria_entry = tk.Entry(root, font=font_style, textvariable=criteria_var)
criteria_entry.pack(pady=10)
criteria_entry.pack(pady=10)

# Create a button to retrieve donors' data from the database based on the selected criteria
retrieve_donors_button = tk.Button(root, text="Retrieve Donors", bg="#008CBA", fg="white", font=font_style,
                                   command=retrieve_donors)
retrieve_donors_button.pack(pady=10)

# Create a Treeview to display donor information
columns = ("ID", "Name", "Blood Group", "Contact", "Blood Bank")
display_tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")

# Set column headings
for col in columns:
    display_tree.heading(col, text=col)
    display_tree.column(col, width=100)

display_tree.pack()

# Create a button to delete donors from the database
delete_button = tk.Button(root, text="Delete Donor", bg="#FF0000", fg="white", font=font_style, command=delete_donor)
delete_button.pack(pady=10)

# Create an error label to display error messages
error_label = tk.Label(root, text="", bg=bg_color, fg="red", font=font_style)
error_label.pack()

root.mainloop()
