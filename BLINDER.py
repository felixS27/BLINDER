import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
import random
import shutil
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import webbrowser
from datetime import datetime

# toplevel function
def blind_data():
    check_label_filling()

# check for correct usage (all fields are filled out correctly)
def check_label_filling():
    source_path = Path(dir_path.get())
    if source_path.exists() and len(str(source_path))>1:
        if len(file_suffix.get())>0:
            if file_suffix.get().startswith("."):
                files = sorted([file for file in source_path.glob(f'*{file_suffix.get()}')])
                number_of_files = len(files)
                if number_of_files > 0:
                    check_blinded_folder(source_path,files,number_of_files)
                else:
                    open_errormessage(f'Directory does not contain files with {file_suffix.get()} suffix.',0)
            else:
                open_errormessage("File suffix does not start with a \".\"",0)
        else:
            open_errormessage("No file suffix provided.",0)
    else:
        open_errormessage("File directory does not exist.",0)

# Check if blinded data already exists
def check_blinded_folder(source_path,files,number_of_files):
    blinded_path = source_path/'blinded'
    if blinded_path.exists():
        file_list = [file for file in blinded_path.glob(f'*{file_suffix.get()}')]
        if len(file_list)>0:
            print('Blinded folder contains blinded data.')
            open_errormessage("The folder contains already blinded data.",1)
        else:
            key_path = blinded_path/'key.csv'
            if key_path.exists():
                open_errormessage("The folder contains a \"key.csv\" file.",1)
            else:
                blind_files(append=False)
    else:
        blind_files(append=False)


def copy_and_rename(source_file,destination_file):
    shutil.copy(source_file,destination_file)

def update_status(message, color="black"):
    status_label.config(text=message, fg=color)
    root.update_idletasks()

def update_counter(count, total):
    counter_label.config(text=f"Processed {count} out of {total} files")
    root.update_idletasks()

def open_errormessage(message,stage):
    errorwindow = tk.Toplevel(root)
    errorwindow.title("Warning!")
    errorwindow.focus()
    errorwindow.grab_set()
    
    if stage==0:
        # A Label widget to show in toplevel
        errorwindow.geometry('250x150+550+300')
        tk.Label(errorwindow,text="Blinding not possible!").grid(row=0,column=0,padx=5, pady=5)
        tk.Label(errorwindow,text=message).grid(row=1,column=0,padx=5, pady=5)
        tk.Label(errorwindow,text="Please fix the error and restart blinding.").grid(row=2,column=0,padx=5, pady=5)
        tk.Button(errorwindow, text="Close", command=errorwindow.destroy).grid(row=3,column=0,padx=5, pady=5)

    elif stage==1:
        errorwindow.geometry('270x180+550+300')
        for i in range(3):  # Assuming there are 3 buttons
            errorwindow.grid_columnconfigure(i, minsize=10, weight=0)
        tk.Label(errorwindow,text="Directory already contains a blinded folder!").grid(row=0,column=0,columnspan=3,padx=5, pady=5)
        tk.Label(errorwindow,text=message).grid(row=1,column=0,columnspan=3,padx=5, pady=5)
        tk.Label(errorwindow,text="Please choose if you want to overwrite the files,\nappend new files or abort blinding.").grid(row=2,column=0,columnspan=3,padx=5, pady=5)
        tk.Button(errorwindow, text="Overwrite", command=lambda: blinding(errorwindow,append=False)).grid(row=3,column=0,padx=5, pady=5,sticky='E')
        tk.Button(errorwindow, text="Append", command=lambda: blinding(errorwindow,append=True)).grid(row=3,column=1,padx=5, pady=5)
        tk.Button(errorwindow, text="Abort", command=errorwindow.destroy).grid(row=3,column=2,padx=5, pady=5,sticky='W')
        tk.Button(errorwindow, text="Close", command=errorwindow.destroy).grid(row=4,column=1,padx=5, pady=5)


def blinding(top_window,append):
    top_window.destroy()
    blind_files(append=append)

