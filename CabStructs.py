# coding=utf-8
import struct
import datetime
from abc import ABCMeta, abstractmethod
from weakref import WeakKeyDictionary

class DWORDValue(object):
    """A descriptor for DWORD values"""
    def __init__(self):
        self.data = WeakKeyDictionary()

    def __get__(self, obj, type):
        return struct.unpack("<I", self.data.get(obj))[0]

    def __set__(self, obj, value):
        try:
            v = struct.pack("<I", value)
            self.data[obj] = v
        except struct.error as e:
            raise ValueError("Only DWORD values are allowed: %08x" % value)


class WORDValue(object):
    """A descriptor for WORD values"""
    def __init__(self):
        self.data = WeakKeyDictionary()

    def __get__(self, obj, type):
        return struct.unpack("<H",self.data.get(obj))[0]

    def __set__(self, obj, value):
        try:
            v = struct.pack("<H", value)
            self.data[obj] = v
        except struct.error as e:
            raise ValueError("Only WORD values are allowed: %04x" % value)

class BYTEValue(object):
    """A descriptor for BYTE values"""
    def __init__(self):
        self.data = WeakKeyDictionary()

    def __get__(self, obj, type):
        return struct.unpack("<B", self.data.get(obj))[0]

    def __set__(self, obj, value):
        try:
            v = struct.pack("<B", value)
            self.data[obj] = v
        except struct.error as e:
            raise ValueError("Only BYTE values are allowed: %02x" % value)


