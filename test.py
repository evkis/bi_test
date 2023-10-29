import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import plotly.express as px
from plotly import graph_objects as go
import streamlit as st
import warnings
import datetime as dt

warnings.filterwarnings('ignore')

#removing the limit on the number of columns
pd.set_option('display.max_columns', None)

# removing the restriction on the width of columns
pd.set_option('display.max_colwidth', None)

# ignore warnings
pd.set_option('chained_assignment', None)

st.set_page_config(page_title="test bi-consult", page_icon=":bar_chart:",layout="wide")

st.title(":bar_chart: Тестовое задание BI-consult")

st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

col1, col2 = st.columns((2))

with col1:
    st.markdown("[сайт компании bi-consult](https://www.biconsult.ru)")
with col2:
    st.markdown("[ссылка на файлы тестового задания](https://drive.google.com/drive/folders/1akG3cUNLR7pFAQtbmCmbqz5URHvSkqlT?usp=sharing)")
#google links
url_cat='https://drive.google.com/file/d/1n35BgALQjOVPRmCWvfU8UyV5snGgKmPd/view?usp=drive_link'
url_prod='https://drive.google.com/file/d/1ojXUd0RCH-7pMJoHOz86wGR4qKTydICb/view?usp=drive_link'
url_cust='https://drive.google.com/file/d/1gsqyheBCM-S6p2Z-1jQwRXot7tQG3BBP/view?usp=drive_link'
url_o='https://drive.google.com/file/d/1aTf1EEFmF-xChD38y_Ff-URXtE_SUW3Q/view?usp=drive_link'
url_od='https://drive.google.com/file/d/14mBcFdEJE6Vz3gvufHjXGYqPAPJVfWm8/view?usp=drive_link'
url_emp='https://docs.google.com/spreadsheets/d/1Us2PnqqpS7DYDkEsEwnmYJIFKL1dP71N/edit?usp=drive_link&ouid=109000048942920439312&rtpof=true&sd=true'

# reading csv from google and saving to df 
@st.cache_data
def read_gcsv(url):
    file_id=url.split('/')[-2]
    dwn_url='https://drive.google.com/uc?id=' + file_id
    df = pd.read_csv(dwn_url, sep=',')
    return df
# reading xls from google and saving to df 
@st.cache_data
def read_gxls(url,a):
    file_id=url.split('/')[-2]
    dwn_url='https://drive.google.com/uc?id=' + file_id
    df = pd.read_excel(dwn_url, sheet_name=a)
    return df
    
#applying functions

df_cat=read_gcsv(url_cat)
df_prod=read_gcsv(url_prod)
df_cust=read_gcsv(url_cust)
df_o=read_gcsv(url_o)
df_od=read_gcsv(url_od)
df_emp=read_gxls(url_emp,0)
df_emp2=read_gxls(url_emp,1)

def df_comb(df_cat,df_prod,df_cust,df_o,df_od,df_emp,df_emp2):
    df_products=df_prod.merge(df_cat,on='CategoryID',how='left')
    orders=df_od.merge(df_o,on='OrderID',how='left')
    orders_1=orders.merge(df_products,on='ProductID',how='left')
    orders_2=orders_1.merge(df_cust,on='CustomerID',how='left')
    df=df_emp.merge(df_emp2,on='Office',how='left')
    df['employee_name']=df['First Name']+' '+ df['Last Name']
    df.drop(['Last Name','First Name'],axis=1,inplace=True)
    df.rename(columns={'EmpID':'EmployeeID','Title':'emp_title', 'Office':'emp_office',\
                    'Address':'emp_address','City':'emp_city', 'Country':'emp_country'
                   },inplace=True)
    df_ini=orders_2.merge(df,on='EmployeeID',how='left')
    df_ini.drop(['ProductID','CustomerID','CustomerID','EmployeeID','CategoryID'],axis=1,inplace=True)
    df_ini["UnitPrice"] = df_ini["UnitPrice"].str.replace(",", ".")
    df_ini["UnitCost"] = df_ini["UnitCost"].str.replace(",", ".")
    df_ini["Discount"] = df_ini["Discount"].str.replace(",", ".")
    df_ini["UnitPrice"]=df_ini["UnitPrice"].astype('float')
    df_ini["UnitCost"] = df_ini["UnitCost"].astype('float')
    df_ini["Discount"] = df_ini["Discount"].astype('float')
    df_ini["OrderDate"]=pd.to_datetime(df_ini["OrderDate"])
    df_ini["month"]=df_ini["OrderDate"].dt.to_period("M")
    df_ini["year"]=df_ini["OrderDate"].dt.to_period("Y")
    return df_ini

