import streamlit as st
from datetime import datetime
import json
import re
import matplotlib.pyplot as plt

st.title("GVplotter")


# Streamlit UI
st.write("GVplotter takes porepressure data from uploaded .txt files and makes a plot")


file_path = st.file_uploader("Choose a .txt file", type=["txt"])

@st.cache_data
def preprocess_and_extract_list(file_path):
    try:
        with open(file_path, encoding="utf-8") as file:
            data = file.read().strip()  # Read the entire file content
        
        # Find the first occurrence of '[' and extract everything from there. This is because of the format of the .txt files
        match = re.search(r"\[.*\]", data, re.DOTALL)  # Match everything from '[' to the last ']'
        
        if match:
            json_data = match.group(0)  # Extract only the list part
            return json_data
        else:
            print("Error: No list found in the file.")
            return None
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None



def load_and_extract_dictionaries(file_path):

    json_data = preprocess_and_extract_list(file_path)

    if json_data:
        try:
            data_list = json.loads(json_data)

            if isinstance(data_list, list) and all(isinstance(item, dict) for item in data_list):
                return data_list
            else:
                print("Error: Extracted data is not a valid list of dictionaries.")
                return []
        
        except json.JSONDecodeError:
            print("Error: Failed to parse extracted JSON.")
            return []
    
    return []

if file_path is not None:
    dict_list = load_and_extract_dictionaries(file_path)
    if len(dict_list) > 0:
        #Leser av serienummeret til poretrykksmåleren
        serie_nummer_måler_dict = dict_list[0]
        serie_nummer_måler = serie_nummer_måler_dict["SerialNumber"]


        #Tar ut data for plotting
        timestamps = [t["DateTime"] for t in dict_list] #String timestamp
        porepressure_millimeter = [p["MillimeterWaterPressure"] for p in dict_list] #number


        #Converts timestamp-strings to objects for matplotlib year, month, day, hour, min, sec
        timestamps_objects = [datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S') for ts in timestamps]

        #Conversion from MillimeterWaterPressure to kPa
        gravity_constant_g = 0.0098065

        porepressure = [p * gravitasjon_g for p in poretrykk_millimeter]

        #Plotting
        fig, ax1 = plt.subplots(figsize=(8,6), dpi=600)
        ax1.plot(timestamps_objects, porepressure, label=serie_nummer_måler, color='tab:green', linewidth = 1)
        ax1.set_title('Poretrykk')
        legend1 = ax1.legend(title='Poretrykksmålere', fontsize='x-small', title_fontsize='x-small', bbox_to_anchor=(1.3,1))
        st.pyplot(fig)
    else:
        st.warning("No valid data to plot.")
