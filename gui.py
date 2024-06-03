import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Make the layout wider
st.set_page_config(layout="wide")

def generate_income_plot(df):
    """
    Input: dataframe (csv file)

    Output: interactive figure comparing the annual salaries of different positions held at UW from 2012-2021

    Currently a line plot is being used but we can change it to a scatter plot, and adjust size of the markers to reflect salary.

    Able to click on specific job types in the legend, which will exclude that data and regenerate a new plot.
    That way, you are able to "zoom" in and compare the data for those with very low salaries.
    """
    # Reshape the DataFrame to long format
    df_long = df.melt(id_vars=['Year'], var_name='Job Type', value_name='Annual Salary')
    df_long = df_long[df_long['Annual Salary'] != 0]
    # Plotting
    fig = px.line(df_long, x='Year', y='Annual Salary', color='Job Type',
                  #size='Annual Salary', color_continuous_scale='purp',
                  color_discrete_sequence=px.colors.qualitative.Plotly,
                  title='Annual Salaries of Different Positions at the University of Washington: 2012-2021',
                  labels={'Annual Salary': 'Annual Salary ($)'},
                  hover_name='Job Type',  # job type on hover
                  hover_data={'Year': True, 'Annual Salary': True},  # display year and salary when hovered over
                  #opacity=0.7,  # marker opacity, if using scatter plot
                  render_mode='webgl',  # webgl for faster rendering
                  markers = True
                    )
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='black')))  # Set marker outline to black
    fig.update_layout(
        width=600,  # Set the width of the plot
        height=900,  # Set the height of the plot
        xaxis_title='Year',  # Set the x-axis title
        yaxis_title='Annual Salary ($)',  # Set the y-axis title
        font=dict(size=14),  # Set the font sizes
        xaxis=dict(tickmode='linear') #tick marks
    )

    st.plotly_chart(fig, use_container_width=True)
# how
income_df = pd.read_csv('processed_data_FP2.csv')
col_df = pd.read_csv("seattle_col.csv", index_col=0)
#income_df = income_df.drop(columns=['Unnamed: 8'])


# Job titles
job_titles = income_df.columns.tolist()[1:]

# Year salaries
income_df.columns = income_df.columns.str.strip()
year_list = income_df.iloc[:, 0].tolist()

# Cost values
costs = pd.read_csv("seattle_col.csv")

st.title('How far does my University of Washington salary go?')