df= df_comb(df_cat,df_prod,df_cust,df_o,df_od,df_emp,df_emp2)

with st.expander("Посмотреть/Скачать начальный комбинированный файл"):
            st.write(df.style.background_gradient(cmap="Blues"))
            csv = df.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "initial_data.csv", mime = "text/csv",
                               help = 'Нажмите, чтобы скачать файл CSV')

st.sidebar.header("Выберите фильтры: ")
start_date = df["OrderDate"].min()
end_date = df["OrderDate"].max()
date1=pd.to_datetime(st.sidebar.date_input("Начальная Дата", start_date))
date2=pd.to_datetime(st.sidebar.date_input("Конечная Дата", end_date))
df = df[(df["OrderDate"] >= date1) & (df["OrderDate"] <= date2)].copy()

country_order = st.sidebar.multiselect("Страна заказчика", df["Country"].unique())

if not country_order:
    df2 = df.copy() 
else:
    df2 = df[df["Country"].isin(country_order)]

city_order = st.sidebar.multiselect("Город заказчика", df2["City"].unique())

if not city_order:
    df3 = df2.copy() 
else:
    df3 = df2[df2["City"].isin(city_order)]

client_order = st.sidebar.multiselect("Заказчик", df3["CompanyName"].unique())

if not client_order:
    df4 = df3.copy() 
else:
    df4 = df3[df3["CompanyName"].isin(client_order)]

category_order = st.sidebar.multiselect("Категория Товара", df4["CategoryName"].unique())

if not category_order:
    df5 = df4.copy() 
else:
    df5 = df4[df4["CategoryName"].isin(category_order)]

product = st.sidebar.multiselect("Товар", df5["ProductName"].unique())

if not product:
    df6 = df5.copy() 
else:
    df6 = df5[df5["ProductName"].isin(product)]

emp_country = st.sidebar.multiselect("Страна сотрудника", df6["emp_country"].unique())

if not emp_country:
    df7 = df6.copy() 
else:
    df7 = df6[df6["emp_country"].isin(emp_country)]

emp_city = st.sidebar.multiselect("Город сотрудника", df7["emp_city"].unique())

if not emp_city:
    df8 = df7.copy() 
else:
    df8 = df7[df7["emp_city"].isin(emp_city)]

emp_office = st.sidebar.multiselect("Офис сотрудника", df8["emp_office"].unique())

if not emp_office:
    df9 = df8.copy() 
else:
    df9 = df8[df8["emp_office"].isin(emp_office)]

emp_title = st.sidebar.multiselect("Должность сотрудника", df9["emp_title"].unique())

if not emp_title:
    df10 = df9.copy() 
else:
    df10 = df9[df9["emp_title"].isin(emp_title)]

employee_name = st.sidebar.multiselect("Имя сотрудника", df10["employee_name"].unique())

if not employee_name:
    df11 = df10.copy() 
else:
    df11 = df10[df10["employee_name"].isin(employee_name)]

with st.expander("Посмотреть/Скачать отфильтрованный файл"):
            st.write(df11.style.background_gradient(cmap="Blues"))
            csv = df.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "filtered_data.csv", mime = "text/csv",
                               help = 'Нажмите, чтобы скачать файл CSV')

# объем продаж
volume_sales=df11['Quantity'].sum()

# Выручка
revenue=(df11['UnitPrice']*df11['Quantity']).sum()

#Себестоимость
cost= (df11['UnitCost']*df11['Quantity']).sum()

#Маржа
margin= revenue- cost

#Маржа процент
margin_percent= round((revenue- cost)*100/revenue, 2)

#наценка
extra_charge=round(margin*100/cost, 2)

#количество заказов

orders_number=df11['OrderID'].nunique()

# функция вычисления средневзвешенного значения

def w_avg(df, values, weights):
 d = df[values]
 w = df[weights]
 return (d * w).sum()/w.sum()

weight_avg= round (w_avg(df11,'Discount','Quantity'),2)

# Insert containers separated into tabs:
#tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
#tab1.write("this is tab 1")
#tab2.write("this is tab 2")
def format_currency(amount):
        return f"{amount:,.0f} $"
def format_per(amount):
        return f"{amount:} %"

st.markdown("## Основные финансовые показатели:")
cl1, cl2, cl3, cl4 = st.columns((4))

with cl1:
    st.write("Объем продаж:")
    st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{volume_sales}</p>", unsafe_allow_html=True)

with cl2:
    st.write("Выручка:")
    st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_currency(revenue)}</p>", unsafe_allow_html=True)
    
