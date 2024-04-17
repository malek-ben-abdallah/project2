
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# -*- coding: utf-8 -*-
"""
##### Author     : Malek Ben Abdallah
"""


import streamlit as st
import pandas as pd
import numpy as np

import plotly as py


#from plotly.offline import iplot
#import chart_studio.plotly as py
import plotly.figure_factory as ff
import plotly.express as px
import pycountry  

import country_converter 

import plotly.graph_objs as go
#from wordcloud import WordCloud

st.title('project')

df = pd.read_csv("Data/ds_salaries.csv", index_col=[0])
#st.write(data) #displays the table of data

#Created on Thu Sep 22 2022




    
    
    
#Converting country codes to country names for employee_residence and company_location
resi_country_list = []
comp_country_list = []
for country_code in df.employee_residence:
    resi_country_list.append(pycountry.countries.get(alpha_2=country_code).name)

for country_code in df.company_location:
    comp_country_list.append(pycountry.countries.get(alpha_2=country_code).name)

df['employee_residence'] = resi_country_list
df['company_location'] = comp_country_list




#Replacing some of the values to understand the graphs clearly
df.remote_ratio.replace([100,50,0], ['Remote', 'Hybrid' ,'On-site'],inplace = True)
df.experience_level.replace(['EN','MI','SE', 'EX'], ['Entry', 'Mid', 'Senior', 'Executive'], inplace = True)
df.company_size.replace(['L','M','S'], ['Large', 'Medium', 'Small'], inplace = True)

# Add subholder to see the raw data on your page 
# add a toggle to checkbox to see the data 
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df)

st.header('Exploratory Data Analysis')
st.markdown('In this section, we will explore the dataset to extract some useful insights.')
st.subheader('1- Top 10 Jobs')



st.write('There are', df['job_title'].value_counts().size, 'job titles in the dataset')
top10_job_title = df['job_title'].value_counts()[:10]
fig = px.bar(y=top10_job_title.values, 
             x=top10_job_title.index, 
             color = top10_job_title.index,
             color_discrete_sequence=px.colors.sequential.Magenta_r  ,
             text=top10_job_title.values,
             title= 'Top 10 Job Titles',
             template= 'plotly_dark' )
fig.update_layout(
    xaxis_title="Job Titles",
    yaxis_title="count",
    font = dict(size=13,family="Franklin Gothic"))

st.plotly_chart(fig)

st.markdown(' => **Job market is mostly dominated by Data Scientists,Data Engineers, Data Analysts, and Machine Learning Engineers.**')

#/2 
st.subheader('2-Employee Location Distribution Map')

converted_country = country_converter.convert(names=df['employee_residence'], to="ISO3")
df['employee_residence'] = converted_country
residence = df['employee_residence'].value_counts()
fig = px.choropleth(locations=residence.index,
                    color=residence.values,
                    color_continuous_scale=px.colors.sequential.Sunsetdark  ,
                    title = 'Employee Loaction Distribution Map')

st.plotly_chart(fig)

st.markdown(' => **From the map above we can conclude that Data science jobs are mostly common in the United States with over 300 job entries then less in Britain, canada and india.**')

#/3
st.subheader('3-Salary Distribution')

fig = px.box(y=df['salary_in_usd'],template= 'plotly_dark', title = 'Salary in USD')
fig.update_layout(font = dict(size=17))
st.write(fig)

st.markdown('**=> Most employees are getting paid around 100,000 USD.**') 

st.markdown('**=> Higher salaries are few especially over 300,000 USD.**')

st.markdown('**=> We have an outliers of 600,000 USD.**')

#/4
st.subheader('4-Experience_level distribution')

grouped_size = df['experience_level'].value_counts()


fig = px.bar(df, x=grouped_size.values, y=grouped_size.index,color = grouped_size.index,
             color_discrete_sequence=px.colors.sequential.Sunset_r,   title= 'Distribution of experience_level')

fig.update_layout(
    yaxis_title="experience_level",
    xaxis_title=" Count")

st.plotly_chart(fig)

st.markdown('**Number of senior and mid-level employees are the highest in the dataset.**')
st.markdown('**Meanwhile, the number of junior-level and expert-level employees is relatively low.**')


#/5
st.subheader('5-Experience level VS Salary')

fig=px.scatter(df, x = 'salary_in_usd', y = 'experience_level', size = 'salary_in_usd', hover_name = 'job_title', color = 'job_title', 
           color_discrete_sequence=px.colors.qualitative.Alphabet, template = 'plotly_dark',
           animation_frame = 'work_year', title = 'Experience level VS Salary').update_yaxes(categoryarray = ['Entry', 'Mid', 'Senior', 'Executive'])

