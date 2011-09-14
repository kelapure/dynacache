package com.ibm.ws.cache.sample;

import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

import com.ibm.websphere.cache.DistributedMap;
import com.ibm.ws.cache.servlet.MySerializableObjectKey;
import com.ibm.wsspi.cache.DistributedObjectCacheFactory;


public class TestDistributedMap extends TestCase {

    String className = null;

   public TestDistributedMap(String name) {
      super(name);
      className = "TestDistributedMap";
   }

   public static void main(String[] args)
   {
       junit.textui.TestRunner.run(suite());
   }

   public static Test suite()
   {
       return new TestSuite(TestDistributedMap.class);
   }

	public DistributedMap getTestMap() {

		//get hold of a DistributedMap via factory
		// cache can be configured here by passing a properties map
		return  DistributedObjectCacheFactory.getMap("myCache");

		// OR via JNDI lookup
		// cache is configured via a cacheinstances.properties or via the admin console Resources-> Object Cache INstances panel
		//return context.lookup("/myJNDICache")

	}

   public void testSize() {
       final String methodName = className+".testSize()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      assertTrue("size not zero after clear",map.size()==0);
      map.put("one","one");
      map.put("two","two");
      map.put("three","three");
      assertTrue("size does not match entries in cache",map.size()==3);
      System.out.println( methodName+" end" );
   }


