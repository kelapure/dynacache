<%@page import="java.lang.management.*"%>

<html>
<head>
<title>All Threads</title>
</head>
<body>

	<%
		ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
		String enableCPUTime = request.getParameter("cpuTime");
		if (enableCPUTime != null) {
			threadMXBean.setThreadCpuTimeEnabled("Enable"
					.equals(enableCPUTime));
		}
		String enableContention = request.getParameter("contention");
		if (enableContention != null) {
			threadMXBean.setThreadContentionMonitoringEnabled("Enable"
					.equals(enableContention));
		}
		enableCPUTime = threadMXBean.isThreadCpuTimeEnabled() ? "Disable"
				: "Enable";
		enableContention = threadMXBean
				.isThreadContentionMonitoringEnabled() ? "Disable"
				: "Enable";
				
	%>
	<div>
		<span><a href="AllThreads.jsp?cpuTime=<%=enableCPUTime%>"><%=enableCPUTime%>
				CPU Time</a>
		</span> <span><a
			href="AllThreads.jsp?contention=<%=enableContention%>"><%=enableContention%>
				Contention Monitoring</a>
		</span>
	</div>

	<div>
		<br>
		Current Thread: <%=Thread.currentThread().getId()%>
		<% if (threadMXBean.isCurrentThreadCpuTimeSupported()) {%>
			CPU time: <%= threadMXBean.getCurrentThreadCpuTime() %>
		<% } %>
		<br>
	</div>	
	
	<table>
		<tr>
			<td>ID</td>
			<td>Name</td>
			<td>State</td>
			<% if (threadMXBean.isThreadCpuTimeEnabled()) {%>
				<td> Cpu Time(NS) </td>
				<td> User Time(NS)</td>
			<% }%>
		</tr>
		<%
			long[] allIds = threadMXBean.getAllThreadIds();
			for (ThreadInfo info : threadMXBean.getThreadInfo(allIds)) {
		%>
		<tr>
			<td><a href="ViewThread.jsp?id=<%=info.getThreadId()%>"><%=info.getThreadId()%></a>
			</td>
			<td><%=info.getThreadName()%></td>
			<td><%=info.getThreadState()%></td>
			<% if (threadMXBean.isThreadCpuTimeEnabled()) {%>
				<td><%=threadMXBean.getThreadCpuTime(info.getThreadId()) %></td>
				<td><%=threadMXBean.getThreadUserTime(info.getThreadId()) %></td>
			<% }%>
						
		</tr>
		<%
			}
		%>
	</table>
</body>
</html>
