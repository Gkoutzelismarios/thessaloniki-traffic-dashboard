import streamlit as st
import pandas as pd
import numpy as np

# 1. ΥΠΟΧΡΕΩΤΙΚΑ ΣΤΗΝ ΠΡΩΤΗ ΓΡΑΜΜΗ ΚΩΔΙΚΑ
# Ρυθμίζει την εφαρμογή σε wide mode για να μην μπερδεύει τους χρήστες με το PWA
st.set_page_config(
    page_title="Thessaloniki Traffic Dashboard",
    page_icon="🚗",
    layout="wide",  
    initial_sidebar_state="expanded"
)

# 2. ΚΥΡΙΟΣ ΤΙΤΛΟΣ
st.title("🚗 Thessaloniki Traffic Dashboard")
st.markdown("### Σύστημα Παρακολούθησης Κυκλοφορίας Θεσσαλονίκης")
st.caption("Η εφαρμογή εκτελείται ζωντανά στον browser σας. Δεν απαιτείται καμία εγκατάσταση.")
st.markdown("---")

# 3. ΠΛΕΥΡΙΚΟ ΜΕΝΟΥ (SIDEBAR)
st.sidebar.header("📍 Κριτήρια Αναζήτησης")
οδός = st.sidebar.selectbox(
    "Επιλέξτε Οδικό Άξονα:",
    ["Περιφερειακή Οδός", "Εγνατία Οδός", "Τσιμισκή", "Λεωφόρος Νίκης", "Βασιλίσσης Όλγας", "Κωνσταντίνου Καραμανλή"]
)

ώρα = st.sidebar.slider("Ώρα Ελέγχου:", 0, 23, 14)

# 4. ΣΤΑΤΙΣΤΙΚΑ ΣΤΟΙΧΕΙΑ (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Μέση Ταχύτητα Ροής", value="38 χλμ/ώ", delta="-5 χλμ/ώ (Καθυστέρηση)")
with col2:
    st.metric(label="Χρόνος Διαδρομής (Κέντρο)", value="22 λεπτά", delta="+4 λεπτά")
with col3:
    st.metric(label="Δείκτης Συμφόρησης", value="74%", delta="Υψηλός", delta_color="inverse")

st.markdown("---")

# 5. ΧΑΡΤΗΣ ΚΑΙ ΔΙΑΓΡΑΜΜΑΤΑ
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Κυκλοφοριακός Φόρτος ανά Ώρα")
    # Δημιουργία τυχαίων δεδομένων για επίδειξη
    δεδομένα_γραφήματος = pd.DataFrame(
        np.random.randint(100, 1000, size=(24, 2)),
        columns=['ΙΧ Οχήματα', 'Μέσα Μαζικής Μεταφοράς']
    )
    st.line_chart(δεδομένα_γραφήματος)

with col_right:
    st.subheader("🗺️ Κεντρικά Σημεία Ελέγχου (Θεσσαλονίκη)")
    # Συντεταγμένες για κεντρικά σημεία της Θεσσαλονίκης
    δεδομένα_χάρτη = pd.DataFrame({
        'lat': [40.6401, 40.6293, 40.6340, 40.6210],
        'lon': [22.9444, 22.9482, 22.9322, 22.9530]
    })
    st.map(δεδομένα_χάρτη)

st.markdown("---")
st.caption("© 2026 Thessaloniki Traffic Dashboard | Αναπτυχθηκε με το Streamlit")