with cl3:
    st.write("Себестоимость:")
    st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_currency(cost)}</p>", unsafe_allow_html=True)

with cl4:
    st.write("Количество заказов:")
    st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{orders_number}</p>", unsafe_allow_html=True)   

cl5, cl6, cl7, cl8 =st.columns((4))

with cl5:
    st.write("Маржа:")
    st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_currency(margin)}</p>", unsafe_allow_html=True)

with cl6:
    st.write("Маржа %:")
    st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_per(margin_percent)}</p>", unsafe_allow_html=True)
    
with cl7:
    st.write("Наценка %:")
    st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_per(extra_charge)}</p>", unsafe_allow_html=True)
    
with cl8:
    st.write("Средневзвешенная скидка %:")
    st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_per(weight_avg)}</p>", unsafe_allow_html=True)

df11['revenue'] = df11['UnitPrice'] * df11['Quantity']
df11['cost'] = df11['UnitCost'] * df11['Quantity']
df11['margin']=df11['revenue']-df11['cost']
def summary(x):
        result = {
            'revenue_sum': x['revenue'].sum(),
            'quantity_sum': x['Quantity'].sum(),
            'cost_sum': x['cost'].sum(),
            'margin_sum': x['margin'].sum(),
            'w_avg': (x['Discount'] * x['Quantity']).sum()/x['Quantity'].sum()}
        return pd.Series(result).round(2)
        
grouped_df_category=df11.groupby(['CategoryName']).apply(summary).reset_index()
grouped_df_category['extra_charge']= round(grouped_df_category['margin_sum']*100/grouped_df_category['cost_sum'], 2)

grouped_df_category['quantity_sum'] = grouped_df_category['quantity_sum'].astype(float)
grouped_df_category['extra_charge'] = grouped_df_category['extra_charge'].astype(float)
grouped_df_category['w_avg'] = grouped_df_category['w_avg'].astype(float)

col1, col2 = st.columns((2))

with col1:
     st.subheader("Операционные показатели эффективности")
     tab1, tab2 = st.tabs(["Выручка и маржа по году", "Выручка и маржа по месяцу"])
     with tab1:
         # Рассчитаем выручку и стоимость
         data_grouped_year = df11.groupby('year')[['revenue', 'cost']].sum().reset_index()
         data_grouped_month = df11.groupby('month')[['revenue', 'cost']].sum().reset_index()
         data_grouped_year["year"]=data_grouped_year["year"].astype(str)
         data_grouped_month["month"]=data_grouped_month["month"].astype(str)
         data_grouped_year["margin"]=data_grouped_year["revenue"]-data_grouped_year["cost"]
         data_grouped_month["margin"]=data_grouped_month["revenue"]-data_grouped_month["cost"]
         data_grouped_year.rename(columns={'year': 'год','revenue': 'выручка', 'margin':'маржа'},inplace=True)
         data_grouped_month.rename(columns={'month': 'месяц','revenue': 'выручка', 'margin':'маржа'},inplace=True)
         data_grouped_year.drop('cost',axis=1,inplace=True)
         data_grouped_month.drop('cost',axis=1,inplace=True)
         # Создание столбчатой диаграммы
         fig = px.bar(data_grouped_year, x='год', 
                     y=['выручка', 'маржа'], labels={'variable':'переменная','value':'выручка'})

         # Настройка внешнего вида
         fig.update_layout(
                          xaxis_title='год',
                          yaxis_title='сумма в тысячах',
                          barmode='stack')

         # Отображение диаграммы
         st.plotly_chart(fig, use_container_width=True, height = 300)
         with st.expander("Посмотреть/Скачать файл"):
            st.write(data_grouped_year.style.background_gradient(cmap="Blues"))
            csv = data_grouped_year.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "data_grouped_year.csv", mime = "text/csv",
                               help = 'Нажмите, чтобы скачать файл CSV')
         
     with tab2:
         
         # Создание столбчатой диаграммы
         fig = px.bar(data_grouped_month, x='месяц', 
                     y=['выручка', 'маржа'], labels={'variable':'переменная','value':'выручка'})


         # Настройка внешнего вида
         fig.update_layout(
                          xaxis_title='месяц',
                          yaxis_title='сумма в тысячах',
                          barmode='stack')

         # Отображение диаграммы
         st.plotly_chart(fig, use_container_width=True, height = 300)
         with st.expander("Посмотреть/Скачать файл"):
            st.write(data_grouped_month.style.background_gradient(cmap="Blues"))
            csv = data_grouped_month.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "data_grouped_month.csv", mime = "text/csv",
                               help = 'Нажмите, чтобы скачать файл CSV')


