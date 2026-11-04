import streamlit as st
from datetime import date
import sqlite3

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="Medicine Expiry Reminder",
    page_icon="💊",
    layout="wide"
)


# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

h1 {
    color: #ffffff;
    font-size: 40px !important;
}

h2, h3 {
    color: #ffffff;
}

div[data-testid="stMetric"] {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #334155;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
}

div[data-testid="stMetricLabel"] {
    color: #cbd5e1;
}

.medicine-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #334155;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# DATABASE CONNECTION
# -----------------------------

conn = sqlite3.connect("medicines.db")

conn.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        expiry_date TEXT,
        quantity INTEGER
    )
""")

# -----------------------------
# APPLICATION HEADER
# -----------------------------

st.title("💊 Medicine Expiry Reminder")

st.caption("Manage your medicines and keep track of expiry dates.")

st.divider()


# -----------------------------
# ADD MEDICINE
# -----------------------------

st.header("➕ Add New Medicine")

with st.form("add_medicine_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        medicine_name = st.text_input("Medicine Name")

    with col2:
        expiry_date = st.date_input("Expiry Date")

    with col3:
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1
        )

    add_button = st.form_submit_button("➕ Add Medicine")

    if add_button:

        if medicine_name.strip():

            conn.execute(
                """
                INSERT INTO medicines (name, expiry_date, quantity)
                VALUES (?, ?, ?)
                """,
                (medicine_name.strip(), str(expiry_date), quantity)
            )

            conn.commit()

            st.success("Medicine added successfully!")

            st.rerun()

        else:
            st.error("Please enter a medicine name!")


st.divider()


# -----------------------------
# FETCH MEDICINES
# -----------------------------

medicines = conn.execute(
    "SELECT * FROM medicines ORDER BY id DESC"
).fetchall()

today = date.today()


# -----------------------------
# CALCULATE DASHBOARD
# -----------------------------

total_medicines = len(medicines)

expired_count = 0
expiring_soon_count = 0
safe_count = 0

for medicine in medicines:

    expiry = date.fromisoformat(medicine[2])

    days_left = (expiry - today).days

    if days_left < 0:
        expired_count += 1

    elif days_left <= 7:
        expiring_soon_count += 1

    else:
        safe_count += 1


# -----------------------------
# DASHBOARD
# -----------------------------

st.header("📊 Medicine Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("💊 Total Medicines", total_medicines)

col2.metric("🔴 Expired", expired_count)

col3.metric("🟠 Expiring Soon", expiring_soon_count)

col4.metric("🟢 Safe", safe_count)


st.divider()


# -----------------------------
# SEARCH MEDICINES
# -----------------------------

st.header("📋 Your Medicines")

search_name = st.text_input(
    "🔍 Search",
    placeholder="Enter medicine name..."
)

if search_name.strip():

    filtered_medicines = [
        medicine for medicine in medicines
        if search_name.lower() in medicine[1].lower()
    ]

else:
    filtered_medicines = medicines


# -----------------------------
# DISPLAY MEDICINE CARDS
# -----------------------------

if filtered_medicines:

    for medicine in filtered_medicines:

        medicine_id = medicine[0]
        name = medicine[1]
        expiry = date.fromisoformat(medicine[2])
        quantity = medicine[3]

        days_left = (expiry - today).days

        if days_left < 0:
            status = "🔴 Expired"
            message = f"Expired {abs(days_left)} days ago"

        elif days_left <= 7:
            status = "🟠 Expiring Soon"
            message = f"{days_left} days remaining"

        else:
            status = "🟢 Safe"
            message = f"{days_left} days remaining"

        # Medicine card

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.subheader(f"💊 {name}")

                st.write(f"📅 Expiry Date: {expiry}")

                st.write(f"📦 Quantity: {quantity}")

                st.write(f"Status: {status}")

                st.caption(message)

            with col2:

                st.write("")

                with st.expander("✏️ Edit"):

                    with st.form(key=f"edit_{medicine_id}"):

                        updated_name = st.text_input(
                            "Medicine Name",
                            value=name
                        )

                        updated_expiry = st.date_input(
                            "Expiry Date",
                            value=expiry
                        )

                        updated_quantity = st.number_input(
                            "Quantity",
                            min_value=1,
                            value=quantity,
                            step=1
                        )

                        update_button = st.form_submit_button(
                            "Save Changes"
                        )

                        if update_button:

                            if updated_name.strip():

                                conn.execute(
                                    """
                                    UPDATE medicines
                                    SET name = ?, expiry_date = ?, quantity = ?
                                    WHERE id = ?
                                    """,
                                    (
                                        updated_name.strip(),
                                        str(updated_expiry),
                                        updated_quantity,
                                        medicine_id
                                    )
                                )

                                conn.commit()

                                st.success("Medicine updated!")

                                st.rerun()

                            else:
                                st.error("Medicine name cannot be empty!")

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{medicine_id}"
                ):

                    conn.execute(
                        "DELETE FROM medicines WHERE id = ?",
                        (medicine_id,)
                    )

                    conn.commit()

                    st.success("Medicine deleted!")

                    st.rerun()

else:

    if search_name.strip():
        st.warning("No matching medicine found.")

    else:
        st.info("No medicines added yet. Add your first medicine above!")


# -----------------------------
# FOOTER
# -----------------------------

st.divider()

st.caption("Medicine Expiry Reminder | Built with Python, Streamlit and SQLite")

conn.close()