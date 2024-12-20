import streamlit as st
import datetime
import json
import os

# Path to the JSON file that will store the appointments
appointments_file = "appointments.json"

# Injecting custom CSS
st.markdown("""
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f0f8ff;
        color: #333333;
    }
    .stApp {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 {
        color: #004466;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .stExpander {
        background-color: #e6f7ff;
        border: 1px solid #cce7ff;
        border-radius: 8px;
    }
    .stExpanderHeader {
        color: #004466;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Function to load appointments from JSON file
def load_appointments():
    if os.path.exists(appointments_file):
        with open(appointments_file, "r") as file:
            return json.load(file)
    return []

# Function to save appointments to JSON file
def save_appointments(appointments):
    with open(appointments_file, "w") as file:
        json.dump(appointments, file, default=str)  # Using default=str to handle datetime serialization

# Initialize session state for appointments
if "appointments" not in st.session_state:
    st.session_state.appointments = load_appointments()

# Function to convert selected time to 24-hour format
def parse_selected_time(hour, minute, period):
    if period == "P.M." and hour != 12:
        hour += 12
    if period == "A.M." and hour == 12:
        hour = 0
    return datetime.time(hour, minute)

# Function to display all appointments
def display_appointments():
    if not st.session_state.appointments:
        st.write("No appointments scheduled.")
    else:
        for i, appt in enumerate(st.session_state.appointments, start=1):
            st.markdown(f"**{i}. {appt['name']}** - {appt['date']}")

# Quicksort Function
def quicksort(arr, key_func):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if key_func(x) < key_func(pivot)]
    middle = [x for x in arr if key_func(x) == key_func(pivot)]
    right = [x for x in arr if key_func(x) > key_func(pivot)]
    return quicksort(left, key_func) + middle + quicksort(right, key_func)

# Binary Search Function
def binary_search(arr, target, key_func):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if key_func(arr[mid]) < target:
            low = mid + 1
        elif key_func(arr[mid]) > target:
            high = mid - 1
        else:
            return mid
    return -1

# Streamlit application
st.title("Appointment Scheduling System")
st.markdown("Welcome to the **Appointment Scheduling System**! Manage your appointments effectively.")

# Create Appointment
with st.expander("Create Appointment", expanded=True):
    name = st.text_input("Enter Client Name:")
    date = st.date_input("Select Appointment Date:", min_value=datetime.date.today())
    hour = st.selectbox("Hour:", options=list(range(1, 13)), index=0, key="create_hour")  # Unique key
    minute = st.selectbox("Minute:", options=list(range(0, 60)), index=0, key="create_minute")  # Unique key
    period = st.selectbox("Period:", options=["A.M.", "P.M."], index=0, key="create_period")  # Unique key
    if st.button("Add Appointment"):
        if name:
            appointment_time = parse_selected_time(hour, minute, period)
            appointment_datetime = datetime.datetime.combine(date, appointment_time)
            new_appointment = {"name": name, "date": appointment_datetime}
            st.session_state.appointments.append(new_appointment)
            save_appointments(st.session_state.appointments)  # Save to JSON
            st.success("Appointment added successfully!")
        else:
            st.error("Client name cannot be empty.")

# Sort Appointments using Quicksort
with st.expander("Sort Appointments"):
    sort_option = st.radio("Sort By:", options=["Date", "Name"])
    if st.button("Sort Appointments"):
        if sort_option == "Date":
            st.session_state.appointments = quicksort(
                st.session_state.appointments, key_func=lambda appt: appt["date"]
            )
        elif sort_option == "Name":
            st.session_state.appointments = quicksort(
                st.session_state.appointments, key_func=lambda appt: appt["name"].lower()
            )
        save_appointments(st.session_state.appointments)  # Save to JSON
        st.success("Appointments sorted successfully!")

# Display Appointments
st.subheader("Scheduled Appointments")
display_appointments()

# Update Appointment - Allow updating any client
with st.expander("Update Appointment"):
    if st.session_state.appointments:
        appt_to_update = st.selectbox(
            "Select Appointment to Update:",
            options=[f"{i + 1}. {appt['name']} - {appt['date']}" for i, appt in enumerate(st.session_state.appointments)],
            index=0,
            key="update_select_appt"  # Unique key
        )
        if appt_to_update:
            index = int(appt_to_update.split(".")[0]) - 1  # Get the selected index
            current_appt = st.session_state.appointments[index]
            new_name = st.text_input("Enter New Client Name:", current_appt["name"])
            new_date = st.date_input("Select New Appointment Date:", current_appt["date"].date())
            current_time = current_appt["date"].time()
            current_hour = current_time.hour % 12 or 12
            current_minute = current_time.minute
            current_period = "P.M." if current_time.hour >= 12 else "A.M."
            new_hour = st.selectbox("Hour:", options=list(range(1, 13)), index=current_hour - 1, key=f"update_hour_{index}")  # Unique key for each appointment
            new_minute = st.selectbox("Minute:", options=list(range(0, 60)), index=current_minute, key=f"update_minute_{index}")  # Unique key
            new_period = st.selectbox("Period:", options=["A.M.", "P.M."], index=0 if current_period == "A.M." else 1, key=f"update_period_{index}")  # Unique key
            if st.button("Update Appointment"):
                new_time = parse_selected_time(new_hour, new_minute, new_period)
                st.session_state.appointments[index] = {
                    "name": new_name,
                    "date": datetime.datetime.combine(new_date, new_time),
                }
                save_appointments(st.session_state.appointments)  # Save to JSON
                st.success("Appointment updated successfully!")
    else:
        st.write("No appointments available to update.")

# Delete Appointment
with st.expander("Delete Appointment"):
    if st.session_state.appointments:
        appt_to_delete = st.selectbox(
            "Select Appointment to Delete:",
            options=[f"{i + 1}. {appt['name']} - {appt['date']}" for i, appt in enumerate(st.session_state.appointments)],
            index=0,
            key="delete_select_appt"  # Unique key
        )
        if appt_to_delete and st.button("Delete Appointment"):
            index = int(appt_to_delete.split(".")[0]) - 1
            st.session_state.appointments.pop(index)
            save_appointments(st.session_state.appointments)  # Save to JSON
            st.success("Appointment deleted successfully!")
    else:
        st.write("No appointments available to delete.")

# Search Appointments using Binary Search
with st.expander("Search Appointments"):
    search_term = st.text_input("Enter Client Name or Date (YYYY-MM-DD) to Search:")
    if search_term:
        # First, sort the appointments
        st.session_state.appointments = quicksort(
            st.session_state.appointments, key_func=lambda appt: appt["name"].lower()
        )
        # Perform binary search
        index = binary_search(
            st.session_state.appointments, search_term.lower(), key_func=lambda appt: appt["name"].lower()
        )
        if index != -1:
            appt = st.session_state.appointments[index]
            st.subheader("Search Result:")
            st.markdown(f"**{appt['name']}** - {appt['date']}")
        else:
            st.write("No matching appointments found.")

