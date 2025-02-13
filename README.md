# BrowserHistoryGrab
Browser History Grabber scripts for the main browsers on Win, Mac, Linux
Browser History CANNOT be grabbed if the browser is running. Run the script/executable with the -kill switch to kill the browsers. 
WARNING: There is no warning - it will kill all processes assocaited with the browser. You WILL lose work. 

run the scripts with: python BrowserHistoryGrab.py -kill (if required) 

Portable executables have been created with pyinstaller. 
pyinstaller --onefile BrowserHistoryGrab.py 

(need to run it on the OS type you want the executable for. Build you own for linux flavour - I've build Windows and MacOS for you - but validate the python code first, then build your own executable. It's like a condom for your pc... I'm a random bloke on the internet, you should not trust my code. 




