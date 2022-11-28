import streamlit as st
import pandas as pd
import plotly.offline as pyo
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from numpy import inf

departments = pd.read_csv('departments.csv')
dept_employees = pd.read_csv('dept_emp.csv')
dept_manager = pd.read_csv('dept_manager.csv')
employees = pd.read_csv('employees.csv')
salaries = pd.read_csv('salaries.csv')
titles = pd.read_csv('titles.csv')


def clean_row(row):
    if row != ['']:
        return row[-1]+'-'+row[-2]+'-'+row[-3]
    else:
        return "Currently Active"


st.set_page_config(page_title='Employees', page_icon='👥', layout='wide')


st.title('👥Employees')




#Salaries of Active Employees   
salaries_active_employees = salaries[salaries['to_date'].astype(str).str.contains('9999')]

#adding department name to department_employees and department_manager tables
dept_employees = dept_employees.merge(departments, left_on='dept_no', right_on='dept_no')
dept_manager= dept_manager.merge(departments, left_on='dept_no', right_on='dept_no')

try:
    selected_employee = st.number_input("Select the Employee:", 10001, 499999)

    col1, col2, col3 = st.columns(3)
    with col1:
    
        #Work History
        work_history = dept_employees
        work_history = work_history[work_history['emp_no'] == selected_employee]
        work_history['to_date'] = work_history['to_date'].astype(str).str.replace('01-01-9999', '')
        work_history['from_date'] = pd.to_datetime(work_history['from_date'], format="%d-%m-%Y", infer_datetime_format=True)
        work_history['to_date'] = work_history['to_date'].str.split('-').apply(clean_row)
        work_history = work_history.sort_values(by='from_date')
        work_history["from_date"] = work_history["from_date"] .dt.strftime("%Y-%m-%d")
        work_history_output = work_history[['dept_name', 'from_date',	'to_date']].set_axis(["Department Name", "From", "To"], axis=1).reset_index().drop(['index'], axis=1)

#workHours Graph

        work_workHours = salaries[salaries['emp_no'] == selected_employee]
        work_workHours['to_date'] = work_workHours['to_date'].astype(str).str.replace('01-01-9999', '')
        work_workHours['from_date'] = pd.to_datetime(work_workHours['from_date'], infer_datetime_format=True)
        work_workHours['to_date'] = work_workHours['to_date'].str.split('-').apply(clean_row)
        work_workHours['from_date_rank'] = work_workHours['from_date'].rank()



#KPIs
#FullName
    column1, column2, column3, column4, column5 = st.columns(5)
    with column1:
        first_name = employees[employees['emp_no'] == selected_employee].first_name.iloc[-1]
        last_name = employees[employees['emp_no'] == selected_employee].last_name.iloc[-1]
        st.metric(label="📛 Name", value=f"{first_name} {last_name}")

    with column2:
        emp_gender = employees[employees['emp_no'] == selected_employee].gender.iloc[-1]
        if emp_gender == 'F':
            st.metric(label="👩🏻Gender", value="Female")
        else:
            st.metric(label="🧑🏻Gender", value="Male")

    with column3:
    #Department
        working_department = work_history.reset_index().drop(['index'], axis=1).iloc[-1].dept_name
        st.metric(label="💻Department", value=f"{working_department}")

    with column4:
    #Date of Birth
        dob = employees[employees['emp_no'] == selected_employee]['birth_date'].iloc[-1]
        st.metric(label="👶Date of Birth", value=f"{dob}")

    with column5:
    #Current workHours
       try:
            current_workHours = work_workHours.iloc[-1].workHours
            st.metric(label="💵 Current workHours", value=f"mins {current_workHours}")
       except:
           st.metric(label="💵 Current workHours", value=f"workHours Unavailable")




    st.caption("Employees number range between 10001 and 499999")




    if work_workHours.empty:
        st.write('Sorry! No workHours records found')
    else:
        work_workHours[['workHours', 'from_date', 'to_date']] \
            .set_axis(['workHours', 'From', 'To'], axis=1)

        fig = go.Figure([go.Scatter(x=work_workHours['from_date_rank'], y=work_workHours['workHours'], mode='lines+markers', marker={'color': 'rgb(255, 51, 51)'}, 
        name='', hovertemplate='<br>Year: %{x}<br>workHours: %{y}<br>')])


        fig.update_layout(
        title = "workHours Chart",
        xaxis=dict(title='Year', showgrid =False),
        yaxis=dict(title='workHours', showgrid =False),
        title_x=0.5,
        autosize=True,
        paper_bgcolor="#00172B",
        plot_bgcolor="#00172B")

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("Employee's Work History")
        st.table(work_history_output)
        

        st.markdown("workHours Records")

        work_workHours["from_date"] = work_workHours["from_date"] .dt.strftime("%Y-%m-%d")
        work_workHours['workHours_py'] = work_workHours['workHours'].shift().fillna(0)
        work_workHours['workHours_growth'] = work_workHours['workHours'] - work_workHours['workHours_py']
        work_workHours['workHours_growth_in_perc'] = round((work_workHours['workHours_growth']/work_workHours['workHours_py'])*100, 2)
        work_workHours['workHours_growth_in_perc'] = work_workHours['workHours_growth_in_perc'].replace(inf, 0)
        work_workHours["from_date_rank"] = work_workHours["from_date_rank"].astype(int)

        df_workHours = work_workHours[["workHours", "from_date", "to_date", "workHours_growth", "workHours_growth_in_perc"]] \
                    .set_axis(["workHours", "From", "To", "workHours Growth", "workHours Growth in %"], axis=1)

        st.table(df_workHours)





except ValueError:
    st.error("Please enter a valid employee number")
    

