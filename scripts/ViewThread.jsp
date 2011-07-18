<%@page import="java.lang.management.*" %>

<%
	long id = Long.parseLong(request.getParameter("id"));
	ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
	ThreadInfo info = threadMXBean.getThreadInfo(id, Integer.MAX_VALUE);
%>
<html>
<head><title>Thread Details for <%=id%></title></head>
<body>
<%
	if (info == null) {
%>
<div>Unknown thread ID: <%=id%></div>
<%
	} else {
%>
<div>ID: <%=info.getThreadId()%></div>
<div>Name: <%=info.getThreadName()%></div>
<div>State: <%=info.getThreadState()%></div>
<%
		if (Thread.State.BLOCKED.equals(info.getThreadState())) {
%>
	<div>&nbsp; &nbsp; &nbsp; Lock Name: <%=info.getLockName()%></div>
	<div>&nbsp; &nbsp; &nbsp; Lock Owner ID: <a href="ViewThread.jsp?id=<%=info.getLockOwnerId()%>"><%=info.getLockOwnerId()%></a></div>
	<div>&nbsp; &nbsp; &nbsp; Lock Owner Name: <%=info.getLockOwnerName()%></div>
<%
	}
%>
<div>Suspended: <%=info.isSuspended()%></div>
<div>In Native Code: <%=info.isInNative()%></div>
<div>Blocked Count: <%=info.getBlockedCount()%></div>
<div>Blocked Time: <%=info.getBlockedTime()%> ms</div>
<div>Waited Count: <%=info.getWaitedCount()%></div>
<div>Waited Time: <%=info.getWaitedTime()%> ms</div>
<hr/>
<div>Stack Trace:</div>
<%
		for (StackTraceElement ste : info.getStackTrace()) {
%>
	<div>&nbsp; &nbsp; &nbsp; <%=ste.toString()%></div>
<%
		} //end for
	} // end else
%>
</body>
</html>
