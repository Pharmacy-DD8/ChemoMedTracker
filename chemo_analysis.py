import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data with correct headers
df = pd.read_excel('SampleChemoData.ods', engine='odf', header=1)

# Rename the 'Unnamed: 0' column to 'Drug'
df.rename(columns={df.columns[0]: 'Drug'}, inplace=True)

# Set 'Drug' as the index
df.set_index('Drug', inplace=True)

# Remove time from column names (convert to date only)
df.columns = pd.to_datetime(df.columns, errors='coerce').strftime('%Y-%m-%d')

# Streamlit App
st.title('Chemo Med Inventory')

# Identify the second column
if len(df.columns) > 1:
    second_column = df.columns[1]
else:
    second_column = None

# Show the current count table (second column)
st.subheader(f'Current Count (Date: {second_column})')
if second_column and second_column in df.columns:
    current_count = df[second_column]
    st.dataframe(current_count)
else:
    st.write('No data available for the second column')

# Collapsible Weekly Count Section
with st.expander('Weekly Count'):
    st.dataframe(df)

# Select a drug to analyze
drug = st.selectbox('Select a drug to analyze', df.index.unique())

# Filter data for the selected drug
filtered_data = df.loc[drug]

st.subheader(f'Data for {drug}')

# Create columns for side-by-side layout
col1, col2 = st.columns([2, 1])  # Adjust column widths as needed

with col1:
    st.dataframe(filtered_data)

with col2:
    st.subheader('Statistics')
    if not filtered_data.empty:
        mean_value = filtered_data.mean().round(2)
        max_value = filtered_data.max()
        min_value = filtered_data.min()

        st.write(f'Mean quantity: {mean_value}')
        st.write(f'Max quantity: {max_value}')
        st.write(f'Min quantity: {min_value}')
    else:
        st.write("No data available for the selected drug.")

# Plotting using Matplotlib (Bar Graph)
st.subheader(f'Quantity of {drug} vials')
fig, ax = plt.subplots()

# Plot the data as a bar graph
bars = filtered_data.T.plot(kind='bar', ax=ax)  # Transpose to plot dates on x-axis
ax.set_xlabel('Date')
ax.set_ylabel('Quantity')
ax.set_title(f'Quantity of {drug} vials')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Get the max value from the data for setting y-axis limit
max_quantity = filtered_data.max()
# Set y-axis limit to a bit larger than the max value
ax.set_ylim(0, max_quantity + (0.2 * max_quantity))  # 20% more than max value

# Annotate each bar with the number of vials
for bar in bars.containers[0]:
    height = bar.get_height()
    ax.annotate(f'{int(height)}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')

# Display the plot
st.pyplot(fig)

# Analyze the change in quantity
st.subheader(f'Change Analysis for {drug}')

# Check if the filtered_data is not empty
if not filtered_data.empty:
    # Calculate the difference between consecutive dates
    daily_changes = filtered_data.diff().dropna()

    # Calculate statistics for changes
    mean_change = daily_changes.mean()
    max_change = daily_changes.max()
    min_change = daily_changes.min()

    # Generate a textual description of the changes
    st.write(f'Analysis of the quantity changes for {drug}:')
    
    if not daily_changes.empty:
        st.write(f'Over the period, the quantity of {drug} vials has fluctuated.')
        st.write(f'The average daily change in quantity is {mean_change:.2f} vials.')
        st.write(f'The maximum increase observed in a day was {max_change:.2f} vials, while the maximum decrease was {-min_change:.2f} vials.')
        
        if mean_change > 0:
            st.write('Overall, there has been an increasing trend in the quantity of vials.')
        elif mean_change < 0:
            st.write('Overall, there has been a decreasing trend in the quantity of vials.')
        else:
            st.write('The quantity of vials has remained relatively stable with no significant overall trend.')
    else:
        st.write('Not enough data to analyze the change.')
else:
    st.write("No data available for the selected drug.")