tab1, tab2 = st.tabs(["Yearly Savings Calculator", "Cost of Living in Seattle"])
with tab1:
    st.header("What we have done")
    st.write('We built a cost calculator to showcase the stark economic differences between the different occupations at UW over time. From the highest paid position of head football coach, to the lowest paid position of ASEs reasearch associates/teaching assistants (abbreviated RA/TA), we found the most consistent data between the years 2012 and 2021 to drive our calculations.')

    st.write('As ASEs, we wanted to explore how our salaries and cost of living affect our overall savings, and how that compares to other positions. By finding data over a range of years, we are also able to see how our salaries change with time, and, consequently, how our savings change. Do our savings decrease as the years go on? In other words, is the cost of living increasing faster than our salaries? Our calculator seeks to organize typical monthly costs with your average income, and calculate the expected savings per month.')

    st.header("The Data")
    st.write('The data was found from multiple sources: World Population Review, University of Washington Salaries, and USDA Food Expenditure. We chose data that was found for all years 2012-2021, and that we felt are the most impactful on our savings. This includes amount spent on rent, groceries, cheese, and cappucinos (or whatever your choice of coffee order).')

    st.write('We plotted the annual salaries of each position below. The user is able to hover over points to learn more about the specific salary, year, and position. The user can also click on positions in the legend to exclude them from the plot, thus enabling closer inspection of the lower paid positions.')

    st.header("The Calculator")
    # Initialize session state \
    if 'salary' not in st.session_state:
        st.session_state.salary = 0.
    if 'year' not in st.session_state:
        st.session_state.year = 2012
    if 'job' not in st.session_state:
        st.session_state.job = None
    if 'rent' not in st.session_state:
        st.session_state.rent = 0.
    if 'grocery' not in st.session_state:
        st.session_state.grocery = 0.
    if 'cheese' not in st.session_state:
        st.session_state.cheese = 0.
    if 'cappa' not in st.session_state:
        st.session_state.cappa = 0.

        # Callback to handle salary update when job title is selected
    def update_salary():
       # Retrieve the selected year and job directly from session state
        selected_year = st.session_state.year
        selected_job = st.session_state.job

        # Set 'Year' as the index temporarily
        income_df.set_index('Year', inplace=True)

        # Access the salary value
        salary = income_df.loc[selected_year, selected_job]
        st.session_state.salary = float(salary)
        st.session_state.rent = col_df.loc[selected_year, "1bed_city"]
        st.session_state.grocery = col_df.loc[selected_year, "Groceries"]
        st.session_state.cheese = col_df.loc[selected_year, "LocalCheese"]
        st.session_state.cappa = col_df.loc[selected_year, "Cappucino"]

        # Reset the index
        income_df.reset_index(inplace=True)


    col1, col2 = st.columns((1,3))

    with col1:
        st.subheader('Enter Information')
        st.write('First, select the job you want to base your savings calculation on. The calculator will autopopulate based on the average cost of item in Seattle in that year. Once finished, the calculator will output your expected ANNUAL savings. You can also manually put in values for any items and see the impact on savings.')

        # Job title selection
        job = st.selectbox(
            "Job Title",
            options=job_titles,
            index=0 if job_titles else None,
            on_change=update_salary,
            key='job',
            #placeholder="Select Job Title...",
        )
        # year selection
        year = st.selectbox(
            "Year",
            options=year_list,
            index=0 if year_list else None,
            on_change=update_salary,
            key='year',
        )
        # Salary input
        salary = st.number_input(
            "Salary",
            value=st.session_state.salary,
            min_value=0., max_value=100000000., step=1000.
        )
        rent = st.number_input(
            "Rent",
            value=st.session_state.rent,
            min_value=0., max_value=100000000., step=1000.,
        )
        groceries = st.number_input(
            "Groceries",
            value=st.session_state.grocery,
            min_value=0., max_value=100000000., step=st.session_state.grocery
        )
        cheese = st.number_input(
            "Cheese",
            value=st.session_state.cheese,
            min_value=0., max_value=100000000., step=st.session_state.cheese,
        )
        cappa = st.number_input(
            "Cappucinos",
            value=st.session_state.cappa,
            min_value=0., max_value=100000000., step=st.session_state.cappa,
        )
        additional = st.number_input("Additional Expenses", value=500., min_value=0., max_value=1000000., step=100.)

        monthly_savings = round((salary/12) - (rent + groceries + cheese*2 + cappa*8 + additional), 2)
        total_savings = round(salary - (rent*12 + groceries*12 + cheese*30 + cappa*100 + additional*12), 2)

        if monthly_savings > 0:
            st.markdown(f"<p style='color:green;font-size: larger;'>Your monthly savings is: ${monthly_savings:,.2f}</p>", unsafe_allow_html=True)
        if monthly_savings < 0:
            st.markdown(f"<p style='color:red;font-size: larger;'>Your monthly savings is: ${monthly_savings:,.2f}</p>", unsafe_allow_html=True)

        if total_savings > 0:
            st.markdown(f"<p style='color:green;font-size: larger;'>Your total annual savings is: ${total_savings:,.2f}</p>", unsafe_allow_html=True)
        if total_savings < 0:
            st.markdown(f"<p style='color:red;font-size: larger;'>Your total annual savings is: ${total_savings:,.2f}</p>", unsafe_allow_html=True)
    st.write('*Note: It is assumed that on average, a person will buy two cups of coffee a week, and purchase about 1 cheese block every 2 weeks.*')

    with col2:
        generate_income_plot(income_df)
    # Streamlit code to display the plot


