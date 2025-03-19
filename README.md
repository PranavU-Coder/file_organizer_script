# File Organizer PyScript

A py-script created with the intention of transporting files from home or downloads directory to respective directories like .mp3 files getting moved to music folder and .mp4 files to videos folder and so on
the script performs the function automatically when activated in the terminal so the manual labour of draggin and droppin files has been removed with this 

## Why would you want this ?

if lets say tomorrow you are going to download a folder from workspace containin 10,000 files of different extensions for some ai-ml recognition training data-sets , this does the job efficiently and quickly 
alright even for a layman , it is great to optimize your system in such a way that all your files get organized and arranged in a proper manner!

## Performance 

for small files (<20 KB) : 15-20 files per second
for medium files (<10 MB) : 5-10 files per second
and for larger files (>100 MB) : files aren't converted instantly but the transportation is still quick

## What's so good about this ?

- **Real-time monitoring** of specified directories using the watchdog library (necessary for running this program)
- **Automatic organization** of files based on extension type
- **Batch processing** with parallel execution performance
- **Conflict resolution** for duplicate filenames
- **Systemd integration** for easy activation/deactivation
- **Low resource usage** so reduced overhead

## How is it able to achieve this ?

- Uses thread pool for parallel file operations
- Implements optimized direct rename when possible instead of copy+delete (this enables instantaneous transport for small files)
- Processes files in configurable batches for maximum efficiency (I have taken 64 , you are allowed to change this value but I recommend keeping it a power of 2 for benefit of running)
- Smart filesystem detection to use the fastest available move operation

# Installation Guide :-

## Pre-Requisites :
- (1) Linux distribution with systemd (I use Ubuntu 24.04 LTS)
- (2) Python 3.6+

## Step 1 : Install Py-Dependencies

copy all these bash commands into the command 

this creates a virtual environment which is most reccomended for running this script

```bash
python3 -m venv ~/.venv/file-organizer
source ~/.venv/file-organizer/bin/activate
```

installing the watchdog library

```bash
pip install watchdog
```