st.plotly_chart(fig)
st.markdown('**Employees with higher experience get higher salaries So we conclude that the salary and Experience level have a positive correlation**')
st.markdown('**In 2020 the salary increase between Mid-level and Entry-level positions are not that important compared with the mid and the senior position**')



#/5+

job_list = ["All"]
with open("Data/job_names.txt") as f:
    for line in f:
        job_list.append(line.replace("'","").split(",")[0].strip())

st.subheader("Data Science Salaries by Job")



option = st.selectbox(
     'Please choose a data science job',
     job_list)

if option != "All":
    fig = px.box(df[df["job_title"] == option], x="experience_level", y="salary_in_usd", points="all",
                 title="Average annual salaries in $ of " + option + " by experience level")
    st.plotly_chart(fig)

    

    
else:
    fig = px.box(df, x="experience_level", y="salary_in_usd", points="all",
                 title="Average annual salaries in $ of " + option + " by experience level")
    st.plotly_chart(fig)





#/6
st.subheader('6-Company size')

grouped_size = df['company_size'].value_counts()

fig = px.pie(values=grouped_size.values, 
             names=grouped_size.index, 
             color = grouped_size.index,
             color_discrete_sequence=px.colors.sequential.Purpor_r,
           title= 'Distribution of Company Size')

st.write(fig)

st.markdown('**1. More than half of the data science jobs are posted by Medium size companies (53.7%) this is probably because most of the companies are medium size.**')
st.markdown('**2. Almost third of the data science jobs are posted by Large size companies.**')
st.markdown("**3. Meanwhile, small size companies may not require a data scientist or any data science-related employee that's why it has the least percentage**")




#/7
st.subheader('7-Employment type')
fig= px.histogram(df, x = 'employment_type',histnorm = 'percent',
             text_auto = '.2f',template = 'plotly_dark', title = 'Precentage of Employment Types')

st.write(fig)

st.markdown('**1. Full-time employees are the highest among others (96.9%)**')
st.markdown('**2. Meanwhile, the number of part-time, contract and freelance employees is very low**')
st.markdown("**3. This can be explained that most of the data science jobs require afull-time position**")


#/8
st.subheader('8- Work Type')





fig= px.histogram(df, x = 'work_year',color = 'remote_ratio', barmode = 'group',color_discrete_sequence=px.colors.qualitative.Pastel,
             template = 'plotly_dark',title='Count of each Work Type')

st.write(fig)


st.markdown('**1. Remote work type is the highest during the 3 years**')
st.markdown('**2. This may be explained by the covid pandemic because during these years the remote working become the solution and a lot of companies decided to keep working remotely even after the pandemic**')




st.subheader('You Can Further Visualize Elements of the Dataset by Selecting an Option Below')



#adding a side bar selection box for convenience
option = st.selectbox(
    'What Data Would You like to Visualize',
    ('Categorical (<20 categories)', 'Categorical (>20)', 'Numerical (Discrete)', 'Numerical (Continuous)', 'Treemap')
    ) 



# sorting by categorical colums with less than 20 categories
cat_feature1=[feature for feature in df.columns if df[feature].dtype=='O' and len(df[feature].unique())<20]

#over 20 categories columns
cat_feature2=[feature for feature in df.columns if df[feature].dtype=='O' and len(df[feature].unique())>20]

#discrete & continuous values for numerical columns
dis_feature=[feature for feature in df.columns if len(df[feature].unique())<20 and df[feature].dtype!='O']

cont_feature=[feature for feature in df.columns if len(df[feature].unique())>20 and df[feature].dtype!='O']



#plotting with streamlit
if option == 'Categorical (<20 categories)':
  for feature in cat_feature1:
    fig = px.histogram(df, x = feature)
    #fig.show()
    st.plotly_chart(fig, use_container_width = True)
elif option == 'Categorical (>20)':
  for feature in cat_feature2:
    fig = px.bar(df, y = feature, x = 'salary')
    st.plotly_chart(fig, use_container_width = True)
elif option == 'Numerical (Discrete)':
  for feature in dis_feature:
    fig2 = px.histogram(df, x=feature)
    st.plotly_chart(fig2, use_container_width = True)
elif option == 'Numerical (Continuous)':
  for feature in cont_feature:
    fig = px.box(df, x = feature)
    st.plotly_chart(fig, use_container_width = True)
  for feature in cont_feature:
    fig1 = px.histogram(df, x= feature, color="experience_level",   marginal="box", # can be `box`, `violin`
                         hover_data=df.columns)
    st.plotly_chart(fig1, use_container_width = True)
elif option == 'Treemap':
  fig=px.treemap(df,path=[px.Constant('Job Roles'),'job_title','company_location','experience_level'],template='ggplot2',hover_name='job_title',title='<b>TreeMap of Different Roles in Data Science with Experience Level')
  fig.update_traces(root_color='lightgrey')
  st.plotly_chart(fig)
  
  
  














