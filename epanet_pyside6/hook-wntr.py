from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
import os

# Collect all WNTR data and binaries
datas = collect_data_files('wntr')
binaries = collect_dynamic_libs('wntr')

# Explicitly add EPANET libraries
import wntr
wntr_path = os.path.dirname(wntr.__file__)
epanet_lib_path = os.path.join(wntr_path, 'epanet', 'libepanet', 'darwin-arm')

if os.path.exists(epanet_lib_path):
    for lib in ['libepanet2.dylib', 'libepanetmsx.dylib']:
        lib_file = os.path.join(epanet_lib_path, lib)
        if os.path.exists(lib_file):
            binaries.append((lib_file, 'wntr/epanet/libepanet/darwin-arm'))

hiddenimports = ['wntr.epanet.toolkit', 'wntr.epanet.util']
