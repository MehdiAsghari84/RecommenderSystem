# import libraries
import pyodbc
import html
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Connect to database (SQL server)
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-MEHDI;'
                      'Database=RS;'
                      'Trusted_Connection=yes;')


# Select Query
sql_query = pd.read_sql_query ('''
SELECT * FROM ExtraWarehouse
                              ''' , conn)

# Catch data from sql server to data frame
Extra_Warehouse = pd.DataFrame(sql_query, columns = ['Warehouse', 'Stockcode', 'Description', 'Qty'])


# Decode HTML special char
def htmldecode(text):
    return html.unescape(text
    )

# clean data
Extra_Warehouse['Description'] = Extra_Warehouse['Description'].apply(htmldecode)

# add size and id   
def get_size(stockcode):
    return str(stockcode)[-2:]

def get_id(stockcode):
    return str(stockcode)[:4]

available_stock = Extra_Warehouse.filter(['Stockcode','Description'], axis=1)
available_stock['size'] = available_stock['Stockcode'].apply(get_size)
available_stock['id'] = available_stock['Stockcode'].apply(get_id)

# Recommender function
def get_recommendations(stockcode,description):
    available_stock = Extra_Warehouse.filter(['Stockcode','Description'], axis=1)
    available_stock['size'] = available_stock['Stockcode'].apply(get_size)
    available_stock['id'] = available_stock['Stockcode'].apply(get_id)
    filter_size = get_size(stockcode)
    filter_id = get_id(stockcode)
    available_stock = available_stock.loc[(available_stock['size']==filter_size) & (available_stock['id']==filter_id)]
    
    input_data = {'Stockcode':stockcode, 'Description': description}
    input_df = pd.DataFrame(data=input_data,index=[0])
    input_df['size'] = input_df['Stockcode'].apply(get_size)
    input_df['id'] = input_df['Stockcode'].apply(get_id) 
    available_stock= available_stock.append(input_df)
    available_stock.reset_index(drop=True, inplace=True)

    tfidf = TfidfVectorizer(max_features=500,stop_words='english')
    tfidf_matrix = tfidf.fit_transform(available_stock['Description'])
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix)

    for i in range(len(cosine_sim[0])):
        if(cosine_sim[0][i]>=0.1):
            print(cosine_sim[0][i],">> ")
            print(available_stock.loc[[i]]['Stockcode'])
        i=i+1

# sample for test
print(get_recommendations('LP00AB1408','8 IN NS PIPE BE NACE '))