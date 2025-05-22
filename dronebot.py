import streamlit as st
import requests
import plotly.graph_objects as go
import numpy as np

# --- Drone Recommendation Logic ---
def suggest_frame_and_type(mission_type, payload_weight_grams):
    if payload_weight_grams > 10000:
        return "Heavy-lift octocopter", 800
    elif payload_weight_grams > 5000:
        return "Heavy-lift hexacopter", 650
    else:
        return "Quadcopter", 550

def suggest_motors(frame_size_mm, payload_weight_grams):
    if frame_size_mm >= 700:
        return "4114 320KV"
    elif frame_size_mm >= 600:
        return "3510 500KV"
    elif frame_size_mm >= 500:
        return "2814 700KV"
    elif frame_size_mm >= 400:
        return "2212 920KV"
    else:
        return "1806 2300KV"

def suggest_propellers(frame_size_mm):
    if frame_size_mm >= 700:
        return 17
    elif frame_size_mm >= 600:
        return 15
    elif frame_size_mm >= 500:
        return 12
    elif frame_size_mm >= 400:
        return 10
    else:
        return 5

def suggest_battery(frame_size_mm):
    if frame_size_mm >= 700:
        return "6S 10000KV"
    elif frame_size_mm >= 600:
        return "6S 8000KV"
    elif frame_size_mm >= 500:
        return "4S 6000KV"
    elif frame_size_mm >= 400:
        return "4S 4000KV"
    else:
        return "3S 2200KV"

# --- Drone 3D Visual Generator ---
def draw_drone_3d(frame_size_mm, propeller_diameter_inches, payload=False):
    arm_length = min(40.0, float(frame_size_mm) / 20.0)
    prop_radius = float(propeller_diameter_inches) / 2.0

    fig = go.Figure()

    for angle_deg in [0, 90, 180, 270]:
        angle_rad = np.radians(angle_deg)
        x = [0, arm_length * np.cos(angle_rad)]
        y = [0, arm_length * np.sin(angle_rad)]
        z = [0, 0]
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            line=dict(color='gray', width=10), name='Arm'))

    for angle_deg in [0, 90, 180, 270]:
        angle_rad = np.radians(angle_deg)
        cx = arm_length * np.cos(angle_rad)
        cy = arm_length * np.sin(angle_rad)
        cz = 0
        theta = np.linspace(0, 2 * np.pi, 20)
        px = cx + prop_radius * np.cos(theta)
        py = cy + prop_radius * np.sin(theta)
        pz = np.full_like(px, cz)
        fig.add_trace(go.Scatter3d(x=px, y=py, z=pz, mode='lines', line=dict(color='black', width=2), name='Propeller'))

    # Body
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=15, color='red'), name='Body'))

    # Forward direction
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, arm_length * 1.2], z=[0, 0], mode='lines', line=dict(color='blue', width=4, dash='dot'), name='Front'))

    # Optional payload box
    if payload:
        fig.add_trace(go.Scatter3d(
            x=[0.5], y=[0.5], z=[-1],
            mode='markers', marker=dict(size=8, color='green'), name='Payload'))

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='data'))

    return fig

# --- Streamlit UI ---
st.title("Drone Design Assistant")
st.write("Answer a few questions and get recommendations for building your drone:")

mission_type = st.selectbox("Mission Type:", ["Recreational", "Photography/Videography", "Delivery", "Inspection", "Other"])
payload_weight_grams = st.number_input("Payload Weight (grams):", min_value=0, value=500)
desired_flight_time_minutes = st.number_input("Desired Flight Time (minutes):", min_value=1, value=10)
frame_size_mm = st.number_input("Frame Size (in mm):", min_value=100, value=450)
propeller_diameter_inches = st.number_input("Propeller Diameter (inches):", min_value=1.0, value=10.0, step=0.1)

if st.button("Get Drone Design Recommendation"):
    st.subheader("Recommendations")

    frame_type, recommended_frame_size = suggest_frame_and_type(mission_type, payload_weight_grams)
    recommended_motor = suggest_motors(recommended_frame_size, payload_weight_grams)
    recommended_prop = suggest_propellers(recommended_frame_size)
    recommended_battery = suggest_battery(recommended_frame_size)

    st.markdown(f"✅ **Recommended:** {frame_type}, {recommended_motor} motors, {recommended_prop}-inch props, {recommended_battery} battery")
    if desired_flight_time_minutes > 20:
        st.markdown("⚠ **High flight time! Consider using larger batteries or fixed-wing designs for endurance.**")

    st.subheader("User Input 3D Visualization")
    user_fig = draw_drone_3d(frame_size_mm, propeller_diameter_inches, payload=True)
    st.plotly_chart(user_fig, use_container_width=True)

    st.subheader("Recommended Drone 3D Visualization")
    recommended_fig = draw_drone_3d(recommended_frame_size, recommended_prop, payload=True)
    st.plotly_chart(recommended_fig, use_container_width=True)

    st.markdown("<br><br>**Note:** This is a simplified visual and estimation. Actual drone builds should consider detailed thrust-to-weight ratios, component compatibility, and real-world testing.", unsafe_allow_html=True)
