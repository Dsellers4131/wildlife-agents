import streamlit as st
import json
from agents.weather_collector import collect_environmental_data
from agents.condition_analyst import analyze_conditions
from tools.queue_tool import publish_alert
from dotenv import load_dotenv

load_dotenv()
logo_path = logo_path = 'assets/wildlife_logo.png'

# Deer tracks loader HTML + CSS
deer_tracks_loader = """
<style>
.loader {
  width: calc(9*30px);
  height: 50px;
  display: grid;
  color: #8d7958;
  filter: drop-shadow(30px 25px 0 currentColor)
          drop-shadow(60px 0 0 currentColor)
          drop-shadow(120px 0 0 currentColor);
  clip-path: inset(0 100% 0 0);
  animation: l14 3s infinite steps(10);
}
.loader:before,
.loader:after {
  content: "";
  width: 24px;
  grid-area: 1/1;
  height: 9px;
  background:
    radial-gradient(farthest-side,currentColor 90%,#0000) left/10px 9px,
    conic-gradient(from -106deg at right,#0000, currentColor 2deg 29deg,#0000 33deg) right/17px 11px;
  background-repeat: no-repeat;
  transform: rotate(7deg);
  transform-origin: 5px 50%;
}
.loader:after {
  margin-top: 12px;
  transform: rotate(-7deg);
}
@keyframes l14 {
  100% {clip-path: inset(0 -30px 0 0)}
}
</style>
<div style="text-align:center; margin-top:10px;">
  <div class="loader"></div>
  <p style="color:#aaaaaa; margin-top:8px;">Following deer movement...</p>
</div>
"""
st.set_page_config(
    page_title = '[CONDITION MONITORING FOR YOU]',
    page_icon = str(logo_path),
    layout = 'centered'
)

st.image(str(logo_path), width = 200)

st.markdown("""
    <h1 style='color: #f5a623; font-weight: 900; letter-spacing: 2px;'>
        CONDITION MONITOR
    </h1>
    <p style='color: #aaaaaa;'>Powered by local AI — Built for WILDLIFE</p>
    <hr style='border-color: #4a7c2f;'>
""", unsafe_allow_html=True)

from tools.locations import HUNTING_LOCATIONS

st.subheader("Your Hunting Location:")

selected_city = st.selectbox(
    "Search your city",
    options=list(HUNTING_LOCATIONS.keys()),
    index=list(HUNTING_LOCATIONS.keys()).index("Austin, TX")
)

lat, lon = HUNTING_LOCATIONS[selected_city]
location_name = selected_city

st.markdown(f"""
    <small style='color: #aaaaaa;'>
    📍 Coordinates: {lat}, {lon} — 
    Not seeing your city? 
    <a href='https://github.com/dallassellers/wildlife-agents/issues' 
    target='_blank' style='color: #f5a623;'>Request it</a>
    </small>
""", unsafe_allow_html=True)

# Run button
if st.button("ANALYZE CONDITIONS", use_container_width=True):
    if not location_name:
        st.warning("Please enter a location name.")
    else:
        location = {"name": location_name, "lat": lat, "lon": lon}

        # Show deer tracks loader while work happens
        loader_placeholder = st.empty()
        loader_placeholder.markdown(deer_tracks_loader, unsafe_allow_html=True)

        # Step 1 - Collect data
        data_package = collect_environmental_data(lat, lon)

        # Step 2 - Analyze
        result = analyze_conditions(data_package)

        # Replace loader with “ready” message
        loader_placeholder.markdown(
            "<p style='text-align:center; color:#f5a623; font-weight:900;'>CONDITIONS READY</p>",
            unsafe_allow_html=True,
        )
        # Score display
        st.markdown("<hr style='border-color: #4a7c2f;'>", unsafe_allow_html=True)
        st.subheader("Condition Score")

        score = result['score']

        if score >= 8:
            color = "#f5a623"
            label = "PRIME CONDITIONS"
        elif score >= 6:
            color = "#4a7c2f"
            label = "GOOD CONDITIONS"
        else:
            color = "#aaaaaa"
            label = "POOR CONDITIONS"

        st.markdown(f"""
            <div style='text-align: center; padding: 20px; 
                        background-color: #2d2d2d; border-radius: 10px;
                        border: 2px solid {color};'>
                <h1 style='color: {color}; font-size: 72px; margin: 0;'>{score}/10</h1>
                <h3 style='color: {color};'>{label}</h3>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"Reasoning: {result['reasoning']}")
        st.markdown(f"Key Factors: {', '.join(result['key_factors'])}")

        #alerting sqs
        st.markdown("<hr style='border-color: #4a7c2f;'>", unsafe_allow_html=True)
        if result['should_alert']:
            publish_alert(result, location)
            st.success("Alert published to AWS SQS — hunters would be notified!")
        else:
            st.info("Conditions below alert threshold — no notification sent")

        # Raw data expander
        with st.expander("View Raw Data"):
            st.json(data_package)