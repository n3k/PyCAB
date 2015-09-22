from pycab.CabExtractor import CabExtractor, Utils
from pycab.CabManager import CABManager
from pycab.CabWriter import CABFolderUnit
import os
import unittest

class IntegrationTestcase(unittest.TestCase):

    def setUp(self):
        pass

    def test_write_single_folder_multi_files_single_cab(self):
        """
        Single Folder - Multiple files - Single Cab
        """
        folder1 = CABFolderUnit()
        folder1.name = "folder1"
        folder1.filename_list = [r"./TestsFiles/pe101.jpg",
                                 r"./TestsFiles/andy_C.mp3",
                                 r"./TestsFiles/super_saiyajin.jpg"
                                ]

        manager = CABManager()
        manager.create_cab(cab_folders=[folder1], cab_name="my_cab_[x].cab", cab_size=1474*1024*16)
        manager.flush_cabset_to_disk(output_dir=r"./TestsFiles/")

        # Perform in memory extraction
        extractor = CabExtractor()
        extractor.extract(r"./TestsFiles/my_cab_0.cab")

        # Check hashes
        extracted_hash_set = set([v for k, v in extractor.get_hashes_of_files().items()])
        files_hash_set = set([v for k, v in Utils.get_hashes_of_files(folder1.filename_list).items()])

        self.assertEquals(extracted_hash_set, files_hash_set)
        # Cleanup
        os.unlink(r"./TestsFiles/my_cab_0.cab")


    def test_write_multi_folder_multi_files_single_cab(self):
        """
        Multiple Folders - Multiple Files - Single Cab
        """
        folder1 = CABFolderUnit(name="folder1", filename_list=[r"./TestsFiles/pe101.jpg"])
        folder2 = CABFolderUnit(name="folder2", filename_list=[r"./TestsFiles/andy_C.mp3"])
        folder3 = CABFolderUnit(name="folder3", filename_list=[r"./TestsFiles/super_saiyajin.jpg"])
        manager = CABManager()
        manager.create_cab(cab_folders=[folder1, folder2, folder3],
                          cab_name="my_cab_[x].cab",
                          cab_size=1474*1024*16
                          )

        manager.flush_cabset_to_disk(output_dir=r"./TestsFiles/")

        # Perform in memory extraction
        extractor = CabExtractor()
        extractor.extract(r"./TestsFiles/my_cab_0.cab")

        # Check hashes
        extracted_hash_set = set([v for k, v in extractor.get_hashes_of_files().items()])
        files_hash_set = set([v for k, v in Utils.get_hashes_of_files(folder1.filename_list + folder2.filename_list + folder3.filename_list).items()])

        self.assertEquals(extracted_hash_set, files_hash_set)
        # Cleanup
        os.unlink(r"./TestsFiles/my_cab_0.cab")

    def test_write_multi_folder_multi_files_multi_cabs(self):
        """
        Multi folder - Multi files - Multi Cabs
        """

        folder1 = CABFolderUnit(name="folder1", filename_list=[r"./TestsFiles/pe101.jpg", r"./TestsFiles/andy_C.mp3"])
        folder2 = CABFolderUnit(name="folder2", filename_list=[r"./TestsFiles/super_saiyajin.jpg"])

        manager = CABManager()
        manager.create_cab(cab_folders=[folder1, folder2], cab_name="my_cab_[x].cab", cab_size=(1474*1024))

        manager.flush_cabset_to_disk(output_dir=r"./TestsFiles/")

        # Perform in memory extraction
        extractor = CabExtractor()
        extractor.extract(r"./TestsFiles/my_cab_0.cab")

        # Check hashes
        extracted_hash_set = set([v for k, v in extractor.get_hashes_of_files().items()])
        files_hash_set = set([v for k, v in Utils.get_hashes_of_files(folder1.filename_list + folder2.filename_list).items()])

        # Check hashes
        self.assertEquals(extracted_hash_set, files_hash_set)
        # Cleanup
        os.unlink(r"./TestsFiles/my_cab_0.cab")
        os.unlink(r"./TestsFiles/my_cab_1.cab")
        os.unlink(r"./TestsFiles/my_cab_2.cab")
        os.unlink(r"./TestsFiles/my_cab_3.cab")

def ReadCabinet():
    manager = CABManager()
    cab = manager.read_cab("my_cab_0.cab")
    with open("cab0.txt", "wt") as f:
        f.write(str(cab))
    cab = manager.read_cab("my_cab_1.cab")
    with open("cab1.txt", "wt") as f:
        f.write(str(cab))
    cab = manager.read_cab("my_cab_2.cab")
    with open("cab2.txt", "wt") as f:
        f.write(str(cab))

    cab = manager.read_cab(r"./TestsFiles/PRUEBA1.CAB")
    with open(r"./TestsFiles/prueba1.txt", "wt") as f:
        f.write(str(cab))
    cab = manager.read_cab(r"./TestsFiles/PRUEBA2.CAB")
    with open(r"./TestsFiles/prueba2.txt", "wt") as f:
        f.write(str(cab))
    cab = manager.read_cab(r"./TestsFiles/PRUEBA3.CAB")
    with open(r"./TestsFiles/prueba3.txt", "wt") as f:
        f.write(str(cab))


if __name__ == "__main__":
    unittest.main()
    #ReadCabinet()