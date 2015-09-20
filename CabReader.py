__author__ = 'n3k'

import struct
from CabStructs import CABFileFormat, CFHEADER, CFFOLDER, CFFILE, CFDATA

class CabReader(CABFileFormat):
    """
    This class is able to read VALID .cab files
    """

    def __init__(self, filename):
        self.filename = filename

        self.cfheader = None
        self.cffolder_list = []
        self.cffile_list = []
        self.cfdata_list = []

        self._read_cab()

    ##### METHODS FOR MANAGING CABs #####
    def get_cfheader(self):
        return self.cfheader

    def get_cffolder_list(self):
        return self.cffolder_list

    def get_cffile_list(self):
        return self.cffile_list

    def get_cfdata_list(self):
        return self.cfdata_list

    def dump_binary(self, filename):
        with open(filename, "wb") as f:
            f.write(self.dump_without_check())


    #####################################

    def _read_dword(self, handle):
        return struct.unpack("<I", handle.read(4))[0]

    def _read_word(self, handle):
        return struct.unpack("<H", handle.read(2))[0]

    def _read_byte(self, handle):
        return struct.unpack("<B", handle.read(1))[0]

    def read_cfheader(self, handle):
        """
        This method creates and returns a new CFHEADER object from the data read
        """

        parameters = {}
        signature = handle.read(4)
        if signature != "MSCF":
            raise Exception("Not a valid CAB File")
        parameters["reserved1"] = self._read_dword(handle)
        parameters["cbCabinet"] = self._read_dword(handle)
        parameters["reserved2"] = self._read_dword(handle)
        parameters["coffFiles"] = self._read_dword(handle)
        parameters["reserved3"] = self._read_dword(handle)
        parameters["versionMinor"] = self._read_byte(handle)
        parameters["versionMajor"] = self._read_byte(handle)
        parameters["cFolders"] = self._read_word(handle)
        parameters["cFiles"] =self._read_word(handle)
        parameters["flags"] = self._read_word(handle)
        parameters["setID"] = self._read_word(handle)
        parameters["iCabinet"] = self._read_word(handle)

        if parameters["flags"] & CFHEADER.cfhdrRESERVE_PRESENT:
            parameters["cbCFHeader"] = self._read_word(handle)
            parameters["cbCFFolder"] = self._read_byte(handle)
            parameters["cbCFData"] = self._read_byte(handle)
            parameters["abReserve"] = handle.read(parameters["cbCFHeader"])
        else:
            parameters["cbCFHeader"] = 0
            parameters["cbCFFolder"] = 0
            parameters["cbCFData"] = 0
            parameters["abReserve"] = ""

        if parameters["flags"] & CFHEADER.cfhdrPREV_CABINET:
            szCabinetPrev = handle.read(1)
            while szCabinetPrev[-1] != "\x00":
                szCabinetPrev += handle.read(1)
            parameters["szCabinetPrev"] = szCabinetPrev
            szDiskPrev = handle.read(1)
            while szDiskPrev[-1] != "\x00":
                szDiskPrev += handle.read(1)
            parameters["szDiskPrev"] = szDiskPrev
        else:
            parameters["szCabinetPrev"] = ""
            parameters["szDiskPrev"] = ""

        if parameters["flags"] & CFHEADER.cfhdrNEXT_CABINET:
            szCabinetNext = handle.read(1)
            while szCabinetNext[-1] != "\x00":
                szCabinetNext += handle.read(1)
            parameters["szCabinetNext"] = szCabinetNext
            szDiskNext = handle.read(1)
            while szDiskNext[-1] != "\x00":
                szDiskNext += handle.read(1)
            parameters["szDiskNext"] = szDiskNext
        else:
            parameters["szCabinetNext"] = ""
            parameters["szDiskNext"] = ""

        return CFHEADER.create_from_parameters(parameters=parameters)

    def read_folders(self, handle):
        result = []
        for i in range(self.cfheader.cFolders):
            parameters = {}
            parameters["coffCabStart"] = self._read_dword(handle)
            parameters["cCFData"] = self._read_word(handle)
            parameters["typeCompress"] = self._read_word(handle)
            if self.cfheader.flags & CFHEADER.cfhdrRESERVE_PRESENT:
                parameters["abReserve"] = handle.read(self.cfheader.cbCFFolder)
            else:
                parameters["abReserve"] = ""
            result.append(CFFOLDER.create_from_parameters(parameters=parameters))
        return result

    def read_files(self, handle):
        result = []
        for i in range(self.cfheader.cFiles):
            parameters = {}
            parameters["cbFile"] = self._read_dword(handle)
            parameters["uoffFolderStart"] = self._read_dword(handle)
            parameters["iFolder"] = self._read_word(handle)
            parameters["date"] = self._read_word(handle)
            parameters["time"] = self._read_word(handle)
            parameters["attribs"] = self._read_word(handle)
            szName = handle.read(1)
            while szName[-1] != "\x00":
                szName += handle.read(1)
            parameters["szName"] = szName
            result.append(CFFILE.create_from_parameters(parameters=parameters))
        return result

    def read_data(self, handle):
        result = []
        data_count = sum([cffolder.cCFData for cffolder in self.cffolder_list])
        for i in range(data_count):
            parameters = {}
            parameters["csum"] = self._read_dword(handle)
            parameters["cbData"] = self._read_word(handle)
            parameters["cbUncomp"] = self._read_word(handle)
            if self.cfheader.flags & CFHEADER.cfhdrRESERVE_PRESENT:
                parameters["abReserve"] = handle.read(self.cfheader.cbCFData)
            else:
                parameters["abReserve"] = ""
            parameters["ab"] = handle.read(parameters["cbData"])
            result.append(CFDATA.create_from_parameters(parameters=parameters))
        return result

    def _read_cab(self):
        """
        This method will try to read the CABs data to fill the structures
        """
        with open(self.filename, "rb") as f:
            self.cfheader = self.read_cfheader(handle=f)
            self.cffolder_list = self.read_folders(handle=f)
            self.cffile_list = self.read_files(handle=f)
            self.cfdata_list = self.read_data(handle=f)

    def __str__(self):
        data = str(self.cfheader)
        for i in self.cffolder_list:
            data += str(i)
        for i in self.cffile_list:
            data += str(i)
        for i in self.cfdata_list:
            data += str(i)
        return data

    def __repr__(self):
        data = repr(self.cfheader)
        for i in self.cffolder_list:
            data += repr(i)
        for i in self.cffile_list:
            data += repr(i)
        for i in self.cfdata_list:
            data += repr(i)
        return data

    def dump_without_check(self):
        data = self.cfheader._repr_without_checks()
        for i in self.cffolder_list:
            data += repr(i)
        for i in self.cffile_list:
            data += repr(i)
        for i in self.cfdata_list:
            data += repr(i)
        return data

