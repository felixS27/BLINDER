from pathlib import Path
import random
import shutil
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

# Define source dir of files
source_path = Path('/Users/fschneider/examplefolder')
# Define destination dir to copy to
destination_dir = source_path/'blinded'
# Make dir if non existant
if not destination_dir.exists():
    destination_dir.mkdir()
# Get all files based on specific suffix
files = sorted([file for file in source_path.glob('*.txt')])
# Get total number of files
number_of_files = len(files)
# Get values for blinding data
index=list(range(number_of_files))
# random shuffle values for assigning
random.shuffle(index)
# Create dict for assigning each file to its blinded version
file_name_mapping={f'{file.name}':f'{idx+1:03d}{file.suffix}' for file,idx in zip(files,index)}
print(file_name_mapping)
# function to do the actual copying
def copy_and_rename(source_file,destination_file):
     shutil.copy(source_file,destination_file)

# with ThreadPoolExecutor() as executor:
#         futures = [executor.submit(copy_and_rename,
#                                    source_path/original_file,
#                                    destination_dir/file_copy) for original_file,file_copy in file_name_mapping.items()]
#         for future in futures:
#             future.result() 

pd.DataFrame({'OriginalFile':[key for key in file_name_mapping.keys()],
       'BlindedFile':[value for value in file_name_mapping.values()]}).to_csv(destination_dir/'key.csv',index=False,sep='\t')