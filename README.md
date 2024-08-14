# BLINDER

## Aim
Development of an application, which blinds files in a folder to maximize the objectivity when manually analysing these files.

## How to use
Download the whole project as zip. If you just want to use the application delete everything from the download except the content of the dist folder of the respective build for the machien you are working on.
Upon starting the application or the script a window opens where you can enter following:
- File directory: Enter the full path to the directory containing the files to blind (or navigate with the 'Browse' button)
- File suffix: Enter the suffix of your files (e.g. '.tif' or '.txt')
- Press button 'Start Blinding Data!' to start the blinding.
- When finished (indicated by displaying 'Finished!') either start new blinding with a new directory and suffix or end application by clicking the 'End Blinding.' button

## How does it work
Based on the file suffix, BLINDER creates a list of all files in the given directory with the given suffix. Then BLINDER creates a list with values ranging from 0 to (number of images) - 1. It then creates a mapping of each file with a random number from that list so that each file is assigned to one unique number. It then copies the files into a subfolder called 'blinded' and renames them according to this mapping. In the end BLINDER stores the mapping as a .csv file in the 'blinded' subfolder for later unblinding of the data.
