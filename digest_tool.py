import subprocess
import docker
import datetime
import sys
import re

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

class cImage:
  def __init__(self,imageId,digest,repository):
    self.imageId = imageId
    self.digest = digest
    self.repository = repository


#Get image digests for the containers
def listContainers():
  containers = client.containers.list()
  containerList = []
  for i in containers:
    #Get the image SHA256 digest manually since it's not exposed via the docker-py SDK
    digestCommand = "docker inspect " + i.id + " | jq \".[].Image\""
    digest = subprocess.run(digestCommand, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
    #Add container object with info from docker-py and docker CLI to custom class
    containerList.append(cContainer(id=i.id[0:12],name=i.name,digest=digest[8:20],image=i.image))
  return containerList

def listImages():
  imageList = []
  imagesCommand = "docker images --digests"
  images = subprocess.run(imagesCommand, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
  parsedImages = images.split('\n')
  cleaned = [i for i in parsedImages if i != '']
  for i in cleaned:
    row = re.split(r'\s{2,}',i)
    image = cImage(imageId = row[3],digest = row[2],repository = row[0])
    imageList.append(image)
  return imageList


#Get arguments used to invoke the script
arg1 = sys.argv[1]
try:
  arg2 = sys.argv[2]
except:
  arg2 = "containerDigests.log"

if arg1 == 'log':
  filename = arg2
  file = open(filename,"w")
  str_timestamp = str(datetime.datetime.now())
  file.write("Running containers and their digests (versions) as of ")
  file.write(str_timestamp)
  file.write("\nName ContainerId ImageDigest\n")

  containers = listContainers()
  images = listImages()
  
  for c in containers:
    for i in images:
      if i.imageId == c.digest:
        message = c.name + " " + c.id + " " + i.digest + '\n'
    file.write(message)
    
  file.close

elif arg1 == 'list':
  print(("Name ContainerId ImageDigest"))
  
  containers = listContainers()
  images = listImages()
  
  for c in containers:
    for i in images:
      if i.imageId == c.digest:
        message = c.name + "\t" + c.id + "\t" + i.digest
        print(message)

elif arg1 == 'find':
  containerId = arg2
  print(("Name\tContainerId\tImageDigest"))
  
  containers = listContainers()
  images = listImages()
  
  for c in containers:
    if c.id == containerId:
      for i in images:
        if i.imageId == c.digest:
          message = c.name + "\t" + c.id + "\t" + i.digest
          print(message)

elif arg1 == 'help':
  helpMessage = '''
  This tool lists running containers and their current image digest.
  
  Usage: python3 digest_tool.py [OPTION] [FILENAME]

  Options:
          list        outputs running container names, ids, and SHA256 digests to pipeline. Used for CLI/shell scripts.
          log         logs same output as the 'list' option to a file. If no filename is given, will output to a timestamped log file.

  Examples: 
            python3 digest_tool.py list
            python3 digest_tool.py log


  '''
  print(helpMessage)
