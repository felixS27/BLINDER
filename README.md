# BLINDER

## Aim
Development of an application, which blinds files in a folder to maximize the objectivity when manually analysing these files.

## How to use
Start application and enter the following:
1. File directory: Enter the full path to the directory containing the files to blind (or navigate with the 'Browse' button)
2. File suffix: Enter the suffix of your files (e.g. '.tif' or '.lif' or '.czi', but without the quotations marks. It doesn't have to be a image file format. As long it is a file suffix, this tool can work with anyfile extension/format.)
3. Press button 'Start Blinding Data!' to start the blinding.
4. When finished (indicated by displaying 'Finished!') either start new blinding with a new directory and suffix or end application by clicking the 'Close Blinder.' button

## How does it work
Based on the file suffix, BLINDER creates a list of all files in the given directory with the given suffix. Then BLINDER creates a list with values ranging from 1 to  total number of images/files. It then creates a mapping of each file with a random number from that list so that each file is assigned to one unique number. It then copies the files into a subfolder called 'blinded' and renames them according to this mapping. Along with the copied files BLINDER stores the mapping as a tab-separated .csv file in the 'blinded' subfolder for later unblinding of the data.
When in source folder already contains a blinded folder, the user has three choices:
1. Overwrite the data in the blinded folder with the new files.
2. Append the new data to the existing. Hereby the numbering continues from the already existing blinded files.
3. Abort and manually take care of the data in the blinded folder.

## Contribution
New ideas about features or reporting a bug. Please feel free to open a issue. I am happy about suggestions.