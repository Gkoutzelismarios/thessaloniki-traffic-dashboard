import streamlit as st

# ΑΥΤΗ Η ΡΥΘΜΙΣΗ ΠΡΕΠΕΙ ΝΑ ΕΙΝΑΙ Η ΠΡΩΤΗ ΕΝΤΟΛΗ STREAMLIT ΣΤΟΝ ΚΩΔΙΚΑ
st.set_page_config(
    page_title="Thessaloniki Traffic Dashboard",
    page_icon="🚗",
    layout="wide",  # Απλώνει την εφαρμογή σε όλο το πλάτος της οθόνης
    initial_sidebar_state="expanded"  # Κρατάει το μενού ανοιχτό αν υπάρχει
)

# ΤΙΤΛΟΣ ΤΗΣ ΕΦΑΡΜΟΓΗΣ
st.title("🚗 Thessaloniki Traffic Dashboard")
st.markdown("---")

# ΕΔΩ ΣΥΝΕΧΙΖΕΤΕ ΜΕ ΤΟΝ ΥΠΟΛΟΙΠΟ ΚΩΔΙΚΑ ΤΗΣ ΕΦΑΡΜΟΓΗΣ ΣΑΣ
st.subheader("Ζωντανή Εικόνα Κίνησης")
st.info("Η εφαρμογή τρέχει κανονικά στον browser σας. Δεν απαιτείται καμία εγκατάσταση εφαρμογής.")

# Παράδειγμα για το πού θα μπουν τα widget σας:
# col1, col2 = st.columns(2)
# with col1:
#     st.write("Δεδομένα Κίνησης")

)
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🚦 Live-Style Geodata Dashboard: Traffic Thessaloniki")

# 1. Φόρτωση των γεωχωρικών δεδομένων (GeoJSON)
@st.cache_data
def load_data():
    gdf = gpd.read_file("https://github.com/Gkoutzelismarios/thessaloniki-traffic-dashboard/releases/download/v1.0/real_thess_traffic.json")
    
    # 🔥 ΔΙΟΡΘΩΣΗ ΣΦΑΛΜΑΤΟΣ: Μετατροπή όλων των στηλών (εκτός γεωμετρίας) σε απλό κείμενο/αριθμό
    # Αυτό αφαιρεί τυχόν ndarrays που κρασάρουν το Folium
    for col in gdf.columns:
        if col != 'geometry':
            # Αν η στήλη περιέχει λίστες, τις μετατρέπει σε απλό κείμενο χωρισμένο με κόμμα
            gdf[col] = gdf[col].apply(lambda x: ", ".join(map(str, x)) if isinstance(x, (list, np.ndarray)) else x)
            gdf[col] = gdf[col].astype(str)
            
    # Μετατροπή της ταχύτητας ξανά σε αριθμό για τα γραφήματα
    if 'Speed_kmh' in gdf.columns:
        gdf['Speed_kmh'] = gpd.pd.to_numeric(gdf['Speed_kmh'], errors='coerce').fillna(0).astype(int)
        
    return gdf

try:
    import numpy as np # Χρειάζεται για τον έλεγχο ndarray στη load_data
    gdf = load_data()
    
    # 2. Sidebar - Φιλτράρισμα Χιλιάδων/Εκατοντάδων Δρόμων
    st.sidebar.header("🎛️ Φίλτρα Dashboard")
    
    # Φίλτρο Κατάστασης Κίνησης
    all_statuses = gdf['Traffic_Status'].unique()
    selected_statuses = st.sidebar.multiselect(
        "Επιλέξτε Κατάσταση Οδικού Δικτύου:", 
        all_statuses, 
        default=all_statuses
    )
    
    # Εφαρμογή Φίλτρου
    filtered_gdf = gdf[gdf['Traffic_Status'].isin(selected_statuses)]
    
    # Χρωματική Παλέτα για το Dashboard
    color_picker = {
        'Traffic Jam': '#FF0000',     # Κόκκινο
        'High Traffic': '#FF8C00',    # Πορτοκαλί
        'Delays': '#FFFF00',          # Κίτρινο
        'Normal Flow': '#00FF00'       # Πράσινο
    }
    
    # 3. Layout: 2 Στήλες (Αριστερά Χάρτης, Δεξιά Γραφήματα)
    col1, col2 = st.columns([2, 1]) # 66% Χάρτης, 33% Στατιστικά
    
    with col1:
        st.subheader("🗺️ Διαδραστικός Γεωχωρικός Χάρτης")
        
        # Κεντράρισμα στη Θεσσαλονίκη
        m = folium.Map(location=[40.6350, 22.9440], zoom_start=13, tiles="OpenStreetMap")
        
        # Προσθήκη των Πολυγώνων των δρόμων απευθείας πάνω στο χάρτη
        if not filtered_gdf.empty:
            folium.GeoJson(
                filtered_gdf,
                name="Traffic Lines",
                style_function=lambda feature: {
                    'fillColor': color_picker.get(feature['properties']['Traffic_Status'], '#0000FF'),
                    'color': color_picker.get(feature['properties']['Traffic_Status'], '#0000FF'),
                    'weight': 4,
                    'fillOpacity': 0.6,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['Road_Name', 'Traffic_Status', 'Speed_kmh'],
                    aliases=['Δρόμος:', 'Κατάσταση:', 'Ταχύτητα (km/h):'],
                    localize=True
                )
            ).add_to(m)
        
        # Εμφάνιση χάρτη
        st_folium(m, width=900, height=600, key="thess_dashboard_map")
        
    with col2:
        st.subheader("📊 Στατιστικά Στοιχεία Πόλης")
        
        st.metric(label="Συνολικά Τμήματα Δρόμων", value=len(filtered_gdf))
        
        if not filtered_gdf.empty:
            avg_speed = round(filtered_gdf['Speed_kmh'].mean(), 1)
            st.metric(label="Μέση Ταχύτητα Δικτύου", value=f"{avg_speed} km/h")
            
            st.write("---")
            chart_data = filtered_gdf['Traffic_Status'].value_counts().reset_index()
            chart_data.columns = ['Κατάσταση', 'Πλήθος']
            
            fig = px.pie(
                chart_data, 
                values='Πλήθος', 
                names='Κατάσταση', 
                title="Ποσοστό Κυκλοφοριακής Συμφόρησης",
                color='Κατάσταση',
                color_discrete_map={
                    'Traffic Jam': '#FF0000',
                    'High Traffic': '#FF8C00',
                    'Delays': '#FFFF00',
                    'Normal Flow': '#008000'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("📋 Δρόμοι με το μεγαλύτερο πρόβλημα:")
            slow_streets = filtered_gdf[filtered_gdf['Traffic_Status'] == 'Traffic Jam'][['Road_Name', 'Speed_kmh']].head(10)
            st.dataframe(slow_streets, use_container_width=True, hide_index=True)
            
        else:
            st.warning("Παρακαλώ επιλέξτε τουλάχιστον μία κατάσταση κίνησης από τα φίλτρα.")

except FileNotFoundError:
    st.error("❌ Το αρχείο 'real_thess_traffic.geojson' δεν βρέθηκε στον φάκελο!")
except Exception as e:
    st.error(f"❌ Προέκυψε σφάλμα: {e}")