   public void testClear() {
       final String methodName = className+".testClear()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      //set some entries
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data,
                 3,   //priority
                 10,  //timeout = 10 seconds
                 EntryInfo.NOT_SHARED,
                 new String[] {"dependency id"});
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      //clear the cache
      map.clear();
      //make sure entries are null
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String newData = (String) map.get(id);
         assertNull("cache entry not null after clear",newData);
      }
      System.out.println( methodName+" end" );
   }

   public void testDRSBootstrap() {
       final String methodName = className+".testDRSBootstrap()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.setDRSBootstrap(true);
      boolean enable = map.isDRSBootstrapEnabled();
      assertTrue("setDRSBootStrap to true",enable==true);
      map.setDRSBootstrap(false);
      enable = map.isDRSBootstrapEnabled();
      assertTrue("setDRSBootStrap to false",enable==false);
      System.out.println( methodName+" end" );
   }

   public void testPutGet() throws Exception {
       final String methodName = className+".testPutGet()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      for (int i=0;i<10000;i++) {
         String id = "test:"+i;
         Object oldValue = map.get(id);
         assertNull("cache entry not null before set",oldValue);
         String data = "this is a test value:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      System.out.println( methodName+" end" );
   }

   public void testObjectKey() throws Exception {
       final String methodName = className+".testObjectKey";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      // test putGet
      for (int i=0;i<2000;i++) {
         String id = "test:"+i;
         Object oid = new Thread(id);
         Object oldValue = map.get(oid);
         assertNull("cache entry not null before set",oldValue);
         String data = "this is a test value:"+i;
         map.put(oid,data);
         String newData = (String) map.get(oid);
         assertEquals("cache entry not equal after set",data,newData);
      }
      // test dependency id
      for (int i=0; i<2000; i++) {
        //Object iodd = new Thread("objectDepIdTest"+i);
        Object iodd = new  MySerializableObjectKey("objectDepIdTest"+i, true);
        String data2 = "this is a test value for ObjectDepIdTest";
        map.put(iodd,data2,
                 3,   //priority
                 10,  //timeout = 10 seconds
                 EntryInfo.NOT_SHARED,
                 new Object[] {"dependency id"});
        String newData2 = (String) map.get(iodd);
        assertEquals("cache entry not equal after set",data2,newData2);
        map.invalidate(iodd);
        String newData21 = (String) map.get(iodd);
        assertNull("cache entry not null after invalidation no. " + i,newData21);
      }
      // test invalidateByTemplate ( or clear)
      for (int i=0;i<2000;i++) {
         String id3 = "test:"+i;
         Object oid3 = new Thread(id3);
         Object oldValue3 = map.get(oid3);
         assertNull("cache entry not null before set",oldValue3);
         String data3 = "this is a test value:"+i;
         map.put(oid3,data3);
         String newData3 = (String) map.get(oid3);
         assertEquals("cache entry not equal after set",data3,newData3);
         map.clear();
         String newData31 = (String) map.get(oid3);
         assertNull("cache entry not null after clear",newData31);
      }
      System.out.println( methodName+" end" );
   }


   public void testPutReplace() throws Exception {
       final String methodName = className+".testPutReplace";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      for (int i=0;i<100;i++) {
         String id = "test:"+i;
         Object oldValue = map.get(id);
         assertNull("cache entry not null before set",oldValue);
         String data = "this is a test value:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      for (int i=0;i<100;i++) {
         String id = "test:"+i;
         String data = "This is a different value to replace previous:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after replace",data,newData);
      }
      System.out.println( methodName+" end" );
   }

   public void testTimeout() throws Exception {
       final String methodName = className+".testTimeout()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      //set some entries
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data,
                 3,   //priority
                 10,  //timeout = 10 seconds
                 EntryInfo.NOT_SHARED,
                 new String[] {"dependency id"});
         String newData = (String) map.get(id);
         assertEquals("testTimeout.1: cache entry not equal after set",data,newData);
      }
      //wait for timeout
      try {
         Thread.sleep(22000);
      } catch (Exception ex) {
      }
      //make sure entries are null
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String newData = (String) map.get(id);
         assertNull("testTimeout.2: cache entry " + id + " not null after timeout",newData);
      }
      map.setTimeToLive(3);  // set globalTimeToLive to 3 sec timeout
      map.setSharingPolicy(EntryInfo.NOT_SHARED);
      //set some entries
      for (int i=0;i<100;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("testTimeout.3: cache entry not equal after set",data,newData);
      }
      //wait for timeout
      try {
         Thread.sleep(20000);
      } catch (Exception ex) {
      }
      //make sure entries are null
      for (int i=0;i<100;i++) {
         String id = "test:"+i;
         String newData = (String) map.get(id);
         assertNull("testTimeout.4: cache entry " + id + " not null after timeout",newData);
      }
      map.setTimeToLive(-1);  // set globalTimeToLive to no timeout
      //set some entries
      for (int i=0;i<100;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("testTimeout.5: cache entry not equal after set",data,newData);
      }
      //wait for timeout
      try {
         Thread.sleep(20000);
      } catch (Exception ex) {
      }
      //make sure entries are not null
      for (int i=0;i<100;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         String newData = (String) map.get(id);
         assertEquals("testTimeout.6: cache entry not equal after waiting 20 sec",data,newData);
      }
      System.out.println( methodName+" end" );
   }


   public void testEntryInvalidation() throws Exception {
       final String methodName = className+".testEntryInvalidation()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      //set some entries
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data,
                 3,   //priority
                 600,  //timeout = 600 seconds
                 EntryInfo.NOT_SHARED,
                 new String[] {"dependency id"});
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      //invalidate each id
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         map.invalidate(id);
      }
      //make sure entries are null
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String newData = (String) map.get(id);
         assertNull("cache entry not null after invalidation",newData);
      }
      System.out.println( methodName+" end" );
   }


   public void testGroupInvalidation() throws Exception {
       final String methodName = className+".testGroupInvalidation()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      //set some entries
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data,
                 3,   //priority
                 600,  //timeout = 600 seconds
                 EntryInfo.NOT_SHARED,
                 new String[] {"dependency id"});
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      //invalidate the group id
      map.invalidate("dependency id");
      //make sure entries are null
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String newData = (String) map.get(id);
         assertNull("cache entry not null after invalidation",newData);
      }
      System.out.println( methodName+" end" );
   }

   public void testKeySet() throws Exception {
       final String methodName = className+".testKeySet()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      //set some entries
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      Set keySet = map.keySet();
      //make sure entries are in key set
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         assertTrue("key not found in key set",keySet.contains(id));
      }
      System.out.println( methodName+" end" );
   }

   public void testValuesCollection() throws Exception {
       final String methodName = className+".testValuesCollection()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      //set some entries
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      Collection values = map.values();
      //make sure values are in the collection
      for (int i=0;i<500;i++) {
         String data = "this is a test value:"+i;
         assertTrue("value not found in value set",values.contains(data));
      }
      System.out.println( methodName+" end" );
   }

   public void testContainsKey() throws Exception {
       final String methodName = className+".testContainsKey()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      //set some entries
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }

      //make sure entries are in the cache
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         assertTrue("key not found in map", map.containsKey(id));
      }
      System.out.println( methodName+" end" );
   }

   public void testContainsValue() throws Exception {
       final String methodName = className+".testContainsValue()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      //set some entries
      for (int i=0;i<500;i++) {
         String id = "test:"+i;
         String data = "this is a test value:"+i;
         map.put(id,data);
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      //make sure values are in the map
      for (int i=0;i<500;i++) {
         String data = "this is a test value:"+i;
         assertTrue("value not found in map:"+data,map.containsValue(data));
      }
      System.out.println( methodName+" end" );
   }


   public void testPutAll() throws Exception {
       final String methodName = className+".testPutAll()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      HashMap sampleMap = new HashMap();
      sampleMap.put("one","val one");
      sampleMap.put("two","val two");
      sampleMap.put("three","val three");
      map.putAll(sampleMap);
      assertTrue("entry one not found",map.get("one").equals("val one"));
      assertTrue("entry two not found",map.get("two").equals("val two"));
      assertTrue("entry three not found",map.get("three").equals("val three"));
      System.out.println( methodName+" end" );
   }

public void testIsEmpty() throws Exception {
       final String methodName = className+".testIsEmpty()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      assertTrue("map was not empty",map.isEmpty());
      System.out.println( methodName+" end" );
   }

public void testPutInvalidationInfo() throws Exception {
       final String methodName = className+".testPutInvalidationInfo()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
	  map.put("one", "value1",
			  1,   //priority
			  0,   //timeout
			  EntryInfo.NOT_SHARED,
			  new String[] {"depId1", "depId2", "depId3"});
	  map.put("one", "value2",
			  1,   //priority
			  0,   //timeout
			  EntryInfo.NOT_SHARED,
			  new String[] {"depId1", "depId2"});
	  map.invalidate("depId3");
	  String newData = (String) map.get("one");
	  assertEquals("cache entry remove after inavalidation by depId", "value2", newData);
      System.out.println( methodName+" end" );
   }


public void testInvalidationListeners() throws Exception {
       final String methodName = className+".testInvalidationListeners()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      map.enableListener(true);
      MyEventListenerImpl listener1 = new MyEventListenerImpl("Listener1", 5, null);
      map.addInvalidationListener(listener1);
      MyEventListenerImpl listener2 = new MyEventListenerImpl("Listener2", 5, null);
      map.addInvalidationListener(listener2);
      //set some entries
      for (int i=0; i < 2000; i++) {
         String id = "c_id_"+i;
         String data = "this is a test value:"+i;
         if (i == 1 || i == 3)
         {
            map.put(id,data,
                    3,   //priority
                    0,   //no timeout
                    EntryInfo.NOT_SHARED,
                    new String[] {"dep_id_1", "dep_id_2"});
         }
         else if (i == 2)
         {
            map.put(id,data,
                    3,   //priority
                    0,   //no timeout
                    EntryInfo.NOT_SHARED,
                    new String[] {"dep_id_1"});
         }
         else if (i == 4 || i == 5 || i == 6)
         {
            map.put(id,data,
                    3,   //priority
                    0,   //no timeout
                    EntryInfo.NOT_SHARED,
                    new String[] {"dep_id_2"});
         }
         else if (i == 8 || i == 9)
         {
            map.put(id,data,
                    3,   //priority
                    1,   //timeout = 1
                    EntryInfo.NOT_SHARED,
                    new String[] {"dep_id_3"});
         }
         else // i= 0, 7, 10, 2000
         {
            map.put(id,data,
                    3,   //priority
                    0,   //no timeout
                    EntryInfo.NOT_SHARED,
                    new String[] {"dep_id_4"});
         }
         String newData = (String) map.get(id);
         assertEquals("cache entry not equal after set",data,newData);
      }
      //invalidate the dep id
      System.out.println("*** Invalidate dep_id_1");
      map.invalidate("dep_id_1");
      listener1.waitOnCompletion();
      listener2.waitOnCompletion();

      for (int i=0; i < 10; i++) {
          String id = "c_id_"+i;
          if (i == 1 || i == 2 || i == 3 || i == 8 || i == 9) {
              String newData = (String) map.get(id);
              assertNull("cache entry not null after invalidation - " + id, newData);
          }
      }
      String rs = listener1.compare(new InvalidationListenerInfo("c_id_1", "this is a test value:1", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener1.compare(new InvalidationListenerInfo("c_id_2", "this is a test value:2", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener1.compare(new InvalidationListenerInfo("c_id_3", "this is a test value:3", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_1", "this is a test value:1", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_2", "this is a test value:2", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_3", "this is a test value:3", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener1.compare(new InvalidationListenerInfo("c_id_8", "this is a test value:8", com.ibm.websphere.cache.InvalidationEvent.TIMEOUT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener1.compare(new InvalidationListenerInfo("c_id_9", "this is a test value:9", com.ibm.websphere.cache.InvalidationEvent.TIMEOUT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_8", "this is a test value:8", com.ibm.websphere.cache.InvalidationEvent.TIMEOUT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_9", "this is a test value:9", com.ibm.websphere.cache.InvalidationEvent.TIMEOUT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 5);
      assertEquals("cache invalidation events not equal", "", rs);
      listener1.restart(4);
      listener2.restart(4);
      System.out.println("*** Invalidate c_id_4, c_id_5, c_id_6, c_id_7");
      map.invalidate("c_id_4");
      map.invalidate("c_id_5");
      map.invalidate("c_id_6");
      map.invalidate("c_id_7");
      listener1.waitOnCompletion();
      listener2.waitOnCompletion();
      for (int i=4; i < 8; i++) {
         String id = "c_id_"+i;
         String newData = (String) map.get(id);
         assertNull("cache entry not null after invalidation - " + id, newData);
      }
      rs = listener1.compare(new InvalidationListenerInfo("c_id_4", "this is a test value:4", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 4);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener1.compare(new InvalidationListenerInfo("c_id_5", "this is a test value:5", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 4);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_4", "this is a test value:4", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 4);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_5", "this is a test value:5", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 4);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener1.compare(new InvalidationListenerInfo("c_id_6", "this is a test value:6", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 4);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener1.compare(new InvalidationListenerInfo("c_id_7", "this is a test value:7", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 4);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_6", "this is a test value:6", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 4);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_7", "this is a test value:7", com.ibm.websphere.cache.InvalidationEvent.EXPLICIT, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 4);
      assertEquals("cache invalidation events not equal", "", rs);

      System.out.println("*** Overflow cacheSize by 2 - c_id_0, c_id_10");
      listener1.restart(2);
      listener2.restart(2);
      for (int i=2000; i < 2011; i++) {
         String id = "c_id_"+i;
         String data = "this is a test value:"+i;
         map.put(id,data,
                 3,   //priority
                 0,   //no timeout
                 EntryInfo.NOT_SHARED,
                 new String[] {"dep_id_4"});
      }
      listener1.waitOnCompletion();
      listener2.waitOnCompletion();
      rs = listener1.compare(new InvalidationListenerInfo("c_id_0", "this is a test value:0", com.ibm.websphere.cache.InvalidationEvent.LRU, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 2);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener1.compare(new InvalidationListenerInfo("c_id_10", "this is a test value:10", com.ibm.websphere.cache.InvalidationEvent.LRU, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 2);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_0", "this is a test value:0", com.ibm.websphere.cache.InvalidationEvent.LRU, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 2);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("c_id_10", "this is a test value:10", com.ibm.websphere.cache.InvalidationEvent.LRU, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 2);
      assertEquals("cache invalidation events not equal", "", rs);

      System.out.println("*** clear");
      listener1.restart(1);
      listener2.restart(1);
      map.clear();
      listener1.waitOnCompletion();
      listener2.waitOnCompletion();
      rs = listener1.compare(new InvalidationListenerInfo("*", null, com.ibm.websphere.cache.InvalidationEvent.CLEAR_ALL, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 1);
      assertEquals("cache invalidation events not equal", "", rs);
      rs = listener2.compare(new InvalidationListenerInfo("*", null, com.ibm.websphere.cache.InvalidationEvent.CLEAR_ALL, com.ibm.websphere.cache.InvalidationEvent.LOCAL, "testInvalidationListeners"), 1);
      assertEquals("cache invalidation events not equal", "", rs);
      map.removeInvalidationListener(listener1);
      map.removeInvalidationListener(listener2);
      map.enableListener(false);
      System.out.println( methodName+" end" );
   }

public void testAlias() throws Exception {
       final String methodName = className+".testAlias()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
	  map.put("one", "value1",
			  1,   //priority
			  0,   //timeout
			  EntryInfo.NOT_SHARED,
			  new String[] {"depId1", "depId2"});
      map.addAlias("one", new String[] {"aliasOne", "aliasTwo"});
	  String value = (String) map.get("aliasOne");
	  assertEquals("get aliasOne", "value1", value);
	  value = (String) map.get("aliasTwo");
	  assertEquals("get aliasTwo", "value1", value);
      map.removeAlias("aliasOne");
	  value = (String) map.get("aliasOne");
      assertNull("value not null after remove aliasOne", value);
	  value = (String) map.get("aliasTwo");
	  assertEquals("get aliasTwo", "value1", value);
      map.removeAlias("aliasTwo");
	  value = (String) map.get("aliasOne");
      assertNull("value not null after remove aliasTwo", value);
	  value = (String) map.get("one");
	  assertEquals("get id - one", "value1", value);
      System.out.println( methodName+" end" );
   }

public void testMultithreadedBig() throws Exception {
       final String methodName = className+".testMultithreadedBig()";
       System.out.println( "\n"+methodName+" begin" );
      DistributedMap map = getTestMap();
      map.clear();
      TesterThread threads[] = new TesterThread[15];
      for (int i=0;i<threads.length;i++) {
          threads[i] = new TesterThread(map,"thread:"+i,1,10000,0);
      }
      for (int i=0;i<threads.length;i++) {
          threads[i].start();
      }
      for (int i=0;i<threads.length;i++) {
          threads[i].join();
      }
      System.out.println( methodName+" end" );
   }

public void testMultithreadedVerify() throws Exception {
       final String methodName = className+".testMultithreadedVerify()";
       System.out.println( "\n"+methodName+" begin" );
      _multithreadVerify(getTestMap());
      System.out.println( methodName+" end" );
   }

   // current performance target is 1.9.  we should decrease this
   // as much as possible.  this must be updated as we make
   // performance improvements.

   static final double targetRatio = 1.9;

   public void testMutltiThreadPerformance() throws Exception {

       final String methodName = className+".testMutltiThreadPerformance()";
       System.out.println( "\n"+methodName+" begin" );

       // WARM up for the test... let the JIT do its job...
      _multithreadVerify(Collections.synchronizedMap(new HashMap()));
      _multithreadVerify(getTestMap());

      // test a standard synchronized map
      long start1 = System.currentTimeMillis();
      _multithreadVerify(Collections.synchronizedMap(new HashMap()));
      long end1 = System.currentTimeMillis();

      // test our map
      long start2 = System.currentTimeMillis();
      _multithreadVerify(getTestMap());
      long end2 = System.currentTimeMillis();

      //compare
      System.err.println("\n-----------------------");
      System.err.println("performance validation");
      System.err.println("-----------------------");

      //display
      System.err.println("standard synchronized map : "+(end1-start1)+" ms");
      System.err.println("distributedmap            : "+(end2-start2)+" ms");
      double ratio = ((double)(end2-start2)) / ((double)(end1-start1));
      System.err.println("performance ratio: "+ratio);
      System.err.println("target ratio: " + targetRatio);
      System.out.println( methodName+" end" );
   }


   // utility function used to stress a Map
   private void _multithreadVerify(Map map) throws Exception {
      map.clear();
      TesterThread threads[] = new TesterThread[15];
      for (int i=0;i<threads.length;i++) {
          threads[i] = new TesterThread(map,"thread:"+i,25,100,10);
      }
      for (int i=0;i<threads.length;i++) {
          threads[i].start();
      }
      for (int i=0;i<threads.length;i++) {
          threads[i].join();
      }
   }


   class TesterThread extends Thread {
       String name;
       int items;
       Map map;
       int getIterations;
       int loops;

       TesterThread(Map map, String name, int loops, int items, int getIterations) {
          this.map  = map;
          this.name = name;
          this.items = items;
          this.getIterations = getIterations;
          this.loops = loops;
       }

       public void run() {
          for (int k=0;k<loops;k++) {
             for (int i=0;i<items;i++) {
                String id = name+":"+i;
                String data = name+": this is a test value:"+i;
                map.put(id,data);
             }
             for (int j=0;j<getIterations;j++) {
               for (int i=0;i<items;i++) {
                  String id = name+":"+i;
                  String data = name+": this is a test value:"+i;
                  String newData = (String) map.get(id);
                  assertEquals("cache entry not equal after set",data,newData);
               }
             }
          }
       }
   }

}
