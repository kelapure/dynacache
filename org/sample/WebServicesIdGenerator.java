
/**
 * This sample is provided for use in customer applications to cache webservices responses
 * in WebSphere Application Server
 */
package org.sample;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.UnsupportedEncodingException;
import java.util.StringTokenizer;

import com.ibm.ejs.ras.Tr;
import com.ibm.ejs.ras.TraceComponent;
import com.ibm.websphere.servlet.cache.CacheConfig;
import com.ibm.websphere.servlet.cache.IdGenerator;
import com.ibm.websphere.servlet.cache.ServletCacheRequest;


public class WebServicesIdGenerator implements IdGenerator  {

	private final static TraceComponent tc = Tr.register(WebServicesIdGenerator.class,
			"WebSphere Dynamic Cache", "com.ibm.ws.cache.resources.dynacache");
	
	private static final String GET_ACCOUNT = "\"getAccount\"";
	private static final String STREAM_ENCODING = "UTF-8";
	private static final String ACTION = "action=";
	private static final String ACCOUNTID_START = "<accountID>";
	private static final String ACOUNTID_END = "</accountID>";
	private static final String COLON = ":";
	private static final String DELIMITER= ";";
		
	/**
	 * Cache policy that governs if a response is cached or not
	 * 
	 * Cache the response for a unique accountID and the getAccount action
	 * 
	 * returning null id is like telling Dynacache to not worry about caching this response
	 * 				  or looking in the cache for this response
	 * 
	 *  returning a non-null id will result in dynacache caching the response if the id does not exist
	 *  					 in the cache (CACHE MISS) or simply returning the cached response for that id from the cache 
	 */
	public String getId(ServletCacheRequest request) {
		
		String cache_id = null;
		String accountID = null;

		if (isActionGetAccount(request)){
			
			request.setGeneratingId(true);  //** DO NOT REMOVE... THIS IS NEEDED FOR PROPER PARSING OF RESPONSE
			
			/**
			 * Insert custom code here for parsing required cache policy elements from the response
			 * to formulate the cacheid
			 */
			accountID = getAccountID(request); // ** pull out the cache parameter of interest from the SOAP response
			
			request.setGeneratingId(false); //** DO NOT REMOVE... THIS IS NEEDED FOR PROPER PARSING OF RESPONSE
		}
		
		if (null != accountID){
			
			//if our cache policy is satisfied return the cacheid
			//Dynacache will use this cache-id to cache the response
			//This cacheid will be seen in the CacheMonitor application		
			cache_id = createCacheID(accountID);
			
		} else {
			cache_id = null;
		}		
		if (tc.isDebugEnabled()){
			Tr.debug(tc, "returning cache-id "+cache_id);
		}
		
		return cache_id;
	}

	//cache_id will look like action="getAccount:<accountID>234478</accountID>
	private String createCacheID(String acctID) {
		StringBuffer strBuf = new StringBuffer();
		strBuf.append(ACTION).append(GET_ACCOUNT).append(COLON);
		strBuf.append(ACCOUNTID_START).append(acctID).append(ACOUNTID_END);
		return  strBuf.toString();
	}

	/* pull out account id from ...
	   <soap:Body> 
	      <api:getAccount> 
	         <accountID>234478</accountID> 
	      </api:getAccount> 
	   </soap:Body> 
	*/
	private String getAccountID(ServletCacheRequest request) {
		
		String accountID = null;
		try {			
			Reader reader = getReader(request);
			String requestBody = readInputStreamAsString(reader);
			if (tc.isDebugEnabled()){
				Tr.debug(tc, "Read a body of size "+requestBody.length()+" bytes");
			}
			int startIndex = requestBody.indexOf(ACCOUNTID_START);
			if (startIndex != -1){
				int endIndex = requestBody.indexOf(ACOUNTID_END);
				accountID = requestBody.substring(startIndex + ACCOUNTID_START.length(), endIndex);
				if (tc.isDebugEnabled()){
					Tr.debug(tc, "found accountID "+accountID);
				}
				
			}	
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		return accountID;
		
	}

	private Reader getReader(ServletCacheRequest request) throws IOException, UnsupportedEncodingException {
		Reader reader = request.getReader();
		if (null == reader){
			reader = new InputStreamReader(request.getInputStream(), STREAM_ENCODING);
		}
		return reader;
	}
	
	private String readInputStreamAsString(Reader r) throws IOException {
		
		final char[] buffer = new char[0x10000]; // 64K buffer
		StringBuilder out = new StringBuilder();
		
		int read;
		do {
			read = r.read(buffer, 0, buffer.length);
			if (read > 0) {
				out.append(buffer, 0, read);
			}
		} while (read >= 0);

		return out.toString();

	}

	private boolean isActionGetAccount(ServletCacheRequest request) {
		boolean actionIsGetAccount = false;
		
		String soapAction = request.getHeader("SOAPAction");
		if (soapAction != null) {
			if (tc.isDebugEnabled()){
				Tr.debug(tc, "Retrieved SOAPAction " + soapAction);
			}
			if (soapAction.equals(GET_ACCOUNT)){
				actionIsGetAccount = true;
			}
			
		} else {
			
			//pull out the action from the http request content-type
			//Content-Type: application/soap+xml;charset=UTF-8;action="getAccount" 
			String contentType = request.getContentType();
	
			if (tc.isDebugEnabled()){
				Tr.debug(tc, "Retrieved contentType " + contentType);
			}
			//parse the content-type with the ; delimiter
			StringTokenizer strToken = new StringTokenizer(contentType, DELIMITER, false);
			while (strToken.hasMoreTokens()) {
				 String token = strToken.nextToken();
				 int index = token.indexOf(ACTION);
		         if (index != -1){	
		        	String actionValue = token.substring(index + ACTION.length());
		     		if (tc.isDebugEnabled()){
		    			Tr.debug(tc, "actionValue=" + actionValue);
		    		}
		     		if (actionValue.equals(GET_ACCOUNT)){
		        		 actionIsGetAccount = true;
		        		 break;
		        	 }
		         }
		     }
		}
		if (tc.isDebugEnabled()){
			Tr.debug(tc, "actionIsGetAccount "+actionIsGetAccount);
		}
		return actionIsGetAccount;
	}

	//Deprecated method ... do nothing
	public int getSharingPolicy(ServletCacheRequest request) {
		//Dynacache runtime will not do anything 
		return 0;
	}

	//Deprecated method ... do nothing
	public void initialize(CacheConfig cc) {		
		//Dynacache runtime will not do anything 
	}	

}

