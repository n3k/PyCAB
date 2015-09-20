__author__ = 'n3k'

"""
This code attemps to create valid .CAB SET files.
"""

import os
from Utils import Utils
from itertools import groupby
from CabStructs import CABFileFormat, CFHEADER, CFFOLDER, CFFILE, CFDATA

class CABException(Exception):
    pass

class CABFolderUnit(object):

    def __init__(self, name="", filename_list=[]):
        self.filename_list = filename_list
        self.name = name
        self.compression = None
        # There is a one to one relation between elements in filedata_list and elements in filename_list
        self.filedata_list = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return set(os.path.basename(_) for _ in self.filename_list) & set(os.path.basename(_) for _ in other.filename_list) == set(os.path.basename(_) for _ in self.filename_list)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class CABFile(CABFileFormat):

    @property
    def slack(self):
        return self.max_data - self.size

    def __init__(self, parameters={}):

        self.cab_filename = parameters.get("cab_filename", None)
        self.max_data = parameters.get("max_data", 0)
        self.cabset = parameters.get("cabset", None)
        self.size = 0

        index_in_set = parameters.get("index_in_set", 0)
        cfdata_reserve = parameters.get("cfdata_reserve", 0)
        cfheader_reserve = parameters.get("cfheader_reserve", 0)
        cffolder_reserve = parameters.get("cffolder_reserve", 0)


        if cfheader_reserve != 0 or cffolder_reserve != 0 or cfdata_reserve != 0:
            flags = CFHEADER.cfhdrRESERVE_PRESENT
        else:
            flags = 0x0000

        reserve = {
            'cbCFHeader' : cfheader_reserve,
            'cbCFFolder' : cffolder_reserve,
            'cbCFData' : cfdata_reserve
            }

        self.cfheader = CFHEADER(flags=flags, reserve=reserve)
        self.cfheader.iCabinet = index_in_set

        self.cffolder_list = []
        self.cffile_list = []
        self.cfdata_list = []

        # This is a help for calculating fields, is not part of the specification
        self.folder_id = 0


    ##### METHODS FOR MANAGING CABs #####
    def get_cfheader(self):
        return self.cfheader

    def get_cffolder_list(self):
        return self.cffolder_list

    def get_cffile_list(self):
        return self.cffile_list

    def get_cfdata_list(self):
        return self.cfdata_list

    #####################################

    def _create_cffolder(self, folder_name):
        new_cffolder = CFFOLDER(self.cfheader, folder_id=self.folder_id)
        new_cffolder.name = folder_name
        self.folder_id += 1
        self.cfheader.add_folder(cffolder=new_cffolder)
        return new_cffolder

    def update_fields(self):
        # Update uoffFolderStart in CFFILE
        self._update_uoffFolderStart()
        #coffCabStart in CFFOLDER
        self._update_coffCabStart()
        # Update cCabinet and coffFiles in CFHEADER
        self._update_cbCabinet()
        self._update_coffFiles()

    def _check_for_scattered_prev_cffile(self, cffolder):
        # This method workarounds a border case that happens when we have 2 files in a folder
        # In wich the first file occupies more than one cab... When this happens, when the second
        # cffile gets added, it cannot share the scattered CFFOLDER because it doesn't work..
        # We need to create an anonymous CFFOLDER here and return it
        last_cffile = cffolder.cffile_list[-1]
        if last_cffile.iFolder & CFFILE.ifoldCONTINUED_FROM_PREV == CFFILE.ifoldCONTINUED_FROM_PREV:
            anonymous_folder = self._create_cffolder(Utils.get_random_name(10))
            self.cffolder_list.append(anonymous_folder)
            return anonymous_folder
        return cffolder

    def add_file(self, folder_name, filename, total_len, data):

        if self.size == self.max_data:
            raise CABException("This cab is full")

        if (self.size + len(data)) <= self.max_data:

            try:
                cffolder = next(_ for _ in self.cffolder_list if _.name == folder_name)
                # We need to check if the cffolder has a cffile scattered that continues from a PREV
                # If this is the case, we need to provide a new cffolder anyways.. this is how it works
                cffolder = self._check_for_scattered_prev_cffile(cffolder)
            except StopIteration:
                cffolder = self._create_cffolder(folder_name)
                self.cffolder_list.append(cffolder)

            cffile = CFFILE(cffolder=cffolder, total_len=total_len, filename=filename)
            self.cffile_list.append(cffile)

            # Max data per CFDATA is 0x8000 -> This is an empirical result
            if len(data) > 0x8000:
                data_chunks = [data[i:i+0x8000] for i in range(0, len(data), 0x8000)]
                for data_chunk in data_chunks:
                    cfdata = CFDATA(cffolder=cffolder, data=data_chunk)
                    self.cfdata_list.append(cfdata)
                    cffolder.add_data(cfdata)
            else:
                cfdata = CFDATA(cffolder=cffolder, data=data)
                self.cfdata_list.append(cfdata)
                # Update cCFData
                cffolder.add_data(cfdata)

            cffolder.add_file(cffile)

            self.update_fields()
            self.size += len(data)

        else:
            raise CABException("The cab hasn't enough space for the data ")

    def _update_uoffFolderStart(self):
        """Updates the Uncompressed byte offset of the start of every file's data"""
        for key, group in groupby(self.cffile_list, lambda x: x.cffolder.folder_id):
            offset = 0
            for cffile in group:
                cffile.uoffFolderStart = offset
                offset += cffile.cbFile

    def _update_coffCabStart(self):
        """Update the Absolute file offset of first CFDATA block for every CFFolder"""
        data_start = len(self.cfheader) + sum([len(cffolder) for cffolder in self.cffolder_list]) + \
                    sum([len(cffile) for cffile in self.cffile_list])
        self.cffolder_list[0].coffCabStart = data_start
        for index, cffolder in enumerate(self.cffolder_list[1:]):
            data_start = data_start + sum([len(cfdata) for cfdata in self.cffolder_list[index].cfdata_list])
            cffolder.coffCabStart = data_start

        # current = 0
        # for index, cfdata in enumerate(self.cfdata_list):
        #     cffolder = cfdata.cffolder
        #     if cffolder.folder_id == current:
        #         offset = len(self.cfheader) + sum([len(cffolder) for cffolder in self.cffolder_list]) + \
        #             sum([len(cffile) for cffile in self.cffile_list])
        #
        #         # now the hard part
        #         for p_data in self.cfdata_list:
        #             if p_data.cffolder.folder_id != current:
        #                 offset += len(p_data)
        #             else:
        #                 current += 1
        #                 cffolder.coffCabStart = offset
        #                 break


    def _update_cbCabinet(self):
        """
        Total size of this cabinet file in bytes.
        """
        self.cfheader.cbCabinet = self.__len__()

    def _update_coffFiles(self):
        """
        Absolute file offset of first CFFILE entry.
        """
        value = len(self.cfheader)
        for i in self.cffolder_list:
            value += len(i)
        self.cfheader.coffFiles = value

    def __repr__(self):
        data = repr(self.cfheader)
        for i in self.cffolder_list:
            data += repr(i)
        for i in self.cffile_list:
            data += repr(i)
        for i in self.cfdata_list:
            data += repr(i)
        return data

    def __str__(self):
        data = str(self.cfheader)
        for i in self.cffolder_list:
            data += str(i)
        for i in self.cffile_list:
            data += str(i)
        for i in self.cfdata_list:
            data += str(i)
        return data

    def __len__(self):
        result = len(self.cfheader)
        for i in self.cffolder_list:
            result += len(i)
        for i in self.cffile_list:
            result += len(i)
        for i in self.cfdata_list:
            result += len(i)
        return result

    @classmethod
    def get_null_ended_string(cls, sz):
        return sz + "\x00"

