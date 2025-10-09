import os,time
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
    run = subprocess.run(os.path.join("main.py"),check=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = run.stdout.decode('utf-8')
    writeLog(output)
    print("Prefix list updated.")
    time.sleep(sleepTime)
