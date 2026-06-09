import streamlit as st
import geopandas as gpd
import pydeck as pdk
import numpy as np
import json

# 1. ΥΠΟΧΡΕΩΤΙΚΑ ΣΤΗΝ ΠΡΩΤΗ ΓΡΑΜΜΗ ΚΩΔΙΚΑ
st.set_page_config(
    page_title="Thessaloniki Traffic Dashboard",
    page_icon="🚗",
    layout="wide",  
    initial_sidebar_state="expanded"
)

# 2. ΚΥΡΙΟΣ ΤΙΤΛΟΣ
st.title("🚗 Thessaloniki Traffic Dashboard (6.000+ Δρόμοι)")
st.markdown("### Πλήρες Ψηφιακό Μοντέλο Οδικού Δικτύου Θεσσαλονίκης")
st.caption("Η εφαρμογή εκτελείται ζωντανά στον browser σας. Δεν απαιτείται καμία εγκατάσταση.")
st.markdown("---")

# 3. ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ (JSON / GEOJSON)
@st.cache_data
def load_geojson_data():
    # 1. Φορτώνουμε το αρχείο χρησιμοποιώντας την κλασική βιβλιοθήκη json
    with open("real_thess_traffic.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 2. Μετατρέπουμε το json απευθείας σε GeoDataFrame (παρακάμπτοντας το pyogrio)
    gdf = gpd.GeoDataFrame.from_features(data["features"])
    
    # 3. Ορίζουμε το σύστημα συντεταγμένων σε WGS84 (παγκόσμιο)
    gdf.set_crs(epsg=4326, inplace=True)
        
    # ΠΡΟΣΟΜΟΙΩΣΗ ΚΙΝΗΣΗΣ: Δημιουργούμε τυχαία κίνηση για κάθε δρόμο
    np.random.seed(42)
    traffic_types = ['Μποτιλιάρισμα', 'Καθυστερήσεις', 'Ελεύθερη Ροή']
    colors = [,   # Κόκκινο
        [ffd166, 200],   # Πορτοκαλί
        [6, 214, 160, 200]     # Πράσινο
    ]
    speeds = [12, 28, 65]
    
    choices = np.random.choice(len(traffic_types), size=len(gdf))
    
    gdf['status'] = [traffic_types[i] for i in choices]
    gdf['color'] = [colors[i] for i in choices]
    gdf['speed'] = [f"{speeds[i]} χλμ/ώ" for i in choices]
    gdf['speed_numeric'] = [speeds[i] for i in choices]
    
    # Έλεγχος για το όνομα του δρόμου
    if 'name' not in gdf.columns:
        gdf['name'] = "Κεντρικός Άξονας / Στενό"
        
    return gdf

    # Έλεγχος για το όνομα του δρόμου
    if 'name' not in gdf.columns:
        gdf['name'] = "Κεντρικός Άξονας / Στενό"
        
    return gdf

# Φόρτωση των δεδομένων με ένδευξη loading
with st.spinner("Φόρτωση οδικού δικτύου (6.000+ δρόμοι)... Παρακαλώ περιμένετε."):
    gdf_streets = load_geojson_data()

# 4. ΣΤΑΤΙΣΤΙΚΑ ΣΤΟΙΧΕΙΑ (KPIs)
συνολικοί_δρόμοι = len(gdf_streets)
μποτιλιαρισμένοι = len(gdf_streets[gdf_streets['status'] == 'Μποτιλιάρισμα'])
μέση_ταχύτητα = int(gdf_streets["speed_numeric"].mean())

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Σύνολο Χαρτογραφημένων Δρόμων", value=f"{συνολικοί_δρόμοι:,} οδοί")
with col2:
    st.metric(label="Δρόμοι σε Μποτιλιάρισμα", value=f"{μποτιλιαρισμένοι:,} άξονες")
with col3:
    st.metric(label="Μέση Ταχύτητα Πόλης", value=f"{μέση_ταχύτητα} χλμ/ώ")

st.markdown("---")

# 5. ΠΛΕΥΡΙΚΟ ΜΕΝΟΥ (SIDEBAR) ΓΙΑ ΦΙΛΤΡΑΡΙΣΜΑ
st.sidebar.header("📍 Φίλτρα Κατάστασης")
επιλογή_κατάστασης = st.sidebar.multiselect(
    "Εμφάνιση δρόμων με βάση την κίνηση:",
    ['Μποτιλιάρισμα', 'Καθυστερήσεις', 'Ελεύθερη Ροή'],
    default=['Μποτιλιάρισμα', 'Καθυστερήσεις', 'Ελεύθερη Ροή']
)

# Φιλτράρισμα του GeoDataFrame βάσει της επιλογής του χρήστη
gdf_filtered = gdf_streets[gdf_streets['status'].isin(επιλογή_κατάστασης)]

# 6. ΕΜΦΑΝΙΣΗ ΧΑΡΤΗ
st.subheader("🗺️ Διαδραστικό Ψηφιακό Δίκτυο Κίνησης")

if len(gdf_filtered) > 0:
    # Μετατροπή σε Python dictionary (JSON) για μέγιστη ταχύτητα στο Pydeck
    geojson_dict = json.loads(gdf_filtered.to_json())
    
    # Χρήση GeoJsonLayer για σχεδίαση χιλιάδων γραμμών ταυτόχρονα
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_dict,
        pickable=True,
        stroked=True,
        filled=False,
        extruded=False,
        get_line_color="properties.color",  # Διαβάζει το χρώμα από τα properties του GeoJSON
        get_line_width=4,                  # Πάχος γραμμής των δρόμων
        line_width_min_pixels=2,           # Ελάχιστο πάχος για zoom out
    )
    
    # Αυτόματο κεντράρισμα στη Θεσσαλονίκη
    view_state = pdk.ViewState(
        latitude=40.640,
        longitude=22.944,
        zoom=12.5,
        pitch=0
    )
    
    # Σχεδίαση χάρτη
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "Οδός: {name}\nΚατάσταση: {status}\nΤαχύτητα: {speed}"}
    ))
else:
    st.error("Παρακαλώ επιλέξτε τουλάχιστον μια κατάσταση κίνησης από το μενού αριστερά.")

st.markdown("---")
st.caption("© 2026 Thessaloniki Traffic Dashboard | Αναπτυχθηκε με Streamlit, GeoPandas & Pydeck")
