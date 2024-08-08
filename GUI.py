import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
import random
import shutil
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from queue import Queue
from threading import Thread

def open_directory():
    directory=filedialog.askdirectory()
    if directory:
        dir_path.delete(0,tk.END)
        dir_path.insert(0,directory)

def copy_and_rename(source_file,destination_file):
     shutil.copy(source_file,destination_file)

def copy_and_rename_with_progress(src, dst, queue):
    copy_and_rename(src, dst)
    queue.put(1)

def update_progress(queue):
    while True:
        progress = queue.get()
        if progress is None:
            break
        progressbar['value'] += progress
        root.update_idletasks()

def blind_data():
    source_path = Path(dir_path.get())
    destination_dir = source_path/'blinded'
    if not destination_dir.exists():
        destination_dir.mkdir()
    files = sorted([file for file in source_path.glob(f'*{file_suffix.get()}')])
    number_of_files = len(files)
    index=list(range(number_of_files))
    random.shuffle(index)
    file_name_mapping={f'{file.name}':f'{idx+1:03d}{file.suffix}' for file,idx in zip(files,index)}
    queue = Queue()
    thread = Thread(target=update_progress,args=(queue,))
    thread.start()
    progressbar['value'] = 0
    progressbar['maximum'] = number_of_files
    with ThreadPoolExecutor() as executor:
            futures = [executor.submit(copy_and_rename_with_progress,
                                    source_path/original_file,
                                    destination_dir/file_copy,
                                    queue) for original_file,file_copy in file_name_mapping.items()]
            for future in futures:
                future.result() 
    queue.put(None) #Stop progress updater
    thread.join()
    pd.DataFrame({'OriginalFile':[key for key in file_name_mapping.keys()],
        'BlindedFile':[value for value in file_name_mapping.values()]}).to_csv(destination_dir/'key.csv',index=False,sep='\t')

root = tk.Tk()  # create parent window
root.title('BLINDER - Blinding files for data analysis') # set window title
root.minsize(500,200) # set minimal window size
root.geometry('500x200+550+300') # set window size and position

# define entry point for directory path
tk.Label(root,text='File directory').grid(row=0,column=0,padx=5,pady=5,sticky='E')
dir_path=tk.Entry(root,bd=1,relief=tk.FLAT)
dir_path.grid(row=0,column=1,padx=5, pady=5)
tk.Button(root, text="Browse", command=open_directory,
          relief=tk.RAISED).grid(row=0,column=2,padx=5, pady=5)

# define entry point for file suffix
tk.Label(root,text='File suffix').grid(row=1,column=0,padx=5, pady=5,sticky='E')
file_suffix=tk.Entry(root,bd=1,relief=tk.FLAT)
file_suffix.grid(row=1,column=1,padx=5, pady=5)

# define buttom for starting calculation
tk.Button(root,text='Start Blinding Data!',command=blind_data,
          relief=tk.RAISED).grid(row=2,column=1,padx=5, pady=5)

#define progressbar
progressbar = ttk.Progressbar(orient=tk.HORIZONTAL,length=200,mode='determinate')
progressbar.grid(row=3,column=0,columnspan=3,padx=5,pady=5)

# define button for ending program
tk.Button(root,text='End blinding.',command=root.quit,
          relief=tk.RAISED).grid(row=4,column=1,padx=5,pady=5) # adjust row according to progress bar

root.mainloop()
