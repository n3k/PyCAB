__author__ = 'n3k'

from CabManager import CABManager
from CabWriter import CABFolderUnit
from CabExtractor import CabExtractor
import os
from Utils import Utils


def write_single_folder_multi_files_single_cab():
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

    extractor = CabExtractor()
    extracted_folder = extractor.extract(r"./TestsFiles/my_cab_0.cab")[0]

    # We need to remove the trailing null byte
    for _ in xrange(len(extracted_folder.filename_list)):
        extracted_folder.filename_list[_] = extracted_folder.filename_list[_][:-1]

    # Check names and hashes
    assert folder1 == extracted_folder
    assert extractor.get_hashes_of_files() == Utils.get_hashes_of_files(folder1.filename_list)

    # Cleanup
    os.unlink(r"./TestsFiles/my_cab_0.cab")


def write_multi_folder_multi_files_single_cab():
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

    extractor = CabExtractor()
    extracted_folder = extractor.extract(r"./TestsFiles/my_cab_0.cab")[0]

    # We need to remove the trailing null byte
    # for _ in xrange(len(extracted_folder.filename_list)):
    #     extracted_folder.filename_list[_] = extracted_folder.filename_list[_][:-1]

    # Check names and hashes
    print extractor.get_hashes_of_files()
    print Utils.get_hashes_of_files(folder1.filename_list + folder2.filename_list + folder3.filename_list)

    assert extractor.get_hashes_of_files() == Utils.get_hashes_of_files(folder1.filename_list + folder2.filename_list + folder3.filename_list)
    # Cleanup
    os.unlink(r"./TestsFiles/my_cab_0.cab")

def write_multi_folder_multi_files_multi_cabs():
    """
    Multi folder - Multi files - Multi Cabs
    """

    folder1 = CABFolderUnit(name="folder1", filename_list=[r"./TestsFiles/pe101.jpg", r"./TestsFiles/andy_C.mp3"])
    folder2 = CABFolderUnit(name="folder2", filename_list=[r"./TestsFiles/super_saiyajin.jpg"])

    manager = CABManager()
    manager.create_cab(cab_folders=[folder1, folder2], cab_name="my_cab_[x].cab", cab_size=(1474*1024))

    manager.flush_cabset_to_disk(output_dir=r"./TestsFiles/")

    extractor = CabExtractor()
    extracted_folder = extractor.extract(r"./TestsFiles/my_cab_0.cab")[0]

    # We need to remove the trailing null byte
    # for _ in xrange(len(extracted_folder.filename_list)):
    #     extracted_folder.filename_list[_] = extracted_folder.filename_list[_][:-1]

    # Check names and hashes
    assert extractor.get_hashes_of_files() == Utils.get_hashes_of_files(folder1.filename_list + folder2.filename_list)
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

    write_single_folder_multi_files_single_cab()
    write_multi_folder_multi_files_single_cab()
    write_multi_folder_multi_files_multi_cabs()
    #ReadCabinet()