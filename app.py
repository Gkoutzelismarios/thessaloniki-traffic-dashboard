import streamlit as st
import geopandas as gpd
import pydeck as pdk
import numpy as np
import json
import requests  # Χρειάζεται για να κατεβάσουμε το αρχείο από το Release URL

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

# 3. ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ ΑΠΟ GITHUB RELEASE URL
@st.cache_data
def load_geojson_data():
    # ⚠️ ΑΝΤΙΚΑΤΑΣΤΗΣΤΕ ΑΥΤΟ ΤΟ LINK ΜΕ ΤΟ ΔΙΚΟ ΣΑΣ LINK ΑΠΟ ΤΟ GITHUB RELEASE
    RELEASE_URL = "https://github.com"
    
    # Κατέβασμα του αρχείου 30MB από το ίντερνετ
    response = requests.get(RELEASE_URL)
    response.raise_for_status() # Έλεγχος αν κατέβηκε επιτυχώς
    data = response.json()
        
    # Μετατροπή του json σε GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(data["features"])
    gdf.set_crs(epsg=4326, inplace=True)
        
    # ΠΡΟΣΟΜΟΙΩΣΗ ΚΙΝΗΣΗΣ
    np.random.seed(42)
    traffic_types = ['Μποτιλιάρισμα', 'Καθυστερήσεις', 'Ελεύθερη Ροή']
    
    colors_string = {
        'Μποτιλιάρισμα': "239,35,60,200",   # Κόκκινο
        'Καθυστερήσεις': "255,159,67,200",  # Πορτοκαλί
        'Ελεύθερη Ροή': "76,201,240,180"    # Γαλάζιο/Πράσινο
    }
    
    speeds_dict = {
        'Μποτιλιάρισμα': 12,
        'Καθυστερήσεις': 24,
        'Ελεύθερη Ροή': 55
    }
    
    choices = np.random.choice(traffic_types, size=len(gdf))
    
    gdf['status'] = choices
    gdf['speed_numeric'] = [speeds_dict[status] for status in choices]
    gdf['speed'] = [f"{speeds_dict[status]} χλμ/ώ" for status in choices]
    gdf['color'] = [[int(x) for x in colors_string[status].split(',')] for status in choices]
    
    if 'name' not in gdf.columns:
        gdf['name'] = "Κεντρικός Άξονας / Στενό"
        
    return gdf

# Φόρτωση των δεδομένων
with st.spinner("Λήψη και φόρτωση οδικού δικτύου από το GitHub Releases... Παρακαλώ περιμένετε."):
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

gdf_filtered = gdf_streets[gdf_streets['status'].isin(επιλογή_κατάστασης)]

# 6. ΕΜΦΑΝΙΣΗ ΧΑΡΤΗ
st.subheader("🗺️ Διαδραστικό Ψηφιακό Δίκτυο Κίνησης")

if len(gdf_filtered) > 0:
    geojson_dict = json.loads(gdf_filtered.to_json())
    
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_dict,
        pickable=True,
        stroked=True,
        filled=False,
        extruded=False,
        get_line_color="properties.color",  
        get_line_width=4,                  
        line_width_min_pixels=2,           
    )
    
    view_state = pdk.ViewState(
        latitude=40.640,
        longitude=22.944,
        zoom=12.5,
        pitch=0
    )
    
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
