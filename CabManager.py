from CabReader import CabReader
from CabWriter import CABSet
import os

class CABManager(object):

    def __init__(self):
        self.cab_set = None

        self.debug_file = "debug.txt"

    def create_cab(self, cab_folders, cab_size=1474*1024,
                  cfheader_reserve=0,
                  cffolder_reserve=0,
                  cfdata_reserve=0,
                  cab_name="out_[x].cab"):

        params = {
            "output_name": cab_name,
            "cab_folders": cab_folders,
            "max_data_per_cab": cab_size,
            "cfheader_reserve": cfheader_reserve,
            "cffolder_reserve": cffolder_reserve,
            "cfdata_reserve": cfdata_reserve
            }

        self.cab_set = CABSet(parameters=params)
        self.cab_set.create_set()



    def flush_cabset_to_disk(self, output_dir=os.getcwd(), debug=False):
        if debug:
            with open(os.path.join(output_dir, self.debug_file), "wt") as f:
                for index, cab in enumerate(self.cab_set):
                    f.write(str(cab))

        #Write the .CABs
        for index, cab in enumerate(self.cab_set):
            with open(os.path.join(output_dir, cab.cab_filename), "wb") as f:
                f.write(repr(cab))

    def read_cab(self, cab_filename):
        data = CabReader(filename=cab_filename)
        return data
