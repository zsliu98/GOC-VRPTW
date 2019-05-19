import pandas


class DataTaker:
    def __init__(self, dir='data'):
        self.distance_time_dir = dir + '/' + 'input_distance-time.csv'
        self.input_node_dir = dir + '/' + 'input_node.xlsx'
        self.input_vehicle_dir = dir + '/' + 'input_vehicle_type.xlsx'

    def read_distance(self):
        table = pandas.read_csv(self.distance_time_dir, usecols=[1, 2, 3, 4])

    def read_node(self):
        table = pandas.read_excel(self.input_node_dir)

    def read_vehicel(self):
        table = pandas.read_excel(self.input_vehicle_dir, sheet_name='Vehicle_data')
