
import java.io.IOException;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import com.ibm.websphere.servlet.session.IBMSession;

/**
 * Servlet Filter implementation class SessionUpdateFilter
 */
public class SessionUpdateFilter implements Filter {

	public void destroy() {
		System.out.println("SessionUpdateFilter.destroy()");
	}

	public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {

		System.out.println("SessionUpdateFilter.doFilter(ServletRequest, ServletResponse, FilterChain) ENTRY");
	    HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;
		
		// pass the request along the filter chain
		chain.doFilter(request, response);
		
		HttpSession session = httpRequest.getSession(false); // do not force creation if session was NOT created

		if (null != session){
			System.out.println("Retrieved session "+ session + " ID: "+ session.getId());
			List<String> attribNames = Collections.list((Enumeration<String>)session.getAttributeNames());
			for (String attribName : attribNames) {
				Object attribValue = session.getAttribute(attribName);
				System.out.println("\t" + attribName + "--> "+ attribValue);
				session.setAttribute(attribName, attribValue);
			}
		}
		
		if (session instanceof IBMSession){
			IBMSession ibmSession = (IBMSession) session;
			ibmSession.sync();
			System.out.println("SYNC issued for session "+ ibmSession.getId());
		}
		
		System.out.println("SessionUpdateFilter.doFilter(ServletRequest, ServletResponse, FilterChain) EXIT");
		
	}

	public void init(FilterConfig fConfig) throws ServletException {
		System.out.println("SessionUpdateFilter.init(FilterConfig)");
	}

}
