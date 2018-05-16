from chalice import Chalice
import boto3
import json

app = Chalice(app_name='nms')
dynamodb = boto3.resource('dynamodb')
nodeTable = dynamodb.Table('node')
projectTable = dynamodb.Table('project')


@app.route('/nodes/{id}')
def getNode(id):
    try:
        response = nodeTable.get_item(Key={'id': id})
    except ClientError as e:
        return {"message" : e.response['Error']['Message']}
    else:
        if 'Item' not in response:
            return {"message" : "The node doesn't exist"}
        else:
            node = response['Item']
            return node

@app.route('/projects/{projName}')
def getProject(projName):
    try:
        response = projectTable.get_item(Key={'projName': projName})
    except ClientError as e:
        return {"message" : e.response['Error']['Message']}
    else:
        if 'Item' not in response:
            return {"message" : "The project doesn't exist"}
        else:
            project = response['Item']
            return project

@app.route('/createNode', methods=['POST'])
def createNode():
    nodeJson = app.current_request.json_body
    if 'id' not in nodeJson or 'location' not in nodeJson or 'shippingStatus' not in nodeJson or 'configStatus' not in nodeJson:
        return {"message" : "Input parameters are missing"}
    item = {
        'id':nodeJson['id'],
        'location':nodeJson['location'],
        'shippingStatus':nodeJson['shippingStatus'],
        'configStatus':nodeJson['configStatus']
    }
    nodeTable.put_item(Item=item)
    return {"message" : "You have created node with id " + nodeJson['id']+ " successfully!"}

@app.route('/updateNode', methods=['POST'])
def updateNode():
    nodeJson = app.current_request.json_body
    if 'id' not in nodeJson or 'location' not in nodeJson or 'shippingStatus' not in nodeJson or 'configStatus' not in nodeJson:
        return {"message" : "Input parameters are missing"}
    key = {'id':nodeJson['id']}
    exp = 'SET #location = :l, #shippingStatus = :ss, #configStatus = :cs'
    names = {'#location':'location', '#shippingStatus':'shippingStatus', '#configStatus':'configStatus'}
    vals = {':l': nodeJson['location'], ':ss': nodeJson['shippingStatus'], ':cs': nodeJson['configStatus']}
    nodeTable.update_item(Key=key,UpdateExpression=exp,ExpressionAttributeNames=names,ExpressionAttributeValues=vals)
    return {"message" : "You have updated node with id " + nodeJson['id']+ " successfully!"}


@app.route('/createProject', methods=['POST'])
def createProject():
    projJson = app.current_request.json_body
    if 'projName' not in projJson or 'customerName' not in projJson or 'startDate' not in projJson or 'endDate' not in projJson:
        return {"message" : "Input parameters are missing"}
    list = []
    item = {
        'projName':projJson['projName'],
        'customerName':projJson['customerName'],
        'startDate':projJson['startDate'],
        'endDate':projJson['endDate'],
        'nodes':list
    }
    projectTable.put_item(Item=item)
    return {"message" : "You have created project with name " + projJson['projName']+ " successfully!"}



@app.route('/updateProject', methods=['POST'])
def updateProject():
    projJson = app.current_request.json_body
    if 'projName' not in projJson or 'customerName' not in projJson or 'startDate' not in projJson or 'endDate' not in projJson:
        return {"message" : "Input parameters are missing"}
    key = {'projName':projJson['projName']}
    exp = 'SET #customerName = :cn, #startDate = :sd, #endDate = :ed'
    names = {'#customerName':'customerName', '#startDate':'startDate', '#endDate':'endDate'}
    vals = {':cn':projJson['customerName'], ':sd':projJson['startDate'], ':ed':projJson['endDate']}
    projectTable.update_item(Key=key,UpdateExpression=exp,ExpressionAttributeNames=names,ExpressionAttributeValues=vals)
    return {"message" : "You have updated project with name " + projJson['projName']+ " successfully!"}


@app.route('/assign', methods=['POST'])
def assign():
    dataJson = app.current_request.json_body
    if 'projName' not in dataJson or 'nodeId' not in dataJson:
        return {"message" : "Input parameters are missing"}
    
    try:
        response = nodeTable.get_item(Key={'id':dataJson['nodeId']})
    except ClientError as e:
        return {"message" : e.response['Error']['Message']}
    else:
        if 'Item' not in response:
            return {"message" : "The node doesn't exist"}
        else:
            node = response['Item']

    try:
        response = projectTable.get_item(Key={'projName':dataJson['projName']})
    except ClientError as e:
        return {"message" : e.response['Error']['Message']}
    else:
        if 'Item' not in response:
            return {"message" : "The project doesn't exist"}
        else:
            project = response['Item']

    nodes = project['nodes']
    if dataJson['nodeId'] in nodes:
        return {"message" : "The node has already been assigned to this project"}

    nodes.append(dataJson['nodeId'])

    key = {'projName':dataJson['projName']}
    exp = 'SET #nodes = :n'
    names = {'#nodes':'nodes'}
    vals = {':n': nodes}
    projectTable.update_item(Key=key,UpdateExpression=exp,ExpressionAttributeNames=names,ExpressionAttributeValues=vals)
    return {"message" : "You have assigned node " + dataJson['nodeId'] + " to project " + dataJson['projName']+ " successfully!" }


@app.route('/unassign', methods=['POST'])
def unassign():
    dataJson = app.current_request.json_body
    if 'projName' not in dataJson or 'nodeId' not in dataJson:
        return {"message" : "Input parameters are missing"}
    
    try:
        response = nodeTable.get_item(Key={'id':dataJson['nodeId']})
    except ClientError as e:
        return {"message" : e.response['Error']['Message']}
    else:
        if 'Item' not in response:
            return {"message" : "The node doesn't exist"}
        else:
            node = response['Item']

    try:
        response = projectTable.get_item(Key={'projName':dataJson['projName']})
    except ClientError as e:
        return {"message" : e.response['Error']['Message']}
    else:
        if 'Item' not in response:
            return {"message" : "The project doesn't exist"}
        else:
            project = response['Item']

    nodes = project['nodes']
    if dataJson['nodeId'] not in nodes:
        return {"message" : "The node has not been assigned to this project"}
    nodes.remove(dataJson['nodeId'])
    
    key = {'projName':dataJson['projName']}
    exp = 'SET #nodes = :n'
    names = {'#nodes':'nodes'}
    vals = {':n':nodes}
    projectTable.update_item(Key=key,UpdateExpression=exp,ExpressionAttributeNames=names,ExpressionAttributeValues=vals)
    return {"message" : "You have unassigned node " + dataJson['nodeId'] + " to project " + dataJson['projName']+ " successfully!" }