with tab2:
    st.subheader("Graphical Visualization of Annual Costs")
    st.write('We built a way to visualize the costs of specific items alongside a chosen annual salary. As the user, you first need to select the job type you want visualized on the plot, and then select the costs you want to graph alongside the job type income. A range of years can be selected using the dual slider.')
    st.subheader('The Plot')
    st.write('The bar plots generated represent historical average annual costs spent by an individual living in Seattle for common costs: rent, groceries, restaurants/eating out, basic utilities (water, heating, electricity), internet (assuming unlimited data, 60 mbps).')
    st.write('The star points generated represents the annual salary of the selected job type, and is stacked on the same plot as the costs. This allows for comparison in how the essential costs vs. income change over time for the same job. *Other costs such as leisure spending, transportation, medical, retirement, are not considered.*')


    import altair as alt
    import pandas as pd
    import streamlit as st

    # Cost values
    data = pd.read_csv("annual_costs.csv")
    data.columns = data.columns.str.strip()

    # Create a new DataFrame for income data
    income_df.columns = income_df.columns.str.strip()

    # Streamlit UI
    st.title("Salary Analysis Over Years")

    # Selectbox for job/column heading options
    default_index = len(job_titles) - 1
    selected_job = st.selectbox("Select Job", job_titles, index=default_index)

    # Year selection range slider
    selected_years = st.slider("Select Year Range", min_value=int(income_df['Year'].min()), max_value=int(income_df['Year'].max()), value=(int(income_df['Year'].min()), int(income_df['Year'].max())), step=1)

    # Create two columns
    left_column, right_column = st.columns([1, 2])

    # Checkbox for each cost column
    columns = data.columns.tolist()[1:]
    selected_columns = []

    left_column.write("Select Costs to Include:")

    # Determine number of rows for checkboxes
    num_columns = 1

    # Create inner columns for checkboxes within the left column
    checkbox_columns = left_column.columns(num_columns)

    # Distribute checkboxes across columns
    for i, column in enumerate(columns):
        col_idx = i % num_columns
        if checkbox_columns[col_idx].checkbox(column, value=False):
            selected_columns.append(column)

    # Filter data based on selected year range
    filtered_data = data[(data['Year'] >= selected_years[0]) & (data['Year'] <= selected_years[1])]
    filtered_income = income_df[(income_df['Year'] >= selected_years[0]) & (income_df['Year'] <= selected_years[1])]

    # Melt the DataFrame for Altair
    melted_data = filtered_data.melt(id_vars='Year', value_vars=selected_columns, var_name='Category', value_name='Cost')
    melted_income = filtered_income.melt(id_vars='Year', value_vars=selected_job, var_name='Category', value_name='Cost')

    # Create the stacked bar chart using Altair
    bar_chart = alt.Chart(melted_data).mark_bar().encode(
        x=alt.X('Year:N', title='Year', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('sum(Cost):Q', title='Dollars'),
        color=alt.Color('Category:N', scale=alt.Scale(scheme='set2')),  # Change the color scheme here
        tooltip=['Year', 'Category', 'Cost']
    ).properties(
        width=900,
        height=500
    )

    # Create the point chart for melted_income
    point_chart = alt.Chart(melted_income).mark_point(
        shape='M0,.5L.6,.8L.5,.1L1,-.3L.3,-.4L0,-1L-.3,-.4L-1,-.3L-.5,.1L-.6,.8L0,.5Z', filled=True, size=400
    ).encode(
        x=alt.X('Year:N', title='Year'),
        y=alt.Y('sum(Cost):Q', title='Dollars'),
        tooltip=['Year', 'Category', 'Cost'],
        color=alt.value('gold'),  # Specify color directly instead of in mark_point
        stroke=alt.value('black')  # Add a black outline
    )

    # Combine both charts
    chart = (bar_chart + point_chart).resolve_scale(y='shared')

    # Display the chart in the right column
    right_column.altair_chart(chart)