class ChunkGenerator(object):

    def __init__(self, filename):
        self.filename = filename
        self.handle = open(self.filename, "rb")
        self.total_filesize = Utils.get_file_size(self.handle)
        self.finished = False

    def get_chunk(self, bytes_to_read):
        chunk = self.handle.read(bytes_to_read)
        if self.handle.tell() >= self.total_filesize:
            self.handle.close()
            self.finished = True
        return chunk


class CABSet(object):

    def __init__(self, parameters={}):
        self.cab_files = []

        # This will be the value to put into iCabinet field of CFHEADER
        self.index_in_set = 0

        self.ordered_file_list_by_size = None

        self.output_name = parameters.get("output_name", "out_[x].cab")

        # This is a list of CABFolderUnit instances
        self.cab_folders = parameters.get("cab_folders", [])

        self.max_data_per_cab = parameters.get("max_data_per_cab", 1024)
        self.cfdata_reserve = parameters.get("cfdata_reserve", 0)
        self.cffolder_reserve = parameters.get("cffolder_reserve", 0)
        self.cfheader_reserve = parameters.get("cfheader_reserve", 0)


    def _create_new_cabfile(self):

        cab_filename = self.output_name.replace("[x]", str(self.index_in_set))

        creation_params= {
            "cab_filename": cab_filename,
            "cabset": self,
            "max_data": self.max_data_per_cab,
            "index_in_set": self.index_in_set,
            "cfheader_reserve": self.cfheader_reserve,
            "cffolder_reserv": self.cffolder_reserve,
            "cfdata_reserve": self.cfdata_reserve
        }

        cab_file = CABFile(parameters=creation_params)

        # increment the cab number in the set
        self.index_in_set += 1
        # add it to the set
        self.cab_files.append(cab_file)
        return cab_file

    def _get_cab_with_free_space(self):
        for cab_file in self.cab_files:
            if cab_file.size < self.max_data_per_cab:
                return cab_file
        # if there is no cab with free space, create a new one
        return self._create_new_cabfile()


    def __iter__(self):
        return iter(self.cab_files)

    def _find_first_cab_of_file(self, filename, folder_name):
        for cabfile in self.cab_files:
            for cffolder in cabfile.cffolder_list:
                if cffolder.name == folder_name:
                    for cffile in cffolder.cffile_list:
                        if cffile.szName == CABFile.get_null_ended_string(filename):
                            return cabfile
        return None


    def _update_prev_cabfile(self, filename):
        # Only execute if there is more than one cab in the set
        if len(self.cab_files) < 2:
            return

        # Get the previous cab and the current cab
        prev_cab = self.cab_files[-2]
        current_cab = self.cab_files[-1]

        if prev_cab.cfheader.flags & CFHEADER.cfhdrNEXT_CABINET != CFHEADER.cfhdrNEXT_CABINET:
        # We only need to update the szCabinetNext, szDiskNext and Flags once!

            # Set the NEXT_CABINET flag in the cfheader
            prev_cab.cfheader.flags |= CFHEADER.cfhdrNEXT_CABINET
            # Update strings in the cfheader indicating there is a next cab
            prev_cab.cfheader.szCabinetNext = CABFile.get_null_ended_string(current_cab.cab_filename)
            prev_cab.cfheader.szDiskNext = CABFile.get_null_ended_string("continued")

            # Set IFolder on CFFILE to ifoldCONTINUED_TO_NEXT
            folder_list = prev_cab.cfheader.cffolder_list
            for folder in folder_list:
                for _cffile in folder.cffile_list:
                    if _cffile.szName == CABFile.get_null_ended_string(filename):
                        if _cffile.iFolder in CFFILE.get_iFolder_options():
                            _cffile.iFolder |= CFFILE.ifoldCONTINUED_TO_NEXT
                        else:
                            _cffile.iFolder = CFFILE.ifoldCONTINUED_TO_NEXT

        # Update offsets - We need to do this every time
        # because we've just added some strings into the structure
        prev_cab.update_fields()

    def _update_current_cabfile(self, filename, folder_name):

        # Only execute if there was more than one cab before inserting the current
        if len(self.cab_files) < 2:
            return

        # The last added cab is the current
        cab_file = self.cab_files[-1]

        if cab_file.cfheader.flags & CFHEADER.cfhdrPREV_CABINET != CFHEADER.cfhdrPREV_CABINET:
        # We only need to update the szCabinetPrev, szDiskPrev and Flags once!

            # Set PREVIOUS CABINET on the actual
            cab_file.cfheader.flags |= CFHEADER.cfhdrPREV_CABINET

            # MSDN - szCabinetPrev:
            # Note that this gives the name of the most-recently-preceding cabinet file that contains
            #  the initial instance of a file entry. This might not be the immediately previous cabinet file,
            #  when the most recent file spans multiple cabinet files. If searching in reverse for a specific file entry,
            #  or trying to extract a file that is reported to begin in the "previous cabinet",
            #  szCabinetPrev would give the name of the cabinet to examine.

            # We need to search for the first cabinet that holds part of the file
            prev_cab = self._find_first_cab_of_file(filename, folder_name)
            if prev_cab == None:
                # This is a border case where the last cabfile had the exact space requiered for the last file.
                prev_cab = self.cab_files[-2]
            cab_file.cfheader.szCabinetPrev = CABFile.get_null_ended_string(prev_cab.cab_filename)
            cab_file.cfheader.szDiskPrev = CABFile.get_null_ended_string("previous")

            folder_list = cab_file.cfheader.cffolder_list
            for folder in folder_list:
                for _cffile in folder.cffile_list:
                    if _cffile.szName == CABFile.get_null_ended_string(filename):
                        if _cffile.iFolder in CFFILE.get_iFolder_options():
                             _cffile.iFolder |= CFFILE.ifoldCONTINUED_FROM_PREV
                        else:
                            _cffile.iFolder = CFFILE.ifoldCONTINUED_FROM_PREV

        # Update offsets - We need to do this every time
        # because we've just added some strings into the structure
        cab_file.update_fields()

    def create_set(self):
        """
        This method will iterate through every folder/file specified previously
        to create the set of cabs
        :return: it returns a list of cab files instances
        """
        for folder_unit in self.cab_folders:
            for full_filename in folder_unit.filename_list:
                chunk_generator = ChunkGenerator(filename=full_filename)
                filename = os.path.basename(full_filename)
                while not chunk_generator.finished:

                    # Look for a CAB in the set with space, if there is not any, create a new one
                    # Then put the file data into the cab structure
                    cab_file = self._get_cab_with_free_space()
                    size_to_fill = cab_file.slack
                    data = chunk_generator.get_chunk(bytes_to_read=size_to_fill)

                    try:
                        cab_file.add_file(folder_name=folder_unit.name,
                                      filename=CABFile.get_null_ended_string(filename),
                                      total_len=chunk_generator.total_filesize,
                                      data=data)
                    except CABException:
                        cab_file = self._create_new_cabfile()
                        cab_file.add_file(folder_name=folder_unit.name,
                                      filename=CABFile.get_null_ended_string(filename),
                                      total_len=chunk_generator.total_filesize,
                                      data=data)

                    # Check if there is a previous CAB created and update required fields
                    self._update_prev_cabfile(filename=filename)
                    # We need to update some fields on the current cab if it is not the first
                    self._update_current_cabfile(filename=filename, folder_name=folder_unit.name)

        return self.cab_files