with col2: 
    st.subheader("Продажи по категории")
    #fig=px.pie(grouped_df_category, values='revenue_sum', names='CategoryName')
    fig = go.Figure()
    fig = go.Figure(data=[go.Pie(labels=grouped_df_category['CategoryName'], values=grouped_df_category['revenue_sum'], textinfo='label+percent',
                             insidetextorientation='radial', name='Продажи по категории',text = grouped_df_category[['extra_charge','w_avg']],
                                 hovertemplate = "%{label}: <br>Объем продаж: %{value} <br>Наценка %: %{text[0]} <br>Средневзв. скидка %: %{text[1]}"
                            )])
    st.plotly_chart(fig, height = 300)
    
    grouped_df_category.rename(columns={'CategoryName': 'категория','revenue_sum': 'выручка', 'quantity_sum':'объем продаж',\
                                       'extra_charge':'наценка','w_avg':'средневзв. скидка'},inplace=True)
    
    grouped_df_category.drop({'cost_sum','margin_sum'},axis=1,inplace=True)

cll1, cll2 = st.columns((2))

with cll2:
    with st.expander("Посмотреть/Скачать файл"):
        st.write(grouped_df_category.style.background_gradient(cmap="Blues"))
        csv = grouped_df_category.to_csv(index = False)
        st.download_button("Скачать данные", data = csv, file_name = "category.csv", mime = "text/csv",help = 'Нажмите, чтобы скачать файл CSV')

col1, col2 = st.columns((2))

def summary2(x):
        result = {
            'revenue': x['revenue'].sum(),
            'cost': x['cost'].sum(),
            'margin': x['margin'].sum()
        }
        return pd.Series(result).round(2)
            
grouped_df_company=df11.groupby(['CompanyName']).apply(summary2).reset_index()

#Маржа процент
grouped_df_company['маржа_процент']=round((grouped_df_company['revenue']- grouped_df_company['cost'])*100/\
                                           grouped_df_company['revenue'], 2)                   


#наценка
grouped_df_company['наценка_процент']= round(grouped_df_company['margin']*100/grouped_df_company['cost'], 2)


grouped_df_company.drop({'cost','revenue','margin'},axis=1,inplace=True)
grouped_df_company.rename(columns={'CompanyName': 'заказчик'},inplace=True)

with col1:
     st.subheader("Сравнение % маржи и % наценки по заказчикам: ")
     # Создание столбчатой диаграммы
     fig = px.bar(grouped_df_company, y='заказчик', 
                  x=['маржа_процент', 'наценка_процент'], labels={'variable':'переменная','value':'%'},orientation='h')

     # Настройка внешнего вида
     fig.update_layout(yaxis_title= 'заказчики',
                    xaxis_title=' % маржи и % наценки',
                    barmode='stack')
     st.plotly_chart(fig, use_container_width=True,height = 500)
    

grouped_df_leaders=df11.groupby(['emp_city','emp_office','employee_name']).apply(summary2).sort_values(by='revenue',ascending=False).reset_index()
#Маржа процент
grouped_df_leaders['маржа_процент']=round((grouped_df_leaders['revenue']- grouped_df_leaders['cost'])*100/\
                                           grouped_df_leaders['revenue'], 2)
grouped_df_leaders.rename(columns={'emp_city': 'город','emp_office':'офис','employee_name':'сотрудник',\
                                  'revenue':'выручка'},inplace=True)
grouped_df_leaders.drop({'cost','margin'},axis=1,inplace=True)

with col2: 
    st.subheader("Лидеры продаж: ")
    fig = px.sunburst(grouped_df_leaders, path=['город','офис','сотрудник'], values='выручка',
                  color='маржа_процент', hover_data=['маржа_процент'],
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(grouped_df_leaders['маржа_процент'], weights=grouped_df_leaders['выручка']))
    st.plotly_chart(fig, use_container_width=True,height = 500)

col1, col2 = st.columns((2))

with col1:
    with st.expander("Посмотреть/Скачать файл"):
        st.write(grouped_df_company.style.background_gradient(cmap="Blues"))
        csv = grouped_df_company.to_csv(index = False)
        st.download_button("Скачать данные", data = csv, file_name = "company.csv", mime = "text/csv",
                               help = 'Нажмите, чтобы скачать файл CSV')
with col2:
    with st.expander("Посмотреть/Скачать файл"):
        st.write(grouped_df_leaders.style.background_gradient(cmap="Blues"))
        csv = grouped_df_leaders.to_csv(index = False)
        st.download_button("Скачать данные", data = csv, file_name = "leaders.csv", mime = "text/csv",
                               help = 'Нажмите, чтобы скачать файл CSV')