def blind_files(append=False):
    source_path = Path(dir_path.get())
    destination_dir = source_path/'blinded'
    if not destination_dir.exists():
        destination_dir.mkdir()
    files = sorted([file for file in source_path.glob(f'*{file_suffix.get()}')])
    number_of_files = len(files)
    index=list(range(number_of_files))
    random.shuffle(index)
    if append:
        no_blinded_files = len([file for file in destination_dir.glob(f'*{file_suffix.get()}')])
    if append:
        file_name_mapping={f'{file.name}':f'{idx+1+no_blinded_files:03d}{file.suffix}' for file,idx in zip(files,index)}
    else:
        file_name_mapping={f'{file.name}':f'{idx+1:03d}{file.suffix}' for file,idx in zip(files,index)}
    if append:
        old_key = pd.read_csv(destination_dir/'key.csv',sep='\t')
        new_key = pd.DataFrame({'OriginalFile':[key for key in file_name_mapping.keys()],
                                'BlindedFile':[value for value in file_name_mapping.values()],
                                'Date':datetime.now().strftime("%Y-%m-%d_%H-%M-%S")})
        pd.concat([old_key,new_key], ignore_index=True).to_csv(destination_dir/'key.csv',index=False,sep='\t')
    else:
        pd.DataFrame({'OriginalFile':[key for key in file_name_mapping.keys()],
                    'BlindedFile':[value for value in file_name_mapping.values()],
                    'Date':datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}).to_csv(destination_dir/'key.csv',index=False,sep='\t')
    
    update_status(message="Processing...",color="orange")
    processed_files = 0
    update_counter(processed_files, number_of_files)
    with ThreadPoolExecutor() as executor:
            futures = [executor.submit(copy_and_rename,
                                    source_path/original_file,
                                    destination_dir/file_copy) for original_file,file_copy in file_name_mapping.items()]
            for future in futures:
                future.result()
                processed_files += 1
                update_counter(processed_files, number_of_files)
    update_status(message="Finished!",color="green")
    

# ### GUI
# ##Setup general window
root = tk.Tk()  # create parent window
root.title('BLINDER - Blinding files for data analysis') # set window title
root.minsize(300,200) # set minimal window size
root.geometry('500x250+550+300') # set window size and position
ttk.Style().theme_use('default') # set window style/theme

# ##Directory entry label
# define entry point for directory path
def open_directory():
    directory=filedialog.askdirectory()
    if directory:
        dir_path.delete(0,tk.END)
        dir_path.insert(0,directory)
# actual label 
tk.Label(root,text='File directory').grid(row=0,column=0,padx=5,pady=5,sticky='E')
dir_path=tk.Entry(root,bd=1,relief=tk.FLAT)
dir_path.grid(row=0,column=1,padx=5, pady=5)
tk.Button(root, text="Browse", command=open_directory,
          relief=tk.RAISED).grid(row=0,column=2,padx=5, pady=5)

# define entry point for file suffix
tk.Label(root,text='File suffix (e.g.: .tif/.lif/.czi/...)').grid(row=1,column=0,padx=5, pady=5,sticky='E')
file_suffix=tk.Entry(root,bd=1,relief=tk.FLAT)
file_suffix.grid(row=1,column=1,padx=5, pady=5)

# define buttom for starting calculation
tk.Button(root,text='Start Blinding Data!',command=blind_data,
          relief=tk.RAISED).grid(row=2,column=1,padx=5, pady=5)

# define status label
status_label = tk.Label(root, text="Wait for action.")
status_label.grid(row=3,column=1,padx=5, pady=5)

# Create a label for file processing counter
counter_label = tk.Label(root, text="Processed 0 out of 0 files")
counter_label.grid(row=4,column=1,padx=5, pady=5)

# define button for ending program
tk.Button(root,text='Close BLINDER.',command=root.quit,
          relief=tk.RAISED).grid(row=5,column=2,padx=5,pady=5)

# ##Button for link to GitHub page
# define the help/about button directing to the BLINDER GitHub page
def open_webpage():
    webbrowser.open("https://github.com/felixS27/BLINDER")
# actual button
tk.Button(root, text="Help/About", command=open_webpage,
          relief=tk.RAISED).grid(row=5,column=0,padx=5,pady=5) 

# define label with my name
tk.Label(root, text="Powered by Felix Schneider",
         font=("Arial", 9, "italic")).grid(row=5,column=1,padx=5,pady=5) 

# add version number
tk.Label(root, text="Version 0.3.0",
         font=("Arial", 9, "italic")).grid(row=6,column=1,padx=5,pady=5) 

root.mainloop()

