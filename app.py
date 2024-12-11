import pandas as pd
import plotly.express as px
import streamlit as st

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
    required_columns = {'year', 'month', 'provider', 'status', 'count'}
    if required_columns.issubset(df.columns):
        # Create a dropdown for selecting provider
        providers = df['provider'].unique()
        selected_provider = st.selectbox("Select a provider", providers)

        # Add a dropdown for selecting year
        years = df['year'].unique()
        selected_year = st.selectbox("Select a year", years)

        # Filter data based on the selected provider and year
        filtered_df = df[(df['provider'] == selected_provider) & (df['year'] == selected_year)]

        # Create a line chart for variations based on month
        fig = px.line(
            filtered_df,
            x='month',
            y='count',
            color='status',
            title=f"Monthly Variations for Provider: {selected_provider} in {selected_year}",
            labels={
                'month': 'Month',
                'count': 'Count',
                'status': 'Status'
            },
            category_orders={
                'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            }
        )

        # Display the line chart
        st.plotly_chart(fig)

        # Create a pie chart for failure and success counts
        pie_fig = px.pie(
            filtered_df,
            names='status',
            values='count',
            title=f"Success and Failure Distribution for {selected_provider} in {selected_year}",
            labels={
                'status': 'Status',
                'count': 'Count'
            }
        )

        # Display the pie chart
        st.plotly_chart(pie_fig)
    else:
        st.error(f"The selected sheet does not have the required columns: {required_columns}")
