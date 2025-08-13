# importing necessary libraries
import pandas as pd
import calendar
import matplotlib.pyplot as plt

# reading file
df = pd.read_csv('sales_data_large.csv')

# checking column types
types_of_columns = df.dtypes
# print(types_of_columns)

# analyze missing data rates
missing_data_rates = df.isnull().mean() # isnull() -> missing values in dataframe
# print(missing_data_rates)

# convert OrderDate column to datetime format
df['OrderDate'] = pd.to_datetime(df['OrderDate']) #pandas function

# find negative values for price and quantity
# print(df[df["Price"] < 0]["Price"]) # 101 item
# print(df[df["Quantity"] < 0]["Quantity"]) # 0 item

# remove the negative lines
df = df[df['Price'] >= 0]

# change the blank or “N/A” values in the 'Status' column to “Unknown”
df['Status'] = df['Status'].replace('N/A', 'Unknown') # replacing
df['Status'] = df['Status'].fillna('Unknown') # filling
# print(df[df['Status'] == 'Unknown'])

# correct city names in 'City' column to title
df['City'] = df['City'].str.title() # calling title() over str.

# new column => TotalPrice: Quantity * Price
df['TotalPrice'] = df['Quantity'] * df['Price']
# print(df['TotalPrice'])

# extract 'Year', 'Month', 'Weekday' columns from date data
df['Year'] = df['OrderDate'].dt.year # dt. -> datetime functions
df['Month'] = df['OrderDate'].dt.month.apply(lambda x: calendar.month_name[x]) # apply(func) -> apply the func to every x
df['Weekday'] = df['OrderDate'].dt.day_name()

# set 'TotalPrice' = 0 for lines that do not have an order status of "Delivered"
df.loc[df['Status']!= 'Delivered', 'TotalPrice'] = 0 # loc[condition, column] OR loc[row, column]

# total sales revenue by month
monthly_revenue = df.groupby('Month')['TotalPrice'].sum() # groupby() -> grouping columns
# print(monthly_revenue)

# top 5 best-selling products
top_products = df.groupby('Product')['Quantity'].sum().sort_values(ascending=False).head()
# sort_values(ascending=False) -> sorting values in decreasing order
# head() -> first 5 values
# print(top_products)

# average basket size by city (total amount / number of orders)
average_order_value = df.groupby('City')['TotalPrice'].sum() / df.groupby('City').size() # size() -> numbers of elements
# print(average_order_value)

# the category is the average price higher
max_price = df.groupby('Product')['Price'].sum().sort_values(ascending=False).head(1)
# print(max_price)

# most cancelled products
top_cancelled = df[df['Status'] == 'Cancelled'].groupby('Product').size().sort_values(ascending=False).head()
# print(top_cancelled)

# Each customer: number of orders, total spending, city where they shop the most, busiest order day
order_count = df.pivot_table(index='CustomerID', values='Quantity', aggfunc='count')
#aggcount -> function to be applied

total_spent = df.pivot_table(index='CustomerID', values='TotalPrice', aggfunc='sum')

most_city = (
    df.groupby(['CustomerID', 'City']) # grouping two columns
    .size() # number of elements
    .reset_index(name='Count') # reset index name and convert it to 'count'
    .sort_values(['CustomerID', 'Count'], ascending=[True, False]) # sorting values increasing and decreasing
    .drop_duplicates('CustomerID') # dropping duplicates of CustomerID
    .set_index('CustomerID')['City'] # indexes -> 'CustomerID', 'City' column
)

most_day = (
    df.groupby(['CustomerID', 'Weekday']) # grouping two columns
    .size() # number of elements
    .reset_index(name='Count') # reset index name and convert it to 'count'
    .sort_values(['CustomerID', 'Count'], ascending=[True, False]) # sorting values increasing and decreasing
    .drop_duplicates('CustomerID') # dropping duplicates of CustomerID
    .set_index('CustomerID')['Weekday'] # indexes -> 'CustomerID', 'Weekday' column
)

summary = order_count.merge(total_spent, on='CustomerID') \
                     .merge(most_city, on='CustomerID') \
                     .merge(most_day, on='CustomerID') # \ -> line continues below
# customerID fixed, merge all pivot tables


# MATPLOTLIB

# MONTHLY SALES CHART
# x/y: month/monthly total sales
monthly_sales = df.groupby('Month')['TotalPrice'].sum()
months = list(calendar.month_name)[1:] # month names

# figure() comes before bar()
plt.figure(figsize=(12, 6)) # graph dimensions
plt.bar(months, monthly_sales) # bar chart
plt.xticks(rotation=45) # x-axis text slope

plt.xlabel('Month') # x-label
plt.ylabel('Total Monthly Sales') # y-label
plt.title('Monthly Sales Chart')
plt.show() # draw


# TOTAL REVENUE PIE CHART
total_revenue = df.groupby('Category')['TotalPrice'].sum()
plt.pie(total_revenue, labels=total_revenue.index, autopct='%1.1f%%')
plt.title("Total Income By Category") # title
plt.show() # draw


# BAR CHART OF ORDER NUMBERS BY CITY
order_number = df.groupby('City')['Quantity'].sum()
cities = df['City'].value_counts().index.tolist()
# value_counts() -> unique values for each value
# index.tolist() -> takes sorted list and converts it to python list

plt.figure(figsize=(8, 5))
plt.bar(cities, order_number)
plt.xticks(rotation=45)

plt.xlabel('Cities')
plt.ylabel('Number of Orders')
plt.title('Number of Orders By Cities')
plt.show()


# AVERAGE ORDER QUANTITY BY DAY OF THE WEEK LINE CHART
mean_of_orders = df.groupby('Weekday')['TotalPrice'].mean()
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

plt.figure(figsize=(8, 5))
plt.plot(days, mean_of_orders) # line graph
plt.xticks(rotation=45)
plt.xlabel('Days')
plt.ylabel('Mean of Orders')
plt.title('Mean of Orders By Days')
plt.grid(True) # visible grids
plt.show()

# writing on another file without index files
df.to_csv('day2-08.07/sales_data_cleaned.csv', index=False)
