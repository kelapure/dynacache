# This program may be used, executed, copied, modified and distributed
# without royalty for the purpose of developing, using, marketing, or distribution

# *******************************************************************************************************************
# File modification history:
# Rohit Kelapure			-- original author
# Bertrand Fayn 30/11/2006 - output format changed to CSV
# Hendrik van Run 24/03/2009 - changed default CSV separator to "," and added support for multiple cache instances
# Deb Banerjee Aug 01, 2012 -- WXS cache treatment, enhancememt, bug fixes, and extensive simplification
# Deb Banerjee Sept, 2012 --   filter introduction, futher enhanecment and consumability improvements
# Deb Banerjee Oct, 2012  --   bug fix, generalization, and simplification
# *******************************************************************************************************************

#----------------------------------------------------------------------------------
# DynaCacheStatistics.py - JYTHON implementation of WXS DynaCache statistics collector
#----------------------------------------------------------------------------------
#
# The purpose of this script is to generate a file of statistics for
# the DynaCache base cache and/or cache instances. The resulting file
# can be parsed using the Java CacheStatisticsParser class. The output
# of that can be viewed, modified and/or graphed using spreadsheet programs.
#
# This script can be included in the wsadmin command invocation like this:
#
# wsadmin -lang jython -f DynaCacheStatics.py serverX file.txt
#
# The script has two required parameters:
# arg1 - serverName
# arg2 - fileName
#
# The script accepts several optional parameters:
# -nodeName - The name of the server node. This parameter is required only if the server name is not unique in the cell.
# -cacheInstance - The JNDI name of the cache instance for which statistics will be
# collected. If not specified, statistics will be collected for the
# base cache only. Name "*" indicates all cache instances.
# Not supported for versions 5.0.2 and earlier.
# -sleepUnit - The unit for sleep intervals. Possible values: hours, minutes or seconds. Default is seconds.
# -sleepInterval - The number of sleep units between polls. Default is 10.
# -fileAppend - If specified, statistics are appended to the file, if it already exists. Otherwise, the file is recreated.
# -csvSeparator - The character used for the CSV field separator. Default is ",".
# -cacheType - An optional filter on caches. A single character should be specified as its value. A value of w or W or m or M
# specifies WXS DynaCache, whereas a value of t or T specified traditional Dynacache. By default there cache filtering is
# turned off. The filter can be conveniently used with the 'cacheInstance' parameter. A parameter combination 
# "-cacheInstance * -cacheType w" will collect statistics for all the configured WXS DynaCache instances in the environment   
#
# Examples:
# DynaCacheStatistics server1 abc.txt "-sleepInterval 15 -fileAppend"
# DynaCacheStatistics server1 xyz.txt "-sleepUnit hours -sleepInterval 1"
#
# NOTES: 
# 1. The script is popularly used as a flight recorder in WebSphere Commerce Environment using DynaCache, especially in the 
# commerce installations using WXS DynaCache. For WXS DynaCache, presently this Client-Side Flight Recorder (CFR) outputs the 
# following MBean statistics in the order as shown here.
# CacheHits CacheMisses CacheLruRemoves CacheRemoves ExplicitInvalidationsFromMemory MemoryCacheEntries MemoryCacheSizeInMB 
# TimeoutInvalidationsFromMemory com.ibm.websphere.xs.dynacache.remote_hits com.ibm.websphere.xs.dynacache.remote_misses
# Refer to WAS and WXS info centers for detailed specification of these counters. 
#
# It should be noted the first two counters (CacheHits, and CacheMisses) are application server (WAS instance) scoped, while 
# the rest are of global scoped, conforming to the cohernet cache principle of WXS. 
#
# If the flight recorder collects the value of the counters in two different active cluster members of the same cluster at the 
# same time, the value of the last eight counters in the list (CacheLruRemoves, ..., com.ibm.websphere.xs.dynacache.remote_misses)
# should be identical. If all the WAS-WCS cluster members recevive similar amount of traffic, which is usually the case, the values
# of the first two counters (CacheHits, and CacheMisses) should also roughly be the same at the same time accross all cluster members.
#
# 2. In a WAS client environment, this script can be conveniently copied in the deployment manager machine in a directory of choice. A simple
# command line can invoke wsadmin passing the flight recorder scriot file and targeting an application server instance. Refer to example
# flightrecorder invocations in this prologue.  
#
# 3. For a production WAS-WCS cell, where all the cluster members receive similar amount of traffic it is STRONLGY RECOMMENDED to execute 
# this script by targeting only one representative cluster member using a relatively longer invocation period -- say every 30 minutes or 
# even an hour or so.
#
# 4. The optional parameters to the client-side flight recorder sript can be provided in any order.
#
#
# Examples of invocations in WAS:
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py server1 MyDynaCacheStatistics.txt
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py server1 MyDynaCacheStatistics.txt “-sleepUnit minutes -sleepInterval 30" 
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py myServer MyDynaCacheStatistics.txt “-nodeName myNode -sleepUnit minutes -sleepInterval 30" 
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py server1 MyDynaCacheStatistics.txt “-cacheInstance baseCache”
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py cluster_member1 MyDynaCacheStatistics.txt “-cacheInstance *”
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py server1 MyDynaCacheStatistics.txt “-cacheInstance baseCache –sleepUnit seconds -sleepInterval 30”
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py server1 MyDynaCacheStatistics.txt “-cacheInstance * -sleepUnit minutes -sleepInterval 15”
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py WCS-Member1 MyDynaCacheStatistics.txt “-sleepUnit minutes -sleepInterval 30 -cacheInstance * -cacheType w”
# ./wsadmin.sh -lang jython -f DynaCacheStatisticsCSV.py server1 MyDynaCacheStatistics.txt “-sleepUnit minutes -sleepInterval 30 -cacheInstance * -cacheType t”
#----------------------------------------------------------------------------------

