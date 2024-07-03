import subprocess
import docker
import datetime
import sys

#Note: this script requires the jq package, e.g. sudo apt install jq

#Connect to local Docker daemon
client = docker.from_env()

#Class for container object to make life easier and because I am used to OOP PowerShell, and because docker-py doesn't expose image digests
class cContainer:
  def __init__(self,id,image,digest,name):
    self.id = id
    self.image = image
    self.digest = digest
    self.name = name


#Enumerate containers
containers = client.containers.list()

#Get image digests for the containers
containerList = []
for i in containers:
  #Get the image SHA256 digest manually since it's not exposed via the docker-py SDK
  digestCommand = "docker inspect " + i.id + " | jq \".[].Image\""
  digest = subprocess.run(digestCommand, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
  #Add container object with info from docker-py and docker CLI to custom class
  containerList.append(cContainer(id=i.id,name=i.name,digest=digest,image=i.image))

arg1 = sys.argv[1]
if arg1 == 'log':
  file = open("update.log","w")
  str_timestamp = str(datetime.datetime.now())
  file.write("Running containers and their digests (versions) as of ")
  file.write(str_timestamp)
  file.write("\nName Id ImageDigest\n")

  for i in containerList:
    message = i.name + " " + i.id[0:12] + " " + i.digest[8:20] + "\n"

    file.write(message)
    
  file.close

elif arg1 == 'list':
  print(("Name Id ImageDigest"))
  for i in containerList:
    message = i.name + " " + i.id[0:12] + " " + i.digest[8:20]
    print(message)





# docker images --format '{{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Digest}}'
