# Import Libraries

import pandas as pd
import numpy as np
import streamlit as st
from fuzzywuzzy import process

# Define some variables
TITLE = 'Part Number Generator'
BOX_FAMILY = 'Select the Product Family'
SERIES = 'Select the Series'
TYPE =  'Select the Type'
COLOR =  'Select the Color'
VOLTAGE_CURRENT = 'Select the Voltage Current AC DC'
OPTIONS = 'Select the Options'
MOUNTING_HOLE_SIZE = 'Select the Mounting Hole Size'
BEZEL_STYLE = 'Select the Bezel Style'
TERMINALS = 'Select the Terminals'
BEZEL_FINISH = 'Select the Bezel Finish'
TYPE_OF_ILLUMINATION = 'Select the Type of Illumination'
LED_COLOR = 'Select the Led Color'
VOLTAGE = 'Select the Voltage'
SEALING = 'Select the Sealing'
SIZE = 'Select the Size'
BEZEL_COLOR = 'Select the Bezel Color'
LENS_COLOR = 'Select the Lens Color'
BOX_ATTRIBUTE = "Select the Attribute" 
BOX_CODE = "Select a Code"
product_family = ["LEDs","JOYS","PCB","PS"]

# Configure page settings
st.set_page_config(page_title='WEB APP TEST', layout='wide')

# Define functions


@st.cache
def load_data():
    """ Function to import data into a dataframe"""
    excel_data = pd.read_excel(
        "...xlsx")
    data = pd.DataFrame(excel_data)
    return data

def attributes(data,family):
    """ Function that returns the attributes available for each chosen product family"""
    filter = data[data["Attribute group"]==f'attributes_{family}']
    return filter["Attribute Label"].unique()

def attribute_code(data,family,attribute,label):
    """ Function that returns the recommended code for the label chosen in each attribute."""
    # Same label (Blue) can have different codes (AB, B) based on the attribute (Bezel Finish, Color, Led Color)

    filter = data[(data["Attribute group"]==f'attributes_{family}') & (data["Attribute Label"]==attribute) & (data["Recommended Label"]==label)]
    code = filter["Recommended code"].unique()
    return code[0]

def attribute_label(data,family,attribute):
    """ Function that returns the recommended label for each attribute selected"""
    filter = data[np.logical_and(data["Attribute group"]==f'attributes_{family}',data["Attribute Label"]==attribute)]
    return filter["Recommended Label"].unique()


def attribute_series(data,family,series):
    """ Function that returns the attributes available for each chosen series in a family"""
    filter = data[np.logical_and(data["Attribute group"]==f'attributes_{family}',data["attribute"].str.startswith(series))]
    result = filter["Attribute Label"].unique().tolist()
    result_final = result.remove('Series')
    return result


def main():
    ''' Streamlit Wep App '''

    data = load_data()

    st.title(TITLE)
              
    # Main Page
    
    # Selected product family in Help Tool. Get an error if duplicated!
    family = st.selectbox(BOX_FAMILY, product_family)

    # Select the series name
    series_list = attribute_label(data,family,"Series")
    series = st.selectbox(SERIES,series_list)
    series_code = attribute_code(data,family,"Series",series)
    attribute_list = attribute_series(data,family,series)
    

    key = 1
    PN = series_code

    for attribute in attribute_list:
        list = attribute_label(data,family,attribute)
        value = st.selectbox(f'Select the {attribute}',list, key=key)
        key += 1
        PN = PN + value

    st.header(PN)  

    # Help Tool
    

    with st.sidebar:
        
        # Describe the tool
        st.header("Help Tool")
        st.caption("Describe the product your are looking for (color, voltage, etc.) to find its series name")
        
        # Select box to choose product family
        st.write(f'Product Family : {family}')
      
        # Filter data based on selected family
        data_family_filter = data[data["Attribute group"]==f'attributes_{family}']

        row1_1, row1_2 = st.columns((1,1))

        with row1_1:
            # First textbox
            input_1 = st.text_input('Insert your first need')
            # Extract all unique values that match the entered text. Limit = 100 to get all options
            options_1 = process.extract(input_1,data_family_filter['Recommended Label'].unique(),limit=100)
            # Create a list to store output of for loop
            result_1 = list()
            # Process.extract returns a sort of tuple with the matched word and the score
            # For good matches score >=90
            # Filter the matched word and store in the list
            for option in options_1:
                if option[1]>=90:
                    result_1 = result_1 + list(option[0].splitlines())
            
        # Same as above for the second textbox
        with row1_2:
            input_2 = st.text_input('Insert your second need')
            options_2 = process.extract(input_2,data_family_filter['Recommended Label'].unique(),limit=100)
            result_2 = list()
            for option in options_2:
                if option[1]>=90:
                    result_2 = result_2 + list(option[0].splitlines())

        # Combine the data based on the inputs
        data_filter_1 = data_family_filter[data_family_filter['Recommended Label'].isin(result_1)]
        series_available_1 = pd.DataFrame(data_filter_1['attribute'].str[:3].unique())

        data_filter_2 = data_family_filter[data_family_filter['Recommended Label'].isin(result_2)]
        series_available_2 = pd.DataFrame(data_filter_2['attribute'].str[:3].unique())

        if len(input_1)>0:
            if len(input_2)>0:
                series_available = pd.merge(series_available_1,series_available_2)
            else:
                series_available = series_available_1
        else:
            series_available = series_available_2
        
        # Print out the results
        series_choice = st.radio("The available product series are:",series_available)



if __name__ == '__main__':
    main()
 