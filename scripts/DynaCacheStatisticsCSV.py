# This program may be used, executed, copied, modified and distributed
# without royalty for the purpose of developing, using, marketing, or distribution

# File modification history:
# Bertrand Fayn 30/11/2006 - output format changed to CSV
# Hendrik van Run 24/03/2009 - changed default CSV separator to "," and added support for multiple cache instances

#----------------------------------------------------------------------------------
# DynaCacheStatistics.py - JYTHON implementation of DynaCache statistics collector
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
#
# Examples:
# DynaCacheStatistics server1 abc.txt "-sleepInterval 15 -fileAppend"
# DynaCacheStatistics server1 xyz.txt "-sleepUnit hours -sleepInterval 1"
#
#----------------------------------------------------------------------------------
import java
import sys

linesep = java.lang.System.getProperty('line.separator')

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
                print "\nError: Extra argument \"[lindex " + args + " 3]\" supplied."
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

        print "\n DEBUG INFO:"
        print " serverName= " + serverName
        print " version=" + version
        print " majorVersion=" + majorVersion
        print " minorVersion=" + minorVersion
        print " fileName= " + fileName
        print " nodeName= " + nodeName
        print " instanceName= " + instanceName
        print " sleepUnit= " + sleepUnit
        print " sleepInterval= " + `sleepInterval`
        print " sleepMilliseconds= " + `sleepMilliseconds`
        print " fileAppend= " + fileAppend
        
        #----------------------------------------------------------
        # find Dynacache MBean
        #----------------------------------------------------------
        queryString = "type=DynaCache,process=" + serverName + nodeSpecification + ",*"
        mbean = AdminControl.queryNames(queryString)
             
        #----------------------------------------------------------
        # validate instanceName
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
            print "\nError: Unrecognized cache instance \"" + instanceName + "\" specified for -cacheInstance argument."
            return


        #----------------------------------------------------------
        # infinite loop - open file, write stats, close file, sleep
        #----------------------------------------------------------
        printNames = "true"
        if (fileAppend == "true"):
            printNames = "false"
        #endIf
     
        while (0 == 0):
                
                #----------------------------------------------------------
                # invoke method on MBean
                #----------------------------------------------------------
                from time import localtime, strftime
                timestamp = strftime("%m/%d/%Y %H:%M:%S", localtime())

                # output would need to include cache instance name (** for all cases with cache instances)
                # output needs to be either:
                # CacheInstance=base cache
                # CacheInstance=JNDI name XXX

                # could specify all cache instances (foreach of getCacheInstanceNames)

                # if cacheInstance is [] then just gather statistics for base cache
                # otherwise gather statistics for each cacheInstance in cacheInstances
                contents = ""
                if (cacheInstances == []):
                    names = "Timestamp"
                    values = timestamp
                    stats = AdminControl.invoke(mbean, "getAllCacheStatistics").split(linesep)
                    for stat in stats:
                        nameValuePair = stat.split('=')
                        names = names + csvSeparator + nameValuePair[0]
                        values = values + csvSeparator + nameValuePair[1]
                    #endFor
                    if (printNames == "true"):
                        contents = names + "\n" + values + "\n"
                        printNames = 1
                    else:
                        contents = values + "\n"
                    #endElse
                else:
                    cacheInstanceCtr = 0
                    for cacheInstance in cacheInstances:
                        values = cacheInstance + csvSeparator + timestamp
                        stats = AdminControl.invoke(mbean, "getAllCacheStatistics", cacheInstance).split(linesep)
                        if (cacheInstanceCtr == 0 and printNames == "true"):
								names = "CacheInstanceName" + csvSeparator + "Timestamp"
                        for stat in stats:
							if (cacheInstanceCtr == 0 and printNames == "true"):
								nameValuePair = stat.split('=')
								names = names + csvSeparator + nameValuePair[0]
								values = values + csvSeparator + nameValuePair[1]
							else:
								nameValuePair = stat.split('=')
								values = values + csvSeparator + nameValuePair[1]
							#endIf
                        if (cacheInstanceCtr == 0 and printNames == "true"):
                            contents = names + "\n"
						#endIf
                        contents = contents + values + "\n"
                        cacheInstanceCtr += 1
                        printNames = "false"

                #----------------------------------------------------------
                # open file and write
                #----------------------------------------------------------
                try:
                    fileId = open(fileName, fileAccess)
                    fileId.write(contents);
                except:
                    print "\nError: Could not open/write to file \"" + fileName + "\"."
                    return
                #endTry
                
                fileAccess = "a"

                #----------------------------------------------------------
                # close file
                #----------------------------------------------------------
                fileId.close()

                #----------------------------------------------------------
                # sleep
                #----------------------------------------------------------
                #print "."
                java.lang.Thread.sleep(sleepMilliseconds)

        #endWhile

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
        print "\n Examples:"
        print "\n DynaCacheStatistics server1 abc.txt \"-sleepInterval 15 -fileAppend\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-sleepUnit hours -sleepInterval 1\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-cacheInstance *\""
        print "\n DynaCacheStatistics server1 xyz.txt \"-cacheInstance inst1\""
#endDef
       
#-----------------------------------------------------------------
# Main - DynaCacheStatistics.jacl
#-----------------------------------------------------------------
DynaCacheStatistics(sys.argv)