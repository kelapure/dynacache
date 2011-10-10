<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<META name="GENERATOR" content="IBM WebSphere Page Designer V3.5.2 for Windows">
<META http-equiv="Content-Style-Type" content="text/css">
<TITLE>Max Cache</TITLE>
</HEAD>

<BODY BGCOLOR="#FFFFFF">
<P align="center">Invalidate Cache<BR>
This program will invalidate the cached object with the key you specify</P>
<P><BR>
</P>
<FORM action="invalidateIT.jsp" method="POST">Key or Dependency ID : <INPUT size="20" type="text" name="key"><BR>
invalidate - invalidates the given key. If the key is for a specific cache entry, then only that object is invalidated. If the key is for a dependency id, then all objects that share that dependency id will be invalidated.
<BR><br>
<input type="checkbox" name="nioMap" /> : Check if using NIO Dmap <br><br>

ObjectCacheInstance jndiName (string) : <INPUT size="40" type="text" name="jndi"><BR>
<BR>

Output to SystemOut.log: <SELECT name="doLogging">
	<OPTION value="false" selected>false</OPTION>
	<OPTION value="true">true</OPTION>
</SELECT><BR>
<br>
<INPUT type="submit" name="SUBMIT" value="Invalidate this Cached Object"><BR>
<BR>
</FORM>

</BODY>
</HTML>

