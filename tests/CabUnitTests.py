__author__ = 'n3k'

import unittest
import random
import datetime

from pycab.CabStructs import CFHEADER, CFFOLDER, CFFILE, CFDATA


class StructsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_cfheader_signature(self):
        """
        This method checks a cfheader complies with basic specification
        """
        reserve = {'cbCFHeader': 0,  'cbCFFolder': 0, 'cbCFData': 0}
        cfheader = CFHEADER(flags=0, reserve=reserve)

        self.assertEquals("MSCF", cfheader.signature)
        self.assertEquals(0x01, cfheader.versionMajor)
        self.assertEquals(0x03, cfheader.versionMinor)

    def test_cfheader_reserve(self):
        """
        This method checks a cfheader actually reserves the bytes that are specified
        """
        bytes_to_reserve = random.randint(1, 30)
        reserve = {'cbCFHeader': bytes_to_reserve,  'cbCFFolder': 0, 'cbCFData': 0}
        cfheader = CFHEADER(flags=CFHEADER.cfhdrRESERVE_PRESENT, reserve=reserve)

        self.assertEquals(CFHEADER.cfhdrRESERVE_PRESENT, cfheader.flags & CFHEADER.cfhdrRESERVE_PRESENT)
        self.assertEquals(bytes_to_reserve, cfheader.cbCFHeader)
        self.assertEquals(bytes_to_reserve, len(cfheader.abReserve))
        self.assertEquals(len(cfheader), len(repr(cfheader)))

    def test_cfheader_create_from_params(self):
        """
        This method tests the creation with parameters interface
        """
        params = {
            "reserved1": 0xCAFEBABE,
            "cbCabinet": 0x1000,
            "reserved2": 0xCAFEBABE,
            "coffFiles": 0x1000,
            "reserved3": 0xCAFEBABE,
            "versionMinor": 0x4d,
            "versionMajor": 0x5a,
            "cFolders": 0x1000,
            "cFiles": 0x1000,
            "flags": 0,
            "setID": 0x4141,
            "iCabinet": 0,
            "cbCFHeader": 0xFFFF,
            "cbCFFolder": 0xFF,
            "cbCFData": 0xFF,
            "abReserve": "t r a v e s t i s",
            "szCabinetPrev": "Cab Not Found",
            "szDiskPrev": "Disk Not Found",
            "szCabinetNext": "Cab Not Found",
            "szDiskNext": "Disk Not Found",
            }

        cfheader = CFHEADER.create_from_parameters(parameters=params)

        self.assertEquals("MSCF", cfheader.signature)
        self.assertEquals(0xCAFEBABE, cfheader.reserved1)
        self.assertEquals(0x1000, cfheader.cbCabinet)
        self.assertEquals(0xCAFEBABE, cfheader.reserved2)
        self.assertEquals(0x1000, cfheader.coffFiles)
        self.assertEquals(0xCAFEBABE, cfheader.reserved3)
        self.assertEquals("MZ", chr(cfheader.versionMinor)+chr(cfheader.versionMajor))
        self.assertEquals(0x1000, cfheader.cFolders)
        self.assertEquals(0x1000, cfheader.cFiles)
        self.assertEquals(0x00, cfheader.flags)
        self.assertEquals(0x4141, cfheader.setID)
        self.assertEquals(0x00, cfheader.iCabinet)
        self.assertEquals(0xFFFF, cfheader.cbCFHeader)
        self.assertEquals(0xFF, cfheader.cbCFFolder)
        self.assertEquals(0xFF, cfheader.cbCFData)
        self.assertEquals("t r a v e s t i s", cfheader.abReserve)
        self.assertEquals("Cab Not Found", cfheader.szCabinetPrev)
        self.assertEquals("Disk Not Found", cfheader.szDiskPrev)
        self.assertEquals("Cab Not Found", cfheader.szCabinetNext)
        self.assertEquals("Disk Not Found", cfheader.szDiskNext)
        self.assertEquals(len(cfheader), len(cfheader._repr_without_checks()))

    def test_cfheader_add_folder(self):
        reserve = {'cbCFHeader': 0,  'cbCFFolder': 0, 'cbCFData': 0}
        cfheader = CFHEADER(flags=0, reserve=reserve)
        cffolder = CFFOLDER(cfheader=cfheader)
        cfheader.add_folder(cffolder)
        self.assertEquals(1, cfheader.cFolders)

    def test_cffolder_with_reserve(self):
        reserve = {'cbCFHeader': 0,  'cbCFFolder': 20, 'cbCFData': 0}
        cfheader = CFHEADER(flags=CFHEADER.cfhdrRESERVE_PRESENT, reserve=reserve)
        cffolder = CFFOLDER(cfheader=cfheader)
        self.assertEquals(20, len(cffolder.abReserve))

    def test_cffolder_add_file(self):
        reserve = {'cbCFHeader': 0,  'cbCFFolder': 0, 'cbCFData': 0}
        cfheader = CFHEADER(flags=0, reserve=reserve)
        cffolder = CFFOLDER(cfheader=cfheader)
        cffile = CFFILE(cffolder=cffolder, filename="trav.txt")
        cffolder.add_file(cffile)
        self.assertEquals(1, cfheader.cFiles)

    def test_cffolder_add_data(self):
        reserve = {'cbCFHeader': 0,  'cbCFFolder': 0, 'cbCFData': 0}
        cfheader = CFHEADER(flags=0, reserve=reserve)
        cffolder = CFFOLDER(cfheader=cfheader)
        cfdata = CFDATA(data="testdata1")
        cffolder.add_data(cfdata)
        cfdata = CFDATA(data="testdata2")
        cffolder.add_data(cfdata)
        self.assertEquals(2, cffolder.cCFData)

    def test_cffile_normal_creation(self):
        cffile = CFFILE(total_len=0x1000, filename="trav.txt")
        self.assertEquals(0x1000, cffile.cbFile)
        self.assertEquals("trav.txt", cffile.szName)
        self.assertEquals(len(cffile), len(repr(cffile)))

    def test_cffile_create_from_parameters(self):
        now = datetime.datetime.now()
        params = {
            "cbFile": 0x1000,
            "uoffFolderStart": 0x20202020,
            "iFolder": 0x01,
            "date": ((now.year-1980)<<9)+(now.month<<5)+(now.day),
            "time": (now.hour<<11)+(now.minute<<5)+(now.second/2),
            "attribs": CFFILE._A_EXEC,
            "szName": "trav.txt"
        }
        cffile = CFFILE.create_from_parameters(parameters=params)
        self.assertEquals("trav.txt", cffile.szName)
        self.assertEquals(0x20202020, cffile.uoffFolderStart)
        self.assertEquals(len(cffile), len(repr(cffile)))

    def test_cfdata_normal_creation(self):
        data = "this is the data"
        cfdata = CFDATA(data=data)
        self.assertEquals(data, cfdata.ab)
        self.assertEquals(len(data), cfdata.cbData)
        self.assertEquals(len(data), cfdata.cbUncomp)
        self.assertEquals(len(cfdata), len(repr(cfdata)))

    def test_cfdata_with_reserve(self):
        data = "this is the data"
        reserve = {'cbCFHeader': 0,  'cbCFFolder': 0, 'cbCFData': 20}
        cfheader = CFHEADER(flags=CFHEADER.cfhdrRESERVE_PRESENT, reserve=reserve)
        cffolder = CFFOLDER(cfheader=cfheader)
        cfdata = CFDATA(cffolder=cffolder, data=data)
        self.assertEquals(20, len(cfdata.abReserve))
        self.assertEquals(len(cfdata), len(repr(cfdata)))


if __name__ == "__main__":
    unittest.main()


