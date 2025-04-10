import subprocess

# Run api.py in a new terminal window
subprocess.run(['start', 'cmd', '/k', 'python api.py'], shell=True)

# Run request.py in a new terminal window
subprocess.run(['start', 'cmd', '/k', 'python request.py'], shell=True) 