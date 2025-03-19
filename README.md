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
- Linux distribution with systemd (I use Ubuntu 24.04 LTS)
- Python 3.6+

## Step 1 : Install Py-Dependencies

copy all these bash commands into the command 

this creates a virtual environment which is most reccomended for running this script

```bash
python3 -m venv .venv
source .venv/bin/activate
```

clone the repository 

```bash
git clone https://github.com/PranavU-Coder/file_organizer_script.git
```

installing the watchdog library

```bash
pip install watchdog
```


## Step 2 : Making Script executable


```bash
chmod +x main.py
```

Edit file paths or add additional file extensions in main.py (go to line 45 of codefile)

## Step 3 : Systemd Service

create this systemd service file (very important for activation)

```bash
mkdir -p ~/.config/systemd/user/
nano ~/.config/systemd/user/file-organizer.service
```

once nano opens , write these lines :
also please note , Replace USERNAME with your actual username

```text
[Unit]
Description=File Organization Service
After=network.target

[Service]
Type=simple

ExecStart=/home/USERNAME/file_organizer_script/.venv/bin/python /home/USERNAME/file_organizer_script/main.py
WorkingDirectory=/home/USERNAME/file_organizer_script
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

save the file and close nano
after which reload systemd to recognize the new service

```bash
systemctl --user daemon-reload
```

## Step 4 : Final footsteps

Create command aliases

paste these lines in `~/.bashrc` :

```text
alias activate-organizer='systemctl --user start file-organizer.service && echo "File organizer activated!"'
alias deactivate-organizer='systemctl --user stop file-organizer.service && echo "File organizer deactivated!"'
```

finally reload the bashrc

```bash
source ~/.bashrc
```

## Test Drive

check if it works by running this command 
```bash
activate-organizer
```

similarly to stop
```bash
deactivate-organizer
```
you can check the status of the programme by 

```bash
systemctl --user status file-organizer.service
```

## Allowing it to run almost always

add this command to terminal , this allows the script to run in background as soon as user logins to computer without having to manually activating the script

```bash
systemctl --user enable file-organizer.service
```


# Final Words

If you found this project worth while or useful please star it , and contribute to src so it can be more efficient 
took me a lot of time to work on this
