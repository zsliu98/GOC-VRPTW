import pandas as pd


class DataTaker:
    def __init__(self, read_dir='data'):
        self.distance_time_dir = read_dir + '/' + 'input_distance-time.csv'
        self.input_node_dir = read_dir + '/' + 'input_node.xlsx'
        self.input_vehicle_dir = read_dir + '/' + 'input_vehicle_type.xlsx'

    def read_distance(self):
        table = pd.read_csv(self.distance_time_dir, usecols=[1, 2, 3, 4])
        return table

    def read_node(self):
        table = pd.read_excel(self.input_node_dir)
        return table

    def read_vehicle(self):
        table = pd.read_excel(self.input_vehicle_dir, sheet_name='Vehicle_data')
        return table
