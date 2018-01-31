import requests
import json
import os
import sys
import time
from urlparse import urlparse
from string import Template


def login():

    resp = requests.get(base_url+"/api/login?nonce=xyz&state=http%3A%2F%2Fglobal%2Fauthorize", allow_redirects=False)
    url1 = resp.headers.get("Location")

    resp2 = requests.get(url1, allow_redirects=False)
    url2 = resp2.headers.get("Location")

    data = 'userid=admin@example.com&password=password'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    resp3 = requests.post(base_url+url2, data=data, headers=headers, allow_redirects=False)
    url3 = resp3.headers.get("Location")

    resp4 =  requests.get(url3, allow_redirects=False)
    url4 = resp4.headers.get("Location")

    o = urlparse(url4)
    global bearer
    bearer = o.fragment


def addAllNodes():
    headers = {'Authorization': 'Bearer ' + bearer}
    resp = requests.get(base_url+"/api/cluster/nodes", headers=headers)
    nodes = json.loads(resp.content)
    for node in nodes:
        if node['castleStatus'] == "":
            requests.post(base_url+"/api/cluster/nodes/"+node['name'], data=None, headers=headers)
            time.sleep(30)
    return


def createObjectSevice():
    # list all services
    headers = {'Authorization': 'Bearer '+bearer}
    resp = requests.get(base_url+'/api/services', headers=headers)
    services = json.loads(resp.content)
    for service in services :
        if service['serviceType']['code'] == 'object' :
            print 'Object store found'
            return service['id']

    print "create new service"
    objSer = {'available': 0, 'storageMode': 'replication', 'serviceType': {'code': 'object', 'name': 'Object Storage'}, 'used': 0,  'storageProfileType': 'none', 'name': 'Object Storage', 'storageUnitType': 'node', 'storageDesiredUnitCount': 1, 'storageMinUnitCount': 1, 'hasCertificate': False}
    resp = requests.post(base_url+'/api/services', data=json.dumps(objSer), headers=headers)
    new_service =  json.loads(resp.content)
    return new_service['service']['id']


def createObjectUsers(serviceId):
    headers = {'Authorization': 'Bearer ' + bearer}
    resp = requests.get(base_url + '/api/services/'+str(serviceId)+'/users', headers=headers)
    users = json.loads(resp.content)
    user1 = {'displayName': 'bob', 'email': 'bob@user1.com', 'userId': 'user1'}
    user2 = {'displayName': 'jeff', 'email': 'jeff@user2.com', 'userId': 'user2'}
    print "create object store users"
    if len(users) == 0:
        resp1 = requests.post(base_url + '/api/services/'+str(serviceId)+'/users', data=json.dumps(user1), headers=headers)
        resp2 = requests.post(base_url + '/api/services/'+str(serviceId)+'/users', data=json.dumps(user2), headers=headers)
        return json.loads(resp1.content), json.loads(resp2.content)
    elif len(users) == 1:
        resp2 = requests.post(base_url + '/api/services/'+str(serviceId)+'/users', data=json.dumps(user2), headers=headers)
        return users[0], json.loads(resp2.content)
    elif len(users) >= 2:
        return users[0], users[1]


def getServicePort():
    print "Get object store connection info"
    headers = {'Authorization': 'Bearer ' + bearer}
    resp = requests.get(base_url + '/api/objectstoreconnectinfo', headers=headers)
    conn = json.loads(resp.content)
    connInfo = conn['address']
    return connInfo.split(':')


def createS3Config(url,port,user1,user2):
    print "generate s3test.conf file"
    pathname = os.path.dirname(sys.argv[0])
    filein = open(os.path.abspath(pathname)+'/s3testConf.tmpl')
    src = Template(filein.read())
    d={'url': url,'port': port,
       'user1': user1['userId'],'user2': user2['userId'],
       'user1Name': user1['displayName'],'user2Name': user2['displayName'],
       'user1Key': user1['accessKey'], 'user2Key': user2['accessKey'],
       'user1Secret': user1['secretKey'], 'user2Secret': user2['secretKey'],
       'user1Email': user1['email'], 'user2Email': user2['email']}
    result = src.substitute(d)
    file = open('/tmp/s3test.conf','w')
    file.write(result)
    file.close
    return


if len(sys.argv) == 2:
    global base_url
    base_url = 'http://'+sys.argv[1]
else:
    sys.exit("script takes exactly one argument - the castle Host IP")

login()
addAllNodes()
serviceId = createObjectSevice()
user1, user2 = createObjectUsers(serviceId)
url, port = getServicePort()
createS3Config(url, port, user1, user2)
