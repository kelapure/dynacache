<%@ page import = "javax.naming.*" %>
<%@ page import = "com.ibm.websphere.cache.*" %>

<%
	/*
	 * This code was written by Arthur Meloy
	 * Its purpose is to test IBM's WebSphere Application Server Dynamic Cache
	*/
	
	//get the parameters
	String key = (String)request.getParameter("key");
	String jndi = (String)request.getParameter("jndi");
	String log = (String)request.getParameter("doLogging");
	String nioMap = (String)request.getParameter("nioMap");
	
	boolean doLogging = false;
	if (log.equalsIgnoreCase("false"))
	{
		doLogging = false;
	}
	else
	{
		doLogging = true;
	}
	
	//look up the distributed map 
	InitialContext ic = new InitialContext();
	//DistributedMap dmap =(DistributedMap)ic.lookup(jndi);
	DistributedMap dmap = null;
	DistributedNioMap dniomap = null;
	if (nioMap == null) { 
	   dmap =(DistributedMap)ic.lookup(jndi);
	   dmap.invalidate(key);
	}   
	else {
 	   dniomap =(DistributedNioMap)ic.lookup(jndi); 
       dniomap.invalidate(key);   
    }   
	
%>

<!-- Sample JSP file -->
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<META name="GENERATOR" content="IBM WebSphere Page Designer V3.5.2 for Windows">
<META http-equiv="Content-Style-Type" content="text/css">
<TITLE>Invalidate a Cached Object</TITLE>
</HEAD>
<body>
<%
	String msg = "A request to invalidate the cached object(s) with the Key or Dependency ID = " + key + " has been made in the ObjectCacheInstance=" + jndi;

if (doLogging == true)
{
	// lookup logger
	com.ibm.maxcache.LoggerHome logIThome = (com.ibm.maxcache.LoggerHome)ic.lookup("java:comp/env/ejb/Logger");
	//create a logger
	com.ibm.maxcache.Logger logIT = (com.ibm.maxcache.Logger) logIThome.create();
	//log the message
	logIT.logit(msg);
	//remove the logger object
	logIT.remove();
}
%>
<%=msg%>
<br><br>
<a href="main.htm">back to main</a>
</body>
</html>
