import pycountry
import pandas as pd
import plotly.express as px
import streamlit as st

# Function to convert country code to full name
def get_country_name(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except AttributeError:
        return code  # If the code is invalid, return it as-is

# Load the Excel file
uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")
if uploaded_file:
    # Load all sheets into a dictionary of DataFrames
    sheets = pd.read_excel(uploaded_file, sheet_name=None)

    # Select a sheet for visualization
    sheet_names = list(sheets.keys())
    selected_sheet = st.selectbox("Select a sheet to visualize", sheet_names)

    # Load the selected sheet
    df = sheets[selected_sheet]

    # Ensure the data has the expected columns
    required_columns = {'year', 'month', 'provider', 'country', 'status', 'count'}
    if required_columns.issubset(df.columns):
        # Convert country codes to full country names
        df['country'] = df['country'].apply(get_country_name)

        # Create a filter for year and provider
        years = df['year'].unique()
        selected_year = st.selectbox("Select a year", years)

        providers = df['provider'].unique()
        selected_provider = st.selectbox("Select a provider", providers)

        # Filter data based on selected year and provider
        filtered_df = df[(df['year'] == selected_year) & (df['provider'] == selected_provider)]

        # Ensure months are ordered correctly for plotting
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        filtered_df['month'] = pd.Categorical(filtered_df['month'], categories=month_order, ordered=True)

        # Create a summary of counts for failures and success per provider per month and year
        summary_data = (
            filtered_df.groupby(['year', 'month', 'provider', 'status'])['count']
            .sum()
            .reset_index()
        )

        # Calculate total counts per month and provider
        total_counts = (
            filtered_df.groupby(['year', 'month', 'provider'])['count']
            .sum()
            .reset_index()
            .rename(columns={'count': 'total_count'})
        )

        # Merge the total counts with the summary data
        expanded_summary = pd.merge(summary_data, total_counts, on=['year', 'month', 'provider'])

        # Calculate the percentage of each status (PASSED, FAILED) per month/provider
        expanded_summary['percentage'] = expanded_summary['count'] / expanded_summary['total_count'] * 100

        # Create two columns for layout with increased width
        col1, col2 = st.columns([1, 2])  # Left column (data) and right column (graph)

        # In the left column, display the expanded summary data with wider table
        with col1:
            st.write("<style>div.stDataFrame {width: 100%; max-width: 1200px; margin-bottom: 30px;}</style>", unsafe_allow_html=True)
            st.write("Expanded Summary Data", expanded_summary)

        # In the right column, display the line graph with larger space
        with col2:
            st.write("<style>div.plotly-graph-div {margin-bottom: 30px;}</style>", unsafe_allow_html=True)
            
            # Create a simple line graph for fail and pass per provider over months
            line_fig = px.line(
                expanded_summary,
                x='month',
                y='count',
                color='status',
                line_group='provider',
                title=f"Failures and Success for {selected_provider} in {selected_year}",
                labels={
                    'month': 'Month',
                    'count': 'Count',
                    'status': 'Status',
                    'provider': 'Provider',
                    'total_count': 'Total Count',
                    'percentage': 'Percentage'
                },
                category_orders={
                    'month': month_order  # Ensure months are in the correct order
                }
            )

            st.plotly_chart(line_fig)

        # ================================
        # New Section for Pass/Fail by Country
        # ================================
        st.write("### Pass and Fail Counts per Country for Selected Provider")
        
        # Filter the data to show counts per country
        country_data = (
            filtered_df.groupby(['country', 'status'])['count']
            .sum()
            .reset_index()
        )
        
        # Create a bar chart for pass/fail per country for the selected provider
        country_fig = px.bar(
            country_data,
            x='country',
            y='count',
            color='status',
            title=f"Pass and Fail Counts per Country for {selected_provider} in {selected_year}",
            labels={
                'country': 'Country',
                'count': 'Count',
                'status': 'Status'
            },
            barmode='stack'  # Stacked bar chart to show pass/fail side-by-side
        )

        st.plotly_chart(country_fig)

        # ================================
        # New Section for Data Behind the Graphs (Tables)
        # ================================
        st.write("### Data Behind the Graphs")
        
        # Table for Pass and Fail Counts per Country
        st.write("#### Pass and Fail Counts per Country")
        st.write(country_data)

    else:
        st.error(f"The selected sheet does not have the required columns: {required_columns}")
