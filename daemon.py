import os,sys,time
import subprocess

sleepTime = 86400

def writeLog(logs):
    if not os.path.exists("/var/log/axaf.log"):
        os.system("touch /var/log/axaf.log")
    file = open("/var/log/axaf.log", "w")
    for lines in logs.splitlines():
        file.write(lines + "\n")
    file.close()

while True:
    location = os.path.join("main.py")
    run = subprocess.run(["python3",location],check=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = run.stdout.decode('utf-8')
    writeLog(output)
    print(f"Prefix list updated. Next Sync Time: after {sleepTime} seconds.")
    print("For the log of this update incident, please refer to /var/log/axaf.log.")
    time.sleep(sleepTime)
