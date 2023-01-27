import pandas as pd

class data_loader:
    df = pd.read_excel('../data/_combined_datasets.xlsx', engine='openpyxl')

    neighbourhood_households_amount = df["houses"].values.tolist()      # Capacity
    neighbourhood_households_disposable_income = df["household_disposable_income"].values.tolist()      # Disposable Income

    neighbourhood_housing_quality = df["satisfaction_housing"].values.tolist()  # Housing Quality
    neighbourhood_shops = df["shop_index"].values.tolist()      # Shops Index
    neighbourhood_crime = df["crime_index"].values.tolist()     # Crime Index
    neighbourhood_nature = df["nature_area_%"].values.tolist()  # Nature Index

    target_neighbourhood_houses_sold = df["houses_sold"].values.tolist()
    target_neighbourhood_houses_price = df["average_house_price"].values.tolist()
    target_neighbourhood_satisfaction = df["satisfaction_neighbourhood"].values.tolist()
    target_neighbourhood_sellers = df["want_to_move_out_%"].values.tolist()\
    
gemente_data = data_loader