import java
import sys

from jarray import array
from java.lang import String
from java.lang import Object
from jarray import array

linesep = java.lang.System.getProperty('line.separator')

#----------------------------------------------------------------------------------
# checks whether it a traditional or modern (wxs) DynaCache implementation
#-----------------------------------------------------------------------------------
def isModernDynaCache(mbean, cacheInstance):
	modernMarker = "com.ibm.websphere.xs.dynacache.remote_hits"
	statNames = AdminControl.invoke(mbean, 'getCacheStatisticNames', cacheInstance).split(linesep)
	if (modernMarker in statNames):
		return 1
	else:
		return 0


def DynaCacheStatistics (args):
	#------------------------------------------------------
	# get arguments and perform argument validation
	#------------------------------------------------------
                      
        global AdminConfig
        global AdminControl
        
        numArgs = len(args)

        if (numArgs < 2):
                print "\nError: Required arguments serverName and fileName not supplied."
                usage()
                return
        #endIf
        if (numArgs > 3):
                print "\nError: More than three arguments supplied. The number of arguments: " + str(numArgs) + ".\n"
                usage()
                return
        #endIf

        #------------------------------------------------------
        # set default values
        #------------------------------------------------------
        serverName = args[0]
        version = ""
        majorVersion = ""
        minorVersion = ""
        fileName = args[1]
        nodeName = ""
        nodeSpecification = ""
        instanceName = ""
        sleepUnit = "seconds"
        sleepInterval = 15  
        fileAppend = "false"
        fileAccess = "w+"
        csvSeparator = ","
        cacheInstanceSupported = "true"
        onlyModernDynaCache = 0 
        onlyTraditionalDynaCache = 0
	cacheInstanceCtr = 0

         
        #------------------------------------------------------
        # validate serverName
        #------------------------------------------------------
        serversFound = 0
        servers = AdminConfig.list("Server").split(linesep)
        for server in servers:
                sname = AdminConfig.showAttribute(server, "name")
                if (sname == serverName):
                        serversFound = serversFound + 1
                #endIf
        #endFor
        if (serversFound == 0):
                print "\nError: Unrecognized server \"" + serverName + "\" specified."
                return
        #endIf
        
        #------------------------------------------------------
        # iterate through optional arguments
        #------------------------------------------------------
        if (len(args) == 3):
            arguments = args[2].split(" ")
        else:
            arguments = []
        #endElse

        print arguments

        numArgs = len(arguments)
        index = 0 #forStart
        while (index < numArgs): #forTest

                token = arguments[index]
                if (token.find("-") != 0):
                        print "\nError: Unrecognized argument \"" + token + "\"."
                        usage()
                        return
                #endIf

                #------------------------------------------------------
                # validate nodeName
                #------------------------------------------------------
                if (token == "-nodeName"):
                        nodeFound = 0
                        index += 1
                        nodeName = arguments[index]
                        nodes = AdminConfig.list("Node").split(linesep)
                        for node in nodes:
                                nname = AdminConfig.showAttribute(node, "name")
                                if (nname == nodeName):
                                        nodeFound = 1
                                        continue
                                #endIf
                        #endFor
                        if (nodeFound == 1):
                                nodeSpecification = ",node=" + nodeName
                                index += 1
                                continue
                        #endIf
                        print "\nError: Unrecognized node \"" + nodeName + "\" specified for -nodeName argument."
                        return
                #endIf

                #------------------------------------------------------
                # validate cacheInstance
                #------------------------------------------------------
                if (token == "-cacheInstance"):
                    index += 1
                    if (cacheInstanceSupported == "false"):
                        print "\nError: -cacheInstance argument supported for versions 5.1 and newer only."
                        return
                    #endIf
                    instanceName = arguments[index]
                    index += 1
                    continue
                #endIf

                #------------------------------------------------------
                # validate sleepUnit
                #------------------------------------------------------
                if (token == "-sleepUnit"):
                        index += 1
                        sleepUnit = arguments[index]
                        if (sleepUnit != "hours" and sleepUnit != "minutes" and sleepUnit != "seconds"):
                                print "\nError: Invalid value \"" + sleepUnit + "\" specified for -sleepUnit argument."
                                print " Value must be hours, minutes or seconds."
                                return
                        #endIf
                        index += 1
                        continue
                #endIf

                #------------------------------------------------------
                # validate sleepInterval
                #------------------------------------------------------
                if (token == "-sleepInterval"):
                        index += 1
                        sleepInterval = arguments[index]
                        try:
                            sleepInterval = int(sleepInterval)
                        #endTry
                        except:
                            print "\nError: Non-integer value \"" + sleepInterval + "\" specified for -sleepInterval argument."
                            print " Value must be between 1 and 32767."
                            return
                        #endExcept
                        
                        if (sleepInterval < 1 or sleepInterval > 32767):
                            print "\nError: Invalid value \"" + `sleepInterval` + "\" specified for -sleepInterval argument."
                            print " Value must be between 1 and 32767."
                            return
                        #endIf
                        index += 1
                        continue
                #endIf

                #------------------------------------------------------
                # set fileAppend
                #------------------------------------------------------
                if (token == "-fileAppend"):
                        fileAppend = "true"
                        fileAccess = "a"
                        index += 1
                        continue
                #endIf

                #------------------------------------------------------
                # set csvSeparator
                #------------------------------------------------------
                if (token == "-csvSeparator"):
                        index += 1
                        csvSeparator = arguments[index]
                        if (len(csvSeparator) != 1):
                            print "\nError: Invalid value \"" + `csvSeparator` + "\" specified for -separator argument."
                            print " Value must be one character."
                            return
                        #endIf
                        index += 1
                        continue
                #endIf


		#------------------------------------------------------
                # validate desired cache type
                #------------------------------------------------------
                if (token == "-cacheType"):
                        index += 1
                        cacheType = arguments[index]
                        
                        if (len(csvSeparator) != 1):
                            print "\nError: Invalid value \"" + `cacheType` + "\" specified for -cacheType argument."
                            print " Value must be one character -- w (m) (or W (M)), or t (or T)."
                            return
                        #endIf
                        
                        # any one character value is accepted 
                        if ((cacheType == 'w') or (cacheType == 'W') or (cacheType == 'm') or (cacheType == 'M')):
                        	onlyModernDynaCache = 1
                    	elif ((cacheType == 't') or (cacheType == 'T')):
                    		onlyTraditionalDynaCache = 1 
                        #endIf
                        index += 1
                        continue
                #endIf
                
                #------------------------------------------------------
                # exit if other (unknown) arguments specified
                #------------------------------------------------------
                print "\nError: unrecognized argument \"" + token + "\"."
                usage()
                return
                index += 1 #forNext
        #endWhile

        #------------------------------------------------------
        # exit if multiple servers found and node not specified
        #------------------------------------------------------
        if (serversFound > 1 and nodeName == ""):
                print "\nError: Multiple servers named \"" + serverName + "\" exist. Argument -nodeName required."
                return
        #endIf

        #------------------------------------------------------
        # exit if server not started
        #------------------------------------------------------
        serverON = AdminControl.completeObjectName("type=Server,name=" + serverName + nodeSpecification + ",*")
        if (serverON == ""):
                print "\nError: Server \"" + serverName + "\" not started."
                return
        #endIf

        #------------------------------------------------------
        # calculate sleepMilliseconds
        #------------------------------------------------------
        if (sleepUnit == "hours"):
                sleepMilliseconds = (sleepInterval * 3600000)
        else:
                if (sleepUnit == "minutes"):
                        sleepMilliseconds = (sleepInterval * 60000)
                else:
                        if (sleepUnit == "seconds"):
                                sleepMilliseconds = (sleepInterval * 1000)
                        #endIf
                #endElse
        #endElse

        # print "\n DEBUG INFO:"
        # print " serverName= " + serverName
        # print " version=" + version
        # print " majorVersion=" + majorVersion
        # print " minorVersion=" + minorVersion
        # print " fileName= " + fileName
        # print " nodeName= " + nodeName
        # print " instanceName= " + instanceName
        # print " onlyModernDynaCache= " + str(onlyModernDynaCache)
        # print " onlyTraditionaDynaCache= " + str(onlyTraditionalDynaCache)
        # print " sleepUnit= " + sleepUnit
        # print " sleepInterval= " + `sleepInterval`
        # print " sleepMilliseconds= " + `sleepMilliseconds`
        # print " fileAppend= " + fileAppend
        
        #----------------------------------------------------------
        # locate the Dynacache MBean
        #----------------------------------------------------------
        queryString = "type=DynaCache,process=" + serverName + nodeSpecification + ",*"
        mbean = AdminControl.queryNames(queryString)


	# Following are the variables needed for invoking the getCacheStatistics() method of the DynaCache MBean. The invocation of 
	# the getCacheStatistics() method needs the names of the desired statistics counters. The names are passed in the 'instances' 
	# jython list. The names are passed so that the values of the corresponding counters from the call get returned in the same 
	# order. Note the first two variables are WAS instance (JVM) scoped while the rest are global cache scoped. This is not the 
	# default order in which statistcs gets returned from the getAllCacheStatistics() invocation.  
	#
	# The present approach of not invoking the getAllCacheStatistics() method is sound. There is no gurantee that the statistics 
	# counters will always be returned in a specific order by the getAllCacheStatistics() invocation, so that one can manipulate 
	# the returned list to the desired order -- first JVM-scoapd followed by gloablly scoped entities.  
	#
	# All these variables will be used later during actual MBean method invocation 
        mbeanForjmx = AdminControl.makeObjectName(mbean)
        instances = ["CacheHits", "CacheMisses", "CacheLruRemoves", "CacheRemoves", "ExplicitInvalidationsFromMemory", "MemoryCacheEntries", "MemoryCacheSizeInMB", 
        "TimeoutInvalidationsFromMemory", "com.ibm.websphere.xs.dynacache.remote_hits", "com.ibm.websphere.xs.dynacache.remote_misses"]
        instancesArray = array(instances, java.lang.String)
        # the signature of the parameter that will be passed to the mbean getCacheStatistics() method
        signature = array(["java.lang.String", "[Ljava.lang.String;"], String)
   
             
        #----------------------------------------------------------
        # validate instanceName and fill up the cache instances (names)
        #----------------------------------------------------------
        cacheInstances = []
        
        if (instanceName == "*"):
            cacheInstances = AdminControl.invoke(mbean, "getCacheInstanceNames").split(linesep)
        else:
            if (instanceName != ""):
                instances = AdminControl.invoke(mbean, "getCacheInstanceNames").split(linesep)
                for instance in instances:
                    if (instance == instanceName):
                        cacheInstances = [instance]
                        print "instance: " + instance

        if (cacheInstances == []):
            # will use baseCache 
            cacheInstances.append("baseCache")	
 
        numOfCacheInstances = len(cacheInstances)
      
 	# ---------------------------------------------------------------------------------------------
        # in the endless loop we create three lists with positional significance as indicated below
        # while traversing the list of cache instaces for the very fist time.
        # cacheInstances -- contains the individual cache instancs. Number of elements >= 1
        # cacheTypes -- corersponding DynaCache type. 1 implies modern WXS and 0 implies traditional
        # skipCache -- whether the user is not interested in this cache type. Value is set from the passed filter '-cacheType'
        # printHeaders -- whether the header corersponding to this cache instance needs to be outputted
        # headers -- the actual csv header for this cache instance 
        # -----------------------------------------------------------------------------------------------       
      	cacheTypes = []
      	skipCache = []
      	printHeaders = []
      	headers = []
        
        # ----------------------------------------------------------------------------------------------
        # some bookkeeping variables to set the correct values in the three lists: 
        # cacheTypes, printHeaders, and headers 
        # ----------------------------------------------------------------------------------------------- 
        prevCacheType = 0
        numOfEffectiveCacheInstances = 0
        firstCacheListTraversal = 1
        firstEffectiveCacheIndx = -1

        # ----------------------------------------------------------------------------------------------
        # controls file opening mode -- append or new 
        # the file is closed on every iteration of while loop
        # ----------------------------------------------------------------------------------------------
        firstLoopIteration = 1
        
        #-----------------------------------------------------------------------------------------------------------------
        # endless loop: open file, process cache (write stats if necesaery), close file, sleep, wake up, ... ad infinitum
        #-----------------------------------------------------------------------------------------------------------------              

        while (0 == 0):
        	
        	#----------------------------------------------------------
                # open file, for the second and subsequent iterations append 
                # contents to the existing file  
                #----------------------------------------------------------
                if (firstLoopIteration == 0):
                	fileAccess = "a"
                	
                try:
                	fileId = open(fileName, fileAccess)
                except:
                    	print "\nError: Failed to open the file: " + fileName + ". Exiting." 
                    	return
                #endTry
                
                #----------------------------------------------------------
                # get the currnt time 
                #----------------------------------------------------------
                from time import localtime, strftime

                timeStamp = localtime()
                dateVal = strftime("%m/%d/%Y", timeStamp);
                timeVal = strftime("%H:%M:%S", timeStamp);
		timeStampVal = dateVal + " " + timeVal

                cacheInstanceCtr = 0
                                
                for cacheInstance in cacheInstances:              	
               	
                	# initialize the buffers for each cache instance
                	contents = ""
                        values = cacheInstance + csvSeparator + timeStampVal + csvSeparator + dateVal + csvSeparator + timeVal    
                                          
                        # test whether the cache instance is of WXS variety and store the result in the cacheTypes list.
                        # also make sure whether user is intersted in this category of cache
                        # note the tests are done only once for a specific cache, not everytime the loop executes for the same cache
                        if (firstCacheListTraversal == 1):  
                        	# initialize the skip variable to false
                		toSkip = 0;                     	
                        	
                        	isModern = isModernDynaCache(mbean, cacheInstance)
                        	cacheTypes.append(isModern)
                        	
                        	# check whether the user is interested in the cache type
                		if (onlyModernDynaCache == 1):
                			if (isModern != 1):
                				toSkip = 1
                		elif (onlyTraditionalDynaCache == 1):
                			if (isModern == 1):
                				toSkip = 1 
                		
                		# skip procressing
                		if (toSkip == 1):
                			# fill up relevant control arrays with values and also advance the 
                			# cache counter
                			skipCache.append(1)
                			printHeaders.append(0)
                			headers.append("")
                			# bump up the counter for continuing to the next element of the cacheinstances list
                			cacheInstanceCtr += 1
                			continue
                 		
                		# control arrived here. We need to do regular processing of the cacheInstance -- be it modern or traditional.
                		skipCache.append(0)
                		numOfEffectiveCacheInstances += 1
                		
                		# if not already set, set the index of the first cache to be considered among the cacheInstances list.  
                		if (firstEffectiveCacheIndx == -1):
                			firstEffectiveCacheIndx = cacheInstanceCtr
                		
                		# set the value of the last index too which may continue to get upgraded if more caches in the 
                		# cacheInstances list are not to be skipped but processed.   	
                		lastEffectiveCacheIndx = cacheInstanceCtr
                			                        	
                        	# to prevent printing of the name (header) information for consecutive cache instances of 
                        	# identical type -- modern or traditional                        
                        	presentCacheType = isModern                   		
                                
                        	if (numOfEffectiveCacheInstances == 1):
                       			printNames = 1
                        	else:
                        		if (prevCacheType == presentCacheType):
                        			printNames = 0
                        		else:
                        			printNames = 1

                        	printHeaders.append(printNames)
                        	
                        	prevCacheType = presentCacheType
                        else:
                        	# prevent the printing of header if the last to-be processed element of the cacheInstances
                        	# list is of the same type as that of the first to-be processed element of the cacheInstances.  
 
                   		# turn off the printHeader flag, if the above mentioned cache types are identical
               			                       	
                       		if (cacheTypes[firstEffectiveCacheIndx] == cacheTypes[lastEffectiveCacheIndx]):
                       			printHeaders[firstEffectiveCacheIndx] = 0
                                     	 	
                       	# -----------------------------------------------------------
                       	# invoke MBean if the cache instance is not to be skipped
                       	# -----------------------------------------------------------
                       	if (skipCache[cacheInstanceCtr] == 1):
                       		# we have to check the next cache instance, bunmp up the counter
                       		cacheInstanceCtr +=1 
                       		continue
                       	                       	 	
                        # -----------------------------------------------------------------------------------------------------------
                        # Actual MBean invocation. Note that different MBean methods are invoked based on the type of the cache. 
                        # This is done for easier interpretation of the generated CSV file. 
                        # As discussed earlier, for modern (WXS) DynaCache, we would like to have the two application server-scoped 
                        # statistics as the first two elements in the CSB file. This is not the default order in which stats gets 
                        # returned from the getAllCacheStatistics() invocation.
                        # -----------------------------------------------------------------------------------------------------------
                        if (cacheTypes[cacheInstanceCtr] == 1):
                               	params = array([cacheInstance, instancesArray], Object) 
                               	result = AdminControl.invoke_jmx(mbeanForjmx, 'getCacheStatistics', params, signature) 
                               	                               	
                               	# parse the returned 'result' of type org.python.core.PyArray and place it in a jython list 
                               	# for further processing
                               	stats = []
                               	for elem in result:
                               		stats.append(elem)
                        else:
                   		stats = AdminControl.invoke(mbean, 'getAllCacheStatistics', cacheInstance).split(linesep)	
                   		
                        if (firstCacheListTraversal == 1):
                        	# initialise names buffer
                        	names = "CacheInstanceName" + csvSeparator + "TimeStamp" + csvSeparator + "Date" + csvSeparator + "Time"  	
                        		
                        # collect the returned name value pairs into formatted contents to be written as a line 
                        for stat in stats:
                        	nameValuePair = stat.split('=')
                        	if (printHeaders[cacheInstanceCtr] == 1):
                        		if (firstCacheListTraversal == 1):
                        			names = names + csvSeparator + nameValuePair[0]
                        			
                       		values = values + csvSeparator + nameValuePair[1]
                   	#endFor  
                   	
                   	if (firstCacheListTraversal == 1):
                   		headers.append(names)
                   	                   	
                   	if (printHeaders[cacheInstanceCtr] == 1):
               			contents = headers[cacheInstanceCtr] + "\n"
                        
                        contents = contents + values + "\n"
                        
                        #----------------------------------------------------------
                	# write to the file
                	#----------------------------------------------------------                   		
                	try:
                     		fileId.write(contents);
                	except:
                    		print "\nError: Failed to write to the file: " + fileName + ". Exiting."
                    		return
	              	#endTry                      
                        
                        cacheInstanceCtr += 1;  
                        # endFor over all the cache instances
                      		 

                # we have traversed all the cache instances and have filled up appropriate values in the bookkeeping arrays
                firstCacheListTraversal = 0;


                #----------------------------------------------------------
                # close file
                #----------------------------------------------------------
                fileId.close()


		#-----------------------------------------------------------
		# if there are no cache instances to be processed, simply exit
		# it does not make any sense then to continue the loop
		#-----------------------------------------------------------
		if (numOfEffectiveCacheInstances == 0):
			print "\nError: User selected parameters have resulted in empty cache instance set. Exiting."
			return
		#endif	 

		firstLoopIteration = 0;
                #----------------------------------------------------------
                # sleep
                #----------------------------------------------------------
                java.lang.Thread.sleep(sleepMilliseconds)

        #endWhile - the endless loop

        return
        
