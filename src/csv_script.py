import csv
import pickle 

pickle_file = file('./firmware/resultados/noise_raw_data')
data = pickle.load(pickle_file)
print(data)

csv_file = file('')