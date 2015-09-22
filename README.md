# PyCAB
[![Build Status](https://travis-ci.org/n3k/PyCAB.svg)](https://travis-ci.org/n3k/PyCAB)
[![Latest Version](https://img.shields.io/pypi/v/pycab.svg)](https://pypi.python.org/pypi/pycab/)
[![Downloads](https://img.shields.io/pypi/dm/pycab.svg)](https://pypi.python.org/pypi/pycab/)

A Python library to manipulate Microsoft Cabinet files


## Features
* Write simple .CAB files
* Write .CAB SETs
* Read .CAB structure
* Extract data from simple .CABs and SETs

## Author
* [Enrique Nissim](https://twitter.com/kiqueNissim) (developer)


## Todo
* Improve the current test code coverage
* Improve the manager interface for usage
* Implement MSZIP

## Writer Usage

```python
    folder = CABFolderUnit(name="folder", filename_list=[r"./TestsFiles/pe101.jpg",
					 		 r"./TestsFiles/andy_C.mp3",
							 r"./TestsFiles/super_saiyajin.jpg"
							 ])
    manager = CABManager()
    manager.create_cab(cab_folders=[folder], cab_name="my_cab_[x].cab", cab_size=1474*1024*16)
    manager.flush_cabset_to_disk(output_dir=r"./TestsFiles/")
```


## Information about CABINET format
https://msdn.microsoft.com/en-us/library/bb417343.aspx