#endDef
           
def usage ():
        print "\n DynaCacheStatistics"
        print "\n Description: Polls cache statistics."
        print "\n DynaCacheStatistics serverName fileName \"\[-nodeName name\]"
        print " \[-sleepUnit unit\] \[-sleepInterval interval\]"
        print " \[-cacheInstance \{name|*\}\] \[-fileAppend\]\""
        print " \[-csvSeparator character\]"
        print "\n Arguments:"
        print " *serverName - The name of the server for which statistics are collected."
        print " *fileName - The name of the file where statistics will be stored."
        print " nodeName - The name of the server node. This parameter is required only"
        print " if the server name is not unique in the cell."
        print " cacheInstance - The JNDI name of the cache instance for which statistics will be"
        print " collected. If not specified, statistics will be collected for"
        print " the base cache only. Name \"*\" indicates all cache instances."
        print " Not supported for versions 5.0.2 and earlier."
        print " sleepUnit - The unit for sleep intervals. Possible values: hours,"
        print " minutes or seconds. Default is seconds."
        print " sleepInterval - The number of sleep units between polls. Default is 10."
        print " fileAppend - If specified, statistics are appended to the file, if it"
        print " already exists. Otherwise, the file is recreated."
        print " csvSeparator - The character used for the CSV field separator. Default is \",\""
        print " One can specify filters by using \"-cacheType\" parameter. w|W|m|M indicates"
        print " modern (WXS) dynacache, whereas t|T stands for the traditional variety."
        print " cacheType - filter. An argument like \"-cacheInstance * -cacheType m\" will"
        print " collect the statistics for all the modern (WXS) dynacache instances present"
        print " in the application server under concern. By default the filtering is turned off." 
        print "\n A Few Examples:"
        print "\n DynaCacheStatistics server1 abc.txt \"-sleepInterval 15 -fileAppend\""
        print "\n DynaCacheStatistics server1 abc.txt \"-sleepUnit minutes -sleepInterval 30\""
        print "\n DynaCacheStatistics server1 abc.txt \"-nodeName myNode -sleepUnit minutes -sleepInterval 30\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-sleepUnit hours -sleepInterval 1\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-cacheInstance *\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-cacheInstance * -cacheType m\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-cacheInstance * -cacheType t\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-sleepUnit minutes -sleepInterval 30 -cacheInstance * -cacheType w\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-cacheInstance inst1\""
#endDef
       
#-----------------------------------------------------------------
# Main - DynaCacheStatistics.py
#-----------------------------------------------------------------
DynaCacheStatistics(sys.argv)