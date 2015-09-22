__author__ = 'n3k'

from abc import ABCMeta, abstractmethod
import os
import hashlib

from Utils import Utils
from CabReader import CabReader
from CabWriter import CABException, CABFolderUnit
from pycab.CabStructs import CFHEADER, CFFILE, CFDATA


class Extraction(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def extract(self, cab):
        """
        This method has to return a list of FolderUnits containing all the data
        """
        pass

    def __init__(self, extractor):
        self.__folder_name = self.__generate_folder_name()
        self._extractor = extractor

    def __generate_folder_name(self):
        i = 0
        base_name = Utils.get_random_name(5) + "_folder_"
        while True:
            yield base_name + str(i)
            i += 1

    def _get_folder_name(self):
        return self.__folder_name.next()

class SimpleExtraction(Extraction):

    def extract(self, cab):

        result = []
        curr_index_data = 0
        folder_unit = CABFolderUnit(name=self._get_folder_name())
        #for findex, cffolder in enumerate(cab.cffolder_list):

        for cffile in cab.cffile_list:
            folder_unit.filename_list.append(cffile.szName)
            file_data_len = 0
            file_data = ""
            while file_data_len < cffile.cbFile:
                current_cfdata = cab.cfdata_list[curr_index_data]
                file_data_len += current_cfdata.cbUncomp
                file_data += current_cfdata.ab
                curr_index_data += 1
            folder_unit.filedata_list.append(file_data)

        result.append(folder_unit)

        return result


class SetExtraction(Extraction):

    def __init__(self, extractor):
        super(SetExtraction, self).__init__(extractor)
        self.cab_list = []
        self.curr_index_data = 0
        self.file_data_len = 0
        self.current_folder_unit = None

    def _get_next_cab_in_set(self, current_cab):
        filename = os.path.join(self._extractor.cab_dirname, current_cab.cfheader.szCabinetNext[:-1])
        if filename != "":
            if os.path.isfile(filename):
                try:
                    cab = CabReader(filename)
                except:
                    raise CABException("File %s is not a valid .CAB" % filename)
                return cab
        return None

    def _read_set(self, cab):
        while cab is not None:
            self.cab_list.append(cab)
            cab = self._get_next_cab_in_set(cab)

    def _check_scattered_file(self, cffile):
        result = cffile.iFolder & CFFILE.ifoldCONTINUED_FROM_PREV == CFFILE.ifoldCONTINUED_FROM_PREV
        result |= cffile.iFolder & CFFILE.ifoldCONTINUED_TO_NEXT == CFFILE.ifoldCONTINUED_TO_NEXT
        return result

    def _read_data_primitive(self, current_cab, cffile):
        file_data = ""
        file_data_len = self.file_data_len
        while file_data_len < cffile.cbFile and self.curr_index_data < len(current_cab.cfdata_list):
            current_cfdata = current_cab.cfdata_list[self.curr_index_data]
            file_data_len += current_cfdata.cbUncomp
            file_data += current_cfdata.ab
            self.curr_index_data += 1
        self.file_data_len = file_data_len
        if self.file_data_len > cffile.cbFile:
            # The CAB compressor of windows does a nasty thing...
            # It allows to share a CFDATA between TWO CFFILES
            # We need to adjust the data if this is the case
            difference = self.file_data_len - cffile.cbFile
            real_file_data = file_data[0:(self.file_data_len-difference)]
            # We will create an anonymous CFDATA and add it to the list ..
            # This way the remaining bytes that belongs to the next CFFILE will be read transparently
            new_cfdata = CFDATA()
            new_cfdata.ab = file_data[(self.file_data_len-difference):self.file_data_len]
            new_cfdata.cbUncomp = len(new_cfdata.ab)
            new_cfdata.cbData = len(new_cfdata.ab)
            current_cab.cfdata_list.insert(self.curr_index_data, new_cfdata)
            return real_file_data
        return file_data


    def extract(self, cab):
        """
        This implementation will get all the remaining cabs on disk to get their content
        Currently, it puts all the files in one folder...
        """
        self._read_set(cab)

        result = []
        scattered_folders = []
        self.file_data_len = 0
        self.current_folder_unit = CABFolderUnit(name=self._get_folder_name())

        for current_cab in self.cab_list:
            self.curr_index_data = 0

            for file_index, cffile in enumerate(current_cab.cffile_list):
                if self._check_scattered_file(cffile):
                    # Work on scattered file
                    if cffile.iFolder & CFFILE.ifoldCONTINUED_FROM_PREV == CFFILE.ifoldCONTINUED_FROM_PREV:
                        # We know we should already have a scattered folder_unit
                        # This is so because only the first CFFILE can be scattered from a PREV
                        file_data = self._read_data_primitive(current_cab, cffile)
                        # Append data to the last filedata
                        self.current_folder_unit.filedata_list[-1] += file_data

                    if cffile.iFolder & CFFILE.ifoldCONTINUED_TO_NEXT == CFFILE.ifoldCONTINUED_TO_NEXT:
                        # We know we must mark the current folder_unit as a scattered one
                        # scattered_folders.append(self.current_folder_unit)
                        if self.curr_index_data < len(current_cab.cfdata_list):
                            # Here we're facing a new scattered CAB
                            self.current_folder_unit.filename_list.append(cffile.szName)
                            file_data = self._read_data_primitive(current_cab, cffile)
                            self.current_folder_unit.filedata_list.append(file_data)
                else:
                    # This are cffiles that end in the same .cab file
                    self.current_folder_unit.filename_list.append(cffile.szName)
                    file_data = self._read_data_primitive(current_cab, cffile)
                    self.current_folder_unit.filedata_list.append(file_data)

                if self.file_data_len >= cffile.cbFile:
                    self.file_data_len = 0

        result.append(self.current_folder_unit)
        return result


class CabExtractor(object):
    """
    This class uses the CabReader to get the actual data, extract it
    and save it to an output directory
    """

    def __init__(self, force_extraction=False):
        self.force_extraction = force_extraction
        self.output_directory = r"./Testing/TestsFiles/extraction/"
        self.cab_dirname = ""
        self.folder_unit_list = []

    def __check_cab_is_first_in_set(self, cab):
        return cab.cfheader.iCabinet == 0

    def __check_more_cabs_remain(self, cab):
        return cab.cfheader.flags & CFHEADER.cfhdrNEXT_CABINET != 0

    def force_extract(self, filename):
        pass
        #cab = CabReader(filename)
        #if self.force_extraction:
        #    folder_unit_list = ForceExtraction().extract(cab)

    def extract(self, filename):
        self.cab_dirname = os.path.dirname(filename) if os.path.dirname(filename) != "" else "."

        cab = CabReader(filename)
        if not self.__check_cab_is_first_in_set(cab):
            raise CABException("The cab file is not the first in the set")

        if self.__check_more_cabs_remain(cab):
            self.folder_unit_list = SetExtraction(extractor=self).extract(cab)
        else:
            self.folder_unit_list = SimpleExtraction(extractor=self).extract(cab)

        return self.folder_unit_list


    def _make_sure_path_exists(self):
        if os.path.isdir(self.output_directory):
            return
        try:
            os.makedirs(self.output_directory)
        except OSError as exception:
           raise CABException("Could not create output directory")

    def flush_to_disk(self):
        self._make_sure_path_exists()
        for folder_unit in self.folder_unit_list:
            os.mkdir(os.path.join(self.output_directory, folder_unit.name))
            for filename, filedata in zip(folder_unit.filename_list, folder_unit.filedata_list):
                # the filename has a nullbyte at the end... we must strip it
                with open(os.path.join(self.output_directory, folder_unit.name, filename[:-1]), "wb") as f:
                    f.write(filedata)

    def get_hashes_of_files(self):
        """
        This method calculates the md5 checksum of every CFFILE
        :return: {"filename": checksum, ...}
        """
        result = {}
        for folder_unit in self.folder_unit_list:
            for filename, filedata in zip(folder_unit.filename_list, folder_unit.filedata_list):
                result[filename] = hashlib.md5(filedata).hexdigest()
        return result


if __name__ == "__main__":
    extractor = CabExtractor()
    #print extractor._get_folder_name()
    #print extractor._get_folder_name()
    #assert extractor.extract(filename=r"./Testing/TestsFiles/PRUEBA2.CAB")
    extractor.extract(filename=r"./Testing/TestsFiles/my_cab_0.cab")
    extractor.flush_to_disk()