class CABFileFormat(object):
    """
    It provides a common set of methods for managing cabs
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_cfheader(self):
        pass

    @abstractmethod
    def get_cffolder_list(self):
        pass

    @abstractmethod
    def get_cffile_list(self):
        pass

    @abstractmethod
    def get_cfdata_list(self):
        pass

    def dump(self, filename):
        with open(filename, "wt") as f:
            f.write(str(self))

    def dump_binary(self, filename):
        with open(filename, "wb") as f:
            f.write(self.__repr__())


class CFHEADER(object):

    """
    typedef struct _CFHEADER
    {
      u1  signature[4];     /*inet file signature */
      u4  reserved1;        /* Reserved field, set to zero. ??? */
      u4  cbCabinet;        /* size of this cabinet file in bytes */
      u4  reserved2;        /* Reserved field, set to zero. ??? */
      u4  coffFiles;        /* offset of the first CFFILE entry */
      u4  reserved3;        /* Reserved field, set to zero. ??? */
      u1  versionMinor;     /* cabinet file format version, minor */
      u1  versionMajor;     /* cabinet file format version, major */
      u2  cFolders;         /* number of CFFOLDER entries in this */
                            /*    cabinet */
      u2  cFiles;           /* number of CFFILE entries in this cabinet */
      u2  flags;            /* cabinet file option indicators */
      u2  setID;            /* must be the same for all cabinets in a */
                            /*    set */
      u2  iCabinet;         /* number of this cabinet file in a set */
      u2  cbCFHeader;       /* (optional) size of per-cabinet reserved */
                            /*    area */
      u1  cbCFFolder;       /* (optional) size of per-folder reserved */
                            /*    area */
      u1  cbCFData;         /* (optional) size of per-datablock reserved */
                            /*    area */
      u1  abReserve[];       /* (optional) per-cabinet reserved area */
      u1  szCabinetPrev[];   /* (optional) name of previous cabinet file */
      u1  szDiskPrev[];      /* (optional) name of previous disk */
      u1  szCabinetNext[];   /* (optional) name of next cabinet file */
      u1  szDiskNext[];      /* (optional) name of next disk */
    } CFHEADER, *PCFHEADER;
    """

    # flags Values
    cfhdrPREV_CABINET    = 0x0001
    cfhdrNEXT_CABINET    = 0x0002
    cfhdrRESERVE_PRESENT = 0x0004

    @property
    def signature(self):
        return self._signature
    @signature.setter
    def signature(self, value):
        if len(value) == 4:
            self._signature = value
        else:
            self._signature = "MSCF"

    reserved1 = DWORDValue()
    cbCabinet = DWORDValue()
    reserved2 = DWORDValue()
    coffFiles = DWORDValue()
    reserved3 = DWORDValue()
    versionMinor = BYTEValue()
    versionMajor = BYTEValue()
    cFolders = WORDValue()
    cFiles = WORDValue()
    flags = WORDValue()
    setID = WORDValue()
    iCabinet = WORDValue()

    # From this point, the fields are optional
    cbCFHeader = WORDValue()
    cbCFFolder = BYTEValue()
    cbCFData = BYTEValue()

    @property
    def abReserve(self):
        return self._abReserve
    @abReserve.setter
    def abReserve(self, value):
        self._abReserve = value

    @property
    def szCabinetPrev(self):
        return self._szCabinetPrev
    @szCabinetPrev.setter
    def szCabinetPrev(self, value):
        self._szCabinetPrev = value

    @property
    def szDiskPrev(self):
        return self._szDiskPrev
    @szDiskPrev.setter
    def szDiskPrev(self, value):
        self._szDiskPrev = value

    @property
    def szCabinetNext(self):
        return self._szCabinetNext
    @szCabinetNext.setter
    def szCabinetNext(self, value):
        self._szCabinetNext = value

    @property
    def szDiskNext(self):
        return self._szDiskNext
    @szDiskNext.setter
    def szDiskNext(self, value):
        self._szDiskNext = value

    def __init__(self, flags, reserve):
        """
        reserve is a dictionary with the follow
        {
        'cbCFHeader' : value,
        'cbCFFolder' : value,
        'cbCFData' : value
        }
        """

        self.signature = "MSCF"
        self.reserved1 = 0x00000000
        self.cbCabinet = 0x00000000
        self.reserved2 = 0x00000000
        self.coffFiles = 0x00000000
        self.reserved3 = 0x00000000
        self.versionMinor = 0x03
        self.versionMajor = 0x01
        self.cFolders = 0x0000
        self.cFiles = 0x0000

        self.flags = flags

        self.setID = 0x0000
        self.iCabinet = 0x0000

        self.cbCFHeader = reserve["cbCFHeader"] if reserve["cbCFHeader"] > 0 else 0x0000
        self.cbCFFolder = reserve["cbCFFolder"] if reserve["cbCFFolder"] > 0 else 0x00
        self.cbCFData = reserve["cbCFData"] if reserve["cbCFData"] > 0 else 0x00

        if self.flags & CFHEADER.cfhdrRESERVE_PRESENT:
            self.abReserve = "\x41" * self.cbCFHeader
        else:
            self.abReserve = ""

        self.szCabinetPrev = ""
        self.szDiskPrev = ""
        self.szCabinetNext = ""
        self.szDiskNext = ""

        self.cffolder_list = []

    @classmethod
    def create_from_parameters(cls, parameters={}):

        flags = parameters["flags"]
        reserve = {
            "cbCFHeader": parameters.get("cbCFHeader", 0),
            "cbCFFolder": parameters.get("cbCFFolder", 0),
            "cbCFData": parameters.get("cbCFData", 0)
        }

        instance = cls(flags=flags, reserve=reserve)
        instance.reserved1 = parameters["reserved1"]
        instance.cbCabinet = parameters["cbCabinet"]
        instance.reserved2 = parameters["reserved2"]
        instance.coffFiles = parameters["coffFiles"]
        instance.reserved3 = parameters["reserved3"]
        instance.versionMinor = parameters["versionMinor"]
        instance.versionMajor = parameters["versionMajor"]
        instance.cFolders = parameters["cFolders"]
        instance.cFiles = parameters["cFiles"]
        instance.flags = flags
        instance.setID = parameters["setID"]
        instance.iCabinet = parameters["iCabinet"]
        instance.cbCFHeader = parameters["cbCFHeader"]
        instance.cbCFFolder = parameters["cbCFFolder"]
        instance.cbCFData = parameters["cbCFData"]
        instance.abReserve = parameters["abReserve"]
        instance.szCabinetPrev = parameters["szCabinetPrev"]
        instance.szDiskPrev = parameters["szDiskPrev"]
        instance.szCabinetNext = parameters["szCabinetNext"]
        instance.szDiskNext = parameters["szDiskNext"]
        return instance


    def add_folder(self, cffolder):
        # Update cFolders :)
        cffolder.cfheader.cFolders += 1
        self.cffolder_list.append(cffolder)

    def __repr__(self):
        data = ""
        data += self.signature
        data += struct.pack("<I", self.reserved1)
        data += struct.pack("<I", self.cbCabinet)
        data += struct.pack("<I", self.reserved2)
        data += struct.pack("<I", self.coffFiles)
        data += struct.pack("<I", self.reserved3)
        data += struct.pack("<B", self.versionMinor)
        data += struct.pack("<B", self.versionMajor)
        data += struct.pack("<H", self.cFolders)
        data += struct.pack("<H", self.cFiles)
        data += struct.pack("<H", self.flags)
        data += struct.pack("<H", self.setID)
        data += struct.pack("<H", self.iCabinet)

        if self.flags & self.cfhdrRESERVE_PRESENT:
            data += struct.pack("<H", self.cbCFHeader)
            data += struct.pack("<B", self.cbCFFolder)
            data += struct.pack("<B", self.cbCFData)
            data += self.abReserve

        if self.flags & self.cfhdrPREV_CABINET:
            data += self.szCabinetPrev
            data += self.szDiskPrev

        if self.flags & self.cfhdrNEXT_CABINET:
            data += self.szCabinetNext
            data += self.szDiskNext

        return data

    def __str__(self):
        data = "\nCFHEADER\n"
        data += "Signature: %s\n" % self.signature
        data += "reserved1: %08x\n" % self.reserved1
        data += "cbCabinet: %08x\n" % self.cbCabinet
        data += "reserved2: %08x\n" % self.reserved2
        data += "coffFiles: %08x\n" % self.coffFiles
        data += "reserved3: %08x\n" % self.reserved3
        data += "versionMinor: %02x\n" % self.versionMinor
        data += "versionMajor: %02x\n" % self.versionMajor
        data += "cFolders: %04x\n" % self.cFolders
        data += "cFiles: %04x\n" % self.cFiles
        data += "flags: %04x\n" % self.flags
        data += "setID: %04x\n" % self.setID
        data += "iCabinet: %04x\n" % self.iCabinet


        data += "cbCFheader: %04x\n" % self.cbCFHeader
        data += "cbCFFolder: %02x\n" % self.cbCFFolder
        data += "cbCFFolder: %02x\n" % self.cbCFData
        data += "abReserve: %s\n" % self.abReserve


        data += "szCabinetPrev: %s\n" % self.szCabinetPrev
        data += "szDiskPrev: %s\n" % self.szDiskPrev


        data += "szCabinetNext: %s\n" % self.szCabinetNext
        data += "szDiskNext: %s\n" %self.szDiskNext

        """
        if self.flags & self.cfhdrRESERVE_PRESENT:
            data += "cbCFheader: %04x\n" % self.cbCFHeader
            data += "cbCFFolder: %02x\n" % self.cbCFFolder
            data += "cbCFFolder: %02x\n" % self.cbCFData
            data += "abReserve: %s\n" % self.abReserve

        if self.flags & self.cfhdrPREV_CABINET:
            data += "szCabinetPrev: %s\n" % self.szCabinetPrev
            data += "szDiskPrev: %s\n" % self.szDiskPrev

        if self.flags & self.cfhdrNEXT_CABINET:
            data += "szCabinetNext: %s\n" % self.szCabinetNext
            data += "szDiskNext: %s\n" %self.szDiskNext
        """
        return data

    def __len__(self):
        signature = 4
        reserved1 = 4
        cbCabinet = 4
        reserved2 = 4
        coffFiles = 4
        reserved3 = 4
        versionMinor = 1
        versionMajor = 1
        cFolders = 2
        cFiles = 2
        flags = 2
        setID = 2
        iCabinet = 2
        cbCFHeader = 2 if self.cbCFHeader != 0x0000 or self.cbCFFolder != 0x00 or self.cbCFData != 0x00 else 0
        cbCFFolder = 1 if self.cbCFHeader != 0x0000 or self.cbCFFolder != 0x00 or self.cbCFData != 0x00 else 0
        cbCFData = 1 if self.cbCFHeader != 0x0000 or self.cbCFFolder != 0x00 or self.cbCFData != 0x00 else 0
        abReserve = len(self.abReserve)
        szCabinetPrev = len(self.szCabinetPrev)
        szDiskPrev = len(self.szDiskPrev)
        szCabinetNext = len(self.szCabinetNext)
        szDiskNext = len(self.szDiskNext)

        size = signature + reserved1 + cbCabinet + reserved2 + coffFiles + reserved3 + versionMinor + versionMajor \
               + cFolders + cFiles + flags + setID + iCabinet + cbCFHeader + cbCFFolder + cbCFData + abReserve \
               + szCabinetNext + szDiskNext + szDiskPrev + szCabinetPrev

        return size

    def _repr_without_checks(self):
        data = ""
        data += self.signature
        data += struct.pack("<I", self.reserved1)
        data += struct.pack("<I", self.cbCabinet)
        data += struct.pack("<I", self.reserved2)
        data += struct.pack("<I", self.coffFiles)
        data += struct.pack("<I", self.reserved3)
        data += struct.pack("<B", self.versionMinor)
        data += struct.pack("<B", self.versionMajor)
        data += struct.pack("<H", self.cFolders)
        data += struct.pack("<H", self.cFiles)
        data += struct.pack("<H", self.flags)
        data += struct.pack("<H", self.setID)
        data += struct.pack("<H", self.iCabinet)
        data += struct.pack("<H", self.cbCFHeader) if (self.flags & CFHEADER.cfhdrRESERVE_PRESENT) \
                                                      or self.cbCFHeader != 0x0000 else ""
        data += struct.pack("<B", self.cbCFFolder) if (self.flags & CFHEADER.cfhdrRESERVE_PRESENT) \
                                                      or self.cbCFFolder != 0x00 else ""
        data += struct.pack("<B", self.cbCFData) if (self.flags & CFHEADER.cfhdrRESERVE_PRESENT) \
                                                      or self.cbCFFolder != 0x00 else ""
        data += self.abReserve
        data += self.szCabinetPrev
        data += self.szDiskPrev
        data += self.szCabinetNext
        data += self.szDiskNext
        return data

    @classmethod
    def get_flags_options(cls):
        return [
            CFHEADER.cfhdrPREV_CABINET,
            CFHEADER.cfhdrNEXT_CABINET,
            CFHEADER.cfhdrRESERVE_PRESENT
        ]

class CFFOLDER(object):
    """
    struct CFFOLDER
    {
      u4  coffCabStart;  /* offset of the first CFDATA block in this
                         /*    folder */
      u2  cCFData;       /* number of CFDATA blocks in this folder */
      u2  typeCompress;  /* compression type indicator */
      u1  abReserve[];   /* (optional) per-folder reserved area */
    };
    """
    tcompMASK_TYPE          = 0x000F    # Mask for compression type
    tcompTYPE_NONE          = 0x0000    # No compression
    tcompTYPE_MSZIP         = 0x0001    # MSZIP
    tcompTYPE_QUANTUM       = 0x0002    # Quantum
    tcompTYPE_LZX           = 0x0003    # LZX

    # Absolute file offset of first CFDATA block for THIS folder
    coffCabStart = DWORDValue()
    cCFData = WORDValue()
    typeCompress = WORDValue()

    @property
    def abReserve(self):
        return self._abReserve
    @abReserve.setter
    def abReserve(self, value):
        self._abReserve = value


    # This is extra metadata for helping in the creation of cab files
    # it isn´t used in the specification
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    def __init__(self, cfheader=None, folder_id=0):
        # The cfheader to which this CFFolder correspond
        self.cfheader = cfheader

        self.coffCabStart = 0x00000000
        self.cCFData = 0x0000
        self.typeCompress = CFFOLDER.tcompTYPE_NONE
        self.abReserve = ""

        self.folder_id = folder_id  # To help identify the folder
        self.cffile_list = []
        self.cfdata_list = []

        # Check if abReserve must be filled
        self.fill_reserve()

    def fill_reserve(self):
        try:
            cfheader = self.cfheader
            if cfheader.flags & CFHEADER.cfhdrRESERVE_PRESENT:
                self.abReserve = "\x41" * cfheader.cbCFFolder
        except AttributeError:
            pass

    @classmethod
    def create_from_parameters(cls, parameters={}):
        instance = cls()
        instance.coffCabStart = parameters["coffCabStart"]
        instance.cCFData = parameters["cCFData"]
        instance.typeCompress = parameters["typeCompress"]
        instance.abReserve = parameters["abReserve"]
        return instance

    def add_data(self, cfdata):
        self.cfdata_list.append(cfdata)
        #cCFData
        self.cCFData += 1

    def add_file(self, cffile):
        self.cffile_list.append(cffile)
        # Update cFiles in CFHEADER
        self.cfheader.cFiles += 1

    def __len__(self):
        result = 4 + 2 + 2 + len(self.abReserve)
        #print "len of cffolder: %d" % result
        return result

    def __repr__(self):
        data = ""
        data += struct.pack("<I", self.coffCabStart)
        data += struct.pack("<H", self.cCFData)
        data += struct.pack("<H", self.typeCompress)
        data += self.abReserve
        return data

    def __str__(self):
        data = "\nCFFOLDER\n"
        data += "coffCabStart: %08x\n" % self.coffCabStart
        data += "cCFData: %04x\n" % self.cCFData
        data += "typeCompress: %04x\n" % self.typeCompress
        data += "abReserve: %s\n" % self.abReserve
        return data

    @classmethod
    def get_typeCompress_options(cls):
        return [
            CFFOLDER.tcompMASK_TYPE,
            CFFOLDER.tcompTYPE_NONE,
            CFFOLDER.tcompTYPE_MSZIP,
            CFFOLDER.tcompTYPE_QUANTUM,
            CFFOLDER.tcompTYPE_LZX
        ]

class CFFILE(object):
    """
    struct CFFILE
    {
      u4  cbFile;           /* uncompressed size of this file in bytes */
      u4  uoffFolderStart;  /* uncompressed offset of this file in the folder */
      u2  iFolder;          /* index into the CFFOLDER area */
      u2  date;             /* date stamp for this file */
      u2  time;             /* time stamp for this file */
      u2  attribs;          /* attribute flags for this file */
      u1  szName[];         /* name of this file */
    };
    """

    #iFolder Values
    ifoldTHIS_CABINET            = 0x0000
    ifoldCONTINUED_FROM_PREV     = 0xFFFD
    ifoldCONTINUED_TO_NEXT       = 0xFFFE
    ifoldCONTINUED_PREV_AND_NEXT = 0xFFFF

    #attribs Values
    _A_RDONLY       = 0x01  # file is read-only
    _A_HIDDEN       = 0x02  # file is hidden
    _A_SYSTEM       = 0x04  # file is a system file
    _A_ARCH         = 0x20  # file modified since last backup
    _A_EXEC         = 0x40  # run after extraction
    _A_NAME_IS_UTF  = 0x80  # szName[] contains UTF

    cbFile = DWORDValue()
    uoffFolderStart = DWORDValue()
    iFolder = WORDValue()
    #format ((year - 1980) << 9)+(month << 5)+(day))
    date = WORDValue()
    #format (hour << 11)+(minute << 5)+(seconds/2)
    time = WORDValue()
    attribs = WORDValue()

    @property
    def szName(self):
        return self._szName
    @szName.setter
    def szName(self, value):
        self._szName = value

    def __init__(self, cffolder=None, total_len=0, filename=""):
        # The CFFolder to which this CFFile corresponds
        self.cffolder = cffolder

        self.cbFile = total_len
        self.uoffFolderStart = 0x000000000 # This is calculated later
        # Set iFolder to the current FolderID
        self.iFolder = cffolder.folder_id if cffolder is not None else 0x0000
        now = datetime.datetime.now()
        #format ((year - 1980) << 9)+(month << 5)+(day))
        self.date = ((now.year-1980)<<9)+(now.month<<5)+(now.day)
        #format (hour << 11)+(minute << 5)+(seconds/2)
        self.time = (now.hour<<11)+(now.minute<<5)+(now.second/2)
        self.attribs = CFFILE._A_ARCH
        self.szName = filename

    @classmethod
    def create_from_parameters(cls, parameters={}):
        instance = cls()
        instance.cbFile = parameters["cbFile"]
        instance.uoffFolderStart = parameters["uoffFolderStart"]
        instance.iFolder = parameters["iFolder"]
        instance.date = parameters["date"]
        instance.time = parameters["time"]
        instance.attribs = parameters["attribs"]
        instance.szName = parameters["szName"]
        return instance

    @classmethod
    def get_attribs_options(cls):
        return [
            CFFILE._A_RDONLY,
            CFFILE._A_HIDDEN,
            CFFILE._A_SYSTEM,
            CFFILE._A_ARCH,
            CFFILE._A_EXEC,
            CFFILE._A_NAME_IS_UTF
        ]

    @classmethod
    def get_iFolder_options(cls):
        return [
            CFFILE.ifoldTHIS_CABINET,
            CFFILE.ifoldCONTINUED_FROM_PREV,
            CFFILE.ifoldCONTINUED_TO_NEXT,
            CFFILE.ifoldCONTINUED_PREV_AND_NEXT
        ]

    def __len__(self):
        result = 4 + 4 + 2 + 2 + 2 + 2 + len(self.szName)
        #print "len of cffile: %d" % result
        return result

    def __repr__(self):
        data = ""
        data += struct.pack("<I", self.cbFile)
        data += struct.pack("<I", self.uoffFolderStart)
        data += struct.pack("<H", self.iFolder)
        data += struct.pack("<H", self.date)
        data += struct.pack("<H", self.time)
        data += struct.pack("<H", self.attribs)
        data += self.szName
        return data

    def __str__(self):
        data = "\nCFFILE\n"
        data += "cbFile: %08x\n" % self.cbFile
        data += "uoffFolderStart: %08x\n" % self.uoffFolderStart
        data += "iFolder: %04x\n" % self.iFolder
        data += "date: %04x\n" % self.date
        data += "time: %04x\n" % self.time
        data += "attribs: %04x\n" % self.attribs
        data += "szName: %s\n" % self.szName
        return data


class CFDATA(object):
    """
    struct CFDATA
    {
      u4  csum;         /* checksum of this CFDATA entry */
      u2  cbData;       /* number of compressed bytes in this block */
      u2  cbUncomp;     /* number of uncompressed bytes in this block */
      u1  abReserve[];  /* (optional) per-datablock reserved area */
      u1  ab[cbData];   /* compressed data bytes */
    };
    """

    csum = DWORDValue()
    cbData = WORDValue()
    cbUncomp = WORDValue()

    @property
    def abReserve(self):
        return self._abReserve
    @abReserve.setter
    def abReserve(self, value):
        self._abReserve = value

    @property
    def ab(self):
        return self._ab
    @ab.setter
    def ab(self, value):
        self._ab = value

    def __init__(self, cffolder=None, data=""):
        self.cffolder = cffolder

        self.csum = 0x00000000

        # 0x8000 is the max allowed in a CFDATA
        size = len(data)
        #print "SIZE: %04x" % size
        #if size > 0x8000:
        #    size = 0x8000
        self.cbData = size
        self.cbUncomp = size
        self.abReserve = ""
        self.ab = data

        # Check if abReserve must be filled
        self.fill_reserve()

    def fill_reserve(self):
        try:
            cfheader = self.cffolder.cfheader
            if cfheader.flags & CFHEADER.cfhdrRESERVE_PRESENT:
                self.abReserve = "\x41" * cfheader.cbCFData
        except AttributeError:
            pass

    @classmethod
    def create_from_parameters(cls, parameters={}):
        instance = cls()
        instance.csum = parameters["csum"]
        instance.cbData = parameters["cbData"]
        instance.cbUncomp = parameters["cbUncomp"]
        instance.abReserve = parameters["abReserve"]
        instance.ab = parameters["ab"]
        return instance

    def __len__(self):
        result = 4 + 2 + 2 + len(self.abReserve) + len(self.ab)
        #print "len of cfdata %d\n" % result
        return result

    def __repr__(self):
        data = ""
        data += struct.pack("<I", self.csum)
        data += struct.pack("<H", self.cbData)
        data += struct.pack("<H", self.cbUncomp)
        data += self.abReserve
        data += self.ab
        return data

    def __str__(self):
        data = "\nCFDATA\n"
        data += "csum: %08x\n" % self.csum
        data += "cbData: %04x\n" % self.cbData
        data += "cbUncomp: %04x\n" % self.cbUncomp
        data += "abReserve: %s\n" % self.abReserve
        data += "ab: %04x bytes of data\n" % len(self.ab)
        return data