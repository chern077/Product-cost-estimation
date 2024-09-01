import streamlit as st
import pandas as pd
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.GProp import GProp_GProps

# Streamlit app title
st.title("Material Cost Calculator")

# File uploader for STEP file
step_file = st.file_uploader("Upload STEP file", type=["stp", "step"])

# Dropdown for material selection
material_options = ["LDPE", "PVC", "ABS", "HDPE", "PU"]
material_input = st.selectbox("Select the type of material", material_options)

# Numeric input for MOQ selection
MOQ_num = st.selectbox("Select the MOQ", [10, 100, 1000, 10000])

if step_file:
    # Save uploaded STEP file temporarily
    with open("temp.stp", "wb") as f:
        f.write(step_file.getbuffer())

    # STEP file processing
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile("temp.stp")

    if status == IFSelect_RetDone:
        step_reader.TransferRoots()
        shape = step_reader.OneShape()
        st.success("STEP file loaded successfully.")

        # Calculate volume properties
        props = GProp_GProps()
        brepgprop_VolumeProperties(shape, props)
        volume = props.Mass() / 1000  # Convert to cubic units
        st.write(f"Volume of the shape: {volume:.2f} cubic units")

        # Load material properties
        df = pd.read_excel("material.xlsx")  # Adjust the path to your Excel file
        density = df.loc[df['Material'] == material_input, 'Density (g/cm3)'].iloc[0]
        cost = df.loc[df['Material'] == material_input, 'Cost/kg INR'].iloc[0]
        wastage_percent = df.loc[df['MOQ'] == MOQ_num, 'Wastage_percentage'].iloc[0]

        # Calculate mass, MOQ mass, and total cost
        mass = density * volume
        moq_mass = (mass * wastage_percent / 100) + mass
        total_cost = moq_mass * cost / 1000

        # Display results
        st.write(f"Density: {density} g/cm³")
        st.write(f"Volume: {volume:.2f} cm³")
        st.write(f"Mass: {mass:.2f} g")
        st.write(f"Cost of material per kg: {cost} INR")
        st.write(f"MOQ: {MOQ_num} units")
        st.write(f"Raw Material Wastage Percentage: {wastage_percent}%")
        st.write(f"Total Cost: {total_cost:.2f} INR")
    else:
        st.error("Failed to load STEP file.")

