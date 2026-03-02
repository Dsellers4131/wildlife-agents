import streamlit as st
from agents.weather_collector import collect_environmental_data
from agents.condition_analyst import analyze_conditions
from tools.queue_tool import publish_alert
from tools.locations import HUNTING_LOCATIONS
from dotenv import load_dotenv

load_dotenv()



# Deer tracks loader
deer_tracks_loader = """
<style>
.loader {
  width: calc(9*30px);
  margin: 0 auto;
  height: 50px;
  display: grid;
  color: #8d7958;
  filter: drop-shadow(30px 25px 0 currentColor)
          drop-shadow(60px 0 0 currentColor)
          drop-shadow(120px 0 0 currentColor);
  clip-path: inset(0 100% 0 0);
  animation: l14 3s infinite steps(10);
}
.loader:before, .loader:after {
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
.loader:after { margin-top: 12px; transform: rotate(-7deg); }
@keyframes l14 { 100% {clip-path: inset(0 -30px 0 0)} }
</style>
<div style="text-align:center; padding: 24px 0;">
  <div class="loader"></div>
  <p style="color:#7a7568; font-family:'sans-serif'; font-size:12px; letter-spacing:3px; margin-top:16px;">
    FOLLOWING DEER MOVEMENT...
  </p>
</div>
"""

st.set_page_config(
    page_title='Wildlife Condition Monitor',
    page_icon="",
    layout='centered'
)

# ── GLOBAL STYLES ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;900&family=Barlow:wght@400;500;600&display=swap');

/* Hide Streamlit default header padding */
.block-container { padding-top: 24px !important; }

/* Metrics grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: rgba(255,255,255,0.04);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}
.moon-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: rgba(255,255,255,0.04);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}
.metric-cell {
  background: #1a1a18;
  padding: 18px 12px;
  text-align: center;
}
.metric-value {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 26px;
  font-weight: 700;
  color: #e8e4d9;
  line-height: 1;
}
.metric-unit { font-size: 13px; color: #f5a623; }
.metric-label {
  font-size: 10px;
  letter-spacing: 2px;
  color: #7a7568;
  margin-top: 5px;
  text-transform: uppercase;
  font-family: 'Barlow Condensed', sans-serif;
}

/* Score ring */
.score-wrapper {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 40px;
  align-items: center;
  margin-bottom: 28px;
}
.score-ring-container {
  position: relative;
  width: 160px;
  height: 160px;
}
.score-ring-container svg { transform: rotate(-90deg); }
.score-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.score-big {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 56px;
  font-weight: 900;
  line-height: 1;
}
.score-denom {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 12px;
  color: #7a7568;
  letter-spacing: 2px;
}
.score-label-tag {
  text-align: center;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 3px;
  margin-top: 10px;
}

