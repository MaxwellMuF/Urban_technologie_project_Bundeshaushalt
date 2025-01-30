

# print(list(range(20,10, -1)))

# print(sorted(['Ist 2012', 'Ist 2013', 'Ist 2014', 'Ist 2015', 'Ist 2016', 'Ist 2017', 'Ist 2018', 'Ist 2019', 'Ist 2020'][::-1]))

# print([1,2,3,4] in [4,5,6])

import pandas as pd

# # Sample DataFrame
# df = pd.DataFrame({
#     'col1': [1, 2, 3, 4, 5]
# })

# # Mapping dictionary
# mapping_dict = {
#     1: 'a',
#     2: 'b',
#     3: 'c',
#     4: 'd',
#     5: 'e'
# }

# df['col2'] = df['col1'].map(mapping_dict)
# print(df)

df = pd.read_csv("domain\data\HR10y_on_id.csv")
print(df.head())
print(df.dtypes)