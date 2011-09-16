import sys
import java
import time

cacheInstanceNames = ["baseCache"]
sleepTime = 5
sType = "APPLICATION_SERVER"
otherAttrList = []
nodeCount = 0
totalCount = 0

def getExceptionText(typ, value, tb):
	value = `value`
	sd = `tb.dumpStack()`
	sd = sd.replace("\\\\","/")
	i = sd.rfind("  File ")
	j = sd.rfind(", line ")
	k = sd.rfind(", in ")
	locn = ""
	if(i>0 and j>0 and k>0):
		file = sd[i+7:j]
		line = sd[j+7:k]
		func = sd[k+4:-3]
		locn = "Function="+func+"  Line="+line+"  File="+file
	return value+" "+locn

def convertToList( inlist ):
	outlist = []
	if (len(inlist) > 0): 
		if (inlist[0] == '[' and inlist[len(inlist) - 1] == ']'): 
			if (inlist[1] == "\"" and inlist[len(inlist)-2] == "\""):
				clist = inlist[1:len(inlist) -1].split(")\" ")
			else:
				clist = inlist[1:len(inlist) - 1].split(" ")
		else:
			clist = inlist.split(java.lang.System.getProperty("line.separator"))

	for elem in clist:
		elem = elem.rstrip();
		if (len(elem) > 0):
			if (elem[0] == "\"" and elem[len(elem) -1] != "\""):
				elem = elem+")\""
			outlist.append(elem)
	return outlist

def listNodes():
	nodes = AdminConfig.list("Node")
	nodeList = convertToList(nodes)
	return nodeList

def listServers(serverType="", nodeName=""):
	optionalParamList = []
	if (len(serverType) > 0):
		optionalParamList = ['-serverType', serverType]
	if (len(nodeName) > 0):
		node = AdminConfig.getid("/Node:" +nodeName+"/")
		optionalParamList = optionalParamList + ['-nodeName', nodeName]
	servers = AdminTask.listServers(optionalParamList)
	servers = convertToList(servers)
	newservers = []
	for aServer in servers:
		sname = aServer[0:aServer.find("(")]
		nname = aServer[aServer.find("nodes/")+6:aServer.find("servers/")-1]
		sid = AdminConfig.getid("/Node:"+nname+"/Server:"+sname)
		if (newservers.count(sid) <= 0):
			newservers.append(sid)
	return newservers

nodeList = listNodes()

for nodeObject in nodeList:

	nodeName = nodeObject.split("(")[0]
	if 1:
		print ""
		print "Processing node: " + nodeName

		try:
			# build list of Application Servers in the Node
			serverList = listServers(sType,nodeName)
		except:
			print "Could not process node. Probably the DMGR? Continuing with the other nodes..."
			continue

		# Update each application server in the node
		for serverObject in serverList:
			serverName = serverObject.split("(")[0]
			print "Contacting server: " + serverName
			for cacheInstance in cacheInstanceNames:
				objectName = "type=DynaCache,node=" + nodeName + ",process=" + serverName + ",*"
				print "  Clearing " + cacheInstance + " on " + objectName + "..."
				doexec = 0
				try:
					nm = AdminControl.completeObjectName(objectName)
					doexec = 1
				except:
					typ, val, tb = sys.exc_info()
					print "  *** ERROR: Cache instance does not exist OR could not contact " + serverName
					print getExceptionText(typ, val, tb)
				if doexec == 1:
					try:
						AdminControl.invoke(nm, "clearCache", cacheInstance)
						print "  clearCache worked"
					except:
						print "  *** ERROR: Cache instance does not exist OR could not contact " + serverName
						typ, val, tb = sys.exc_info()
						print getExceptionText(typ, val, tb)
			print ""
			print "Sleeping..."
			time.sleep(sleepTime)
			print "Came back from sleep"

			nodeCount = nodeCount + 1
			print "  Done with server: "  + serverName + " on node " + nodeName

		totalCount = totalCount + nodeCount

print "Script finished."

#print "Showing files ready to be saved:"   
#print AdminConfig.queryChanges()

#print "Saving configuration..."
#AdminConfig.save()

#print "Syncing all active nodes..."
#AdminNodeManagement.syncActiveNodes()