/* Factor bars */
.factors { display: flex; flex-direction: column; gap: 14px; }
.factor-row {
  display: grid;
  grid-template-columns: 90px 1fr 36px;
  align-items: center;
  gap: 14px;
}
.factor-name {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #7a7568;
  text-transform: uppercase;
}
.bar-track {
  height: 4px;
  background: #2e2e2b;
  border-radius: 2px;
  overflow: hidden;
}
.bar-fill { height: 100%; border-radius: 2px; }
.bar-gold { background: #f5a623; }
.bar-green { background: #4a7c2f; }
.bar-grey { background: #7a7568; }
.factor-pts {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: #e8e4d9;
  text-align: right;
}

/* Reasoning box */
.reasoning-box {
  padding: 20px 20px 20px 24px;
  background: #252522;
  border-left: 2px solid #4a7c2f;
  border-radius: 0 4px 4px 0;
  margin-bottom: 24px;
}
.guide-label {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 3px;
  color: #4a7c2f;
  margin-bottom: 8px;
}
.reasoning-text {
  font-size: 14px;
  line-height: 1.7;
  color: #e8e4d9;
}

/* Alert bars */
.alert-bar-active {
  padding: 14px 20px;
  background: rgba(245,166,35,0.1);
  border: 1px solid rgba(245,166,35,0.4);
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #f5a623;
}
.alert-bar-inactive {
  padding: 14px 20px;
  background: rgba(61,107,33,0.1);
  border: 1px solid rgba(61,107,33,0.3);
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #4a7c2f;
}
.alert-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  animation: pulse 2s infinite;
}
.dot-gold { background: #f5a623; box-shadow: 0 0 6px #f5a623; }
.dot-green { background: #4a7c2f; box-shadow: 0 0 6px #4a7c2f; }
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

/* Section label */
.section-label {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 4px;
  color: #f5a623;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(245,166,35,0.2);
}

/* Divider */
.divider {
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(245,166,35,0.2), transparent);
  margin: 36px 0;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style="margin-bottom:32px; padding-bottom:32px; border-bottom:1px solid rgba(245,166,35,0.15);">
  <div style="font-family:'Barlow Condensed',sans-serif; font-size:10px; font-weight:700;
              letter-spacing:5px; color:#f5a623; margin-bottom:10px; display:flex;
              align-items:center; gap:10px;">
    <span style="display:inline-block; width:20px; height:1px; background:#f5a623;"></span>
    LOCATE · ANALYZE · KNOCK EM DOWN
  </div>
  <div style="font-family:'Barlow Condensed',sans-serif; font-size:52px; font-weight:900;
              line-height:0.95; text-transform:uppercase; color:#e8e4d9; margin-bottom:12px;">
    WILDLIFE<br><span style="color:#f5a623;">CONDITION MONITOR</span>
  </div>
  <p style="color:#7a7568; font-size:13px; line-height:1.6; max-width:500px;">
    Real-time hunting condition intelligence powered by local AI. 
    Know before you go.
  </p>
</div>
""", unsafe_allow_html=True)


st.markdown('<div class="section-label">SELECT YOUR LOCATION</div>', unsafe_allow_html=True)

selected_city = st.selectbox(
    label='Search your city',
    options=list(HUNTING_LOCATIONS.keys()),
    index=list(HUNTING_LOCATIONS.keys()).index("Birmingham, AL"),
    label_visibility='collapsed'
)

lat, lon = HUNTING_LOCATIONS[selected_city]
location_name = selected_city

st.markdown(f"""
<div style="font-size:12px; color:#7a7568; font-family:'Barlow Condensed',sans-serif;
            letter-spacing:1px; margin-bottom:24px;">
  📍 {lat}, {lon} — Not seeing your city?
  <a href="https://github.com/dallassellers/wildlife-agents/issues"
     target="_blank" style="color:#f5a623;">Request it</a>
</div>
""", unsafe_allow_html=True)


if st.button("ANALYZE CONDITIONS", use_container_width=True):

    location = {"name": location_name, "lat": lat, "lon": lon}

    # Loader
    loader_placeholder = st.empty()
    loader_placeholder.markdown(deer_tracks_loader, unsafe_allow_html=True)

    # Step 1 - Collect
    data_package = collect_environmental_data(lat, lon)

    # Step 2 - Analyze
    result = analyze_conditions(data_package)

    # Clear loader
    loader_placeholder.markdown(
        "<p style='text-align:center; color:#f5a623; font-family:Barlow Condensed,sans-serif;"
        "font-weight:700; letter-spacing:3px; font-size:12px;'>CONDITIONS READY</p>",
        unsafe_allow_html=True
    )

    # ── WEATHER METRICS ────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">CURRENT CONDITIONS — {selected_city.upper()}</div>',
                unsafe_allow_html=True)

    w = data_package['weather']
    m = data_package['moon']

    st.markdown(f"""
    <div class="metrics-grid">
      <div class="metric-cell">
        <div class="metric-value">{w['temperature']}<span class="metric-unit">°F</span></div>
        <div class="metric-label">Temperature</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value">{w['wind_speed']}<span class="metric-unit">mph</span></div>
        <div class="metric-label">Wind</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value">{w['pressure']}<span class="metric-unit">hPa</span></div>
        <div class="metric-label">Pressure</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value">{w['humidity']}<span class="metric-unit">%</span></div>
        <div class="metric-label">Humidity</div>
      </div>
    </div>
    <div class="moon-grid">
      <div class="metric-cell">
        <div class="metric-value" style="font-size:18px;">{m['phase'].title()}</div>
        <div class="metric-label">Moon Phase</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value">{m['illumination']}<span class="metric-unit">%</span></div>
        <div class="metric-label">Illumination</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SCORE ──────────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">CONDITION SCORE</div>', unsafe_allow_html=True)

    score = result['score']
    breakdown = result['factor_breakdown']

    if score >= 8:
        color = "#f5a623"
        label = "PRIME CONDITIONS"
    elif score >= 6:
        color = "#4a7c2f"
        label = "GOOD CONDITIONS"
    else:
        color = "#7a7568"
        label = "POOR CONDITIONS"

    # Circumference = 2 * pi * 65 = 408.4
    # offset = 408 * (1 - score/10)
    offset = round(408 * (1 - score / 10))

    def bar_class(val, max_val):
        pct = val / max_val
        if pct >= 0.8: 
            return "bar-gold"
        elif pct >= 0.5: 
            return "bar-green"
        else: 
            return "bar-grey"

    def bar_width(val, max_val):
        return round((val / max_val) * 100)

    st.markdown(f"""
    <div class="score-wrapper">
      <div>
        <div class="score-ring-container">
          <svg width="160" height="160" viewBox="0 0 160 160">
            <circle fill="none" stroke="#2e2e2b" stroke-width="10" cx="80" cy="80" r="65"/>
            <circle fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round"
                    stroke-dasharray="408" stroke-dashoffset="{offset}"
                    cx="80" cy="80" r="65"/>
          </svg>
          <div class="score-overlay">
            <div class="score-big" style="color:{color};">{score}</div>
            <div class="score-denom">/ 10</div>
          </div>
        </div>
        <div class="score-label-tag" style="color:{color};">{label}</div>
      </div>
      <div class="factors">
        <div class="factor-row">
          <div class="factor-name">Pressure</div>
          <div class="bar-track"><div class="bar-fill {bar_class(breakdown['pressure']['score'], breakdown['pressure']['max'])}"
               style="width:{bar_width(breakdown['pressure']['score'], breakdown['pressure']['max'])}%"></div></div>
          <div class="factor-pts">{breakdown['pressure']['score']}/{breakdown['pressure']['max']}</div>
        </div>
        <div class="factor-row">
          <div class="factor-name">Temperature</div>
          <div class="bar-track"><div class="bar-fill {bar_class(breakdown['temperature']['score'], breakdown['temperature']['max'])}"
               style="width:{bar_width(breakdown['temperature']['score'], breakdown['temperature']['max'])}%"></div></div>
          <div class="factor-pts">{breakdown['temperature']['score']}/{breakdown['temperature']['max']}</div>
        </div>
        <div class="factor-row">
          <div class="factor-name">Wind</div>
          <div class="bar-track"><div class="bar-fill {bar_class(breakdown['wind']['score'], breakdown['wind']['max'])}"
               style="width:{bar_width(breakdown['wind']['score'], breakdown['wind']['max'])}%"></div></div>
          <div class="factor-pts">{breakdown['wind']['score']}/{breakdown['wind']['max']}</div>
        </div>
        <div class="factor-row">
          <div class="factor-name">Moon</div>
          <div class="bar-track"><div class="bar-fill {bar_class(breakdown['moon']['score'], breakdown['moon']['max'])}"
               style="width:{bar_width(breakdown['moon']['score'], breakdown['moon']['max'])}%"></div></div>
          <div class="factor-pts">{breakdown['moon']['score']}/{breakdown['moon']['max']}</div>
        </div>
      </div>
    </div>

    <div class="reasoning-box">
      <div class="guide-label">GUIDE ANALYSIS</div>
      <div class="reasoning-text">{result['reasoning']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── ALERT ──────────────────────────────────────────────
    if result['should_alert']:
        publish_alert(result, location)
        st.markdown("""
        <div class="alert-bar-active">
          <div class="alert-dot dot-gold"></div>
          PRIME CONDITIONS DETECTED — ALERT PUBLISHED TO AWS SQS
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-bar-inactive">
          <div class="alert-dot dot-green"></div>
          CONDITIONS BELOW ALERT THRESHOLD — NO NOTIFICATION SENT
        </div>
        """, unsafe_allow_html=True)

    # ── RAW DATA ───────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    with st.expander("VIEW RAW DATA"):
        st.json(data_package)