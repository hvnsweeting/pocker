### Ideally this would replace the bash download script
"""
# https://index.docker.io/api/content/v1/products/images/alpine
import urllib.request
r = urllib.request.Request("https://index.docker.io/v1/repositories/library/hello-world/images", headers={"X-Docker-Token": True})
resp = urllib.request.urlopen(r)
headers = resp.headers
docker_endpoint = headers['X-Docker-Endpoints']
docker_token = headers['X-Docker-Token']
print(docker_endpoint, docker_token)

#  signature=89e1b394a35b15643cd98797cda2353a5f125c42,repository="library/hello-world",access=read
#image = docker_token.split(",")[1].split('=')[1]
image = "library/hello-world"
tag = 'latest'
r = urllib.request.Request(f"https://{docker_endpoint}/v2/{image}/tags/{tag}", headers={"Authorization": f"Token {docker_token}"})
resp = urllib.request.urlopen(r).read()
print(resp)

"""

