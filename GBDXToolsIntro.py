
# coding: utf-8

# # GBDX Tools Training Notebook

# ## First initialize the Interface object that handles authentication

# In[ ]:

from gbdxtools import Interface


# In[ ]:

gbdx = Interface()


# ## Searching for Data

# ### Searching by Geographic Area

# In[ ]:

wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"
results = gbdx.catalog.search(searchAreaWkt=wkt_string)


# In[ ]:

results[0:10]


# ### Adding a date filter

# In[ ]:

wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"
results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                          startDate="2004-01-01T00:00:00.000Z",
                          endDate="2012-01-01T00:00:00.000Z")


# In[ ]:

results


# ### You can add filters for any properties in the catalog items you are searching for. For example, here’s how you return only Quickbird 2 images:

# In[ ]:

wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"

filters = ["sensorPlatformName = 'QUICKBIRD02'"]

results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                          startDate="2004-01-01T00:00:00.000Z",
                          endDate="2012-01-01T00:00:00.000Z",
                          filters=filters)


# In[ ]:

filters = [
        "(sensorPlatformName = 'WORLDVIEW01' OR sensorPlatformName ='QUICKBIRD02')",
        "cloudCover < 10",
        "offNadirAngle > 10"
]

results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                          filters=filters)


# ### Search by Types
# 

# In[ ]:

wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"

types = [ "LandsatAcquisition" ]

results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                          types=types)
results


# ### Get Metadata Info about a given Catalog ID

# In[ ]:

record = gbdx.catalog.get('1050410011360700')
record


# ### Find Data Location given a Catalog ID

# In[ ]:

s3path = gbdx.catalog.get_data_location(catalog_id='1030010045539700')
s3path


# # Ordering imagery

# ### To order the image with DG factory catalog id 10400100143FC900:

# In[ ]:

order_id = gbdx.ordering.order('10400100143FC900')
print order_id


# ### The order_id is unique to your image order and can be used to track the progress of your order. The ordered image sits in a directory on S3. The output of the following describes where:

# In[ ]:

gbdx.ordering.status(order_id)


# # Running Worklfows
# 
# ### Workflows string tasks together to take imagery (or other data) do something to it, and produce an output.
# 
# 
# ## Data Locations
# 
# ### Every GBDX account comes with an S3 storage location that you can access to put your output data as you're working the system. There are many ways to access this data - first let's get the location of your private bucket and the credentials for access:
# 

# In[ ]:

s3creds = gbdx.s3.info
s3creds


# ## Here’s a quick workflow that starts with a Worldview 2 image over San Francisco, runs it through DigitalGlobe’s “Fast Ortho” and “Acomp” tasks, then saves to a user-specified location under s3://bucket/prefix.

# In[ ]:

bucket = s3creds['bucket']
prefix = s3creds['prefix']
s3out = "s3://" + bucket + "/" + "demo_output/"

data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # WV02 Image over San Francisco
aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=True)
workflow = gbdx.Workflow([ aoptask ])
workflow.savedata(aoptask.outputs.data, location="demo_output")
workflow.execute()


# ### We can easily cancel a workflow that we've kicked off as follows:

# In[ ]:

workflow2 = gbdx.Workflow( [] )  # instantiate a blank workflow
workflow2.id = <known_workflow_id>
workflow2.cancel()


# ### At this point the workflow is launched, and you can get status as follows:
# 
# 

# In[ ]:

workflow.status


# ## Tasks
# ### Tasks take inputs, produce outputs, and gbdxtools knows about it all! 

# In[ ]:

task = gbdx.Task("AOP_Strip_Processor")
task.inputs


# ### You can also interactively get more info on a particular input:

# In[ ]:

task.inputs.enable_acomp


# ### Task outputs can be interactively explored the same way as task inputs:
# 
# 

# In[ ]:

task = gbdx.Task("AOP_Strip_Processor")
task.outputs


# In[ ]:

task.outputs.log


# ## Linking Outputs from one task into Inputs of Another Task
# 
# ### The whole point of the workflow system is to build complex workflows with automagic data movement between tasks. This can be done as follows:

# In[ ]:

task1 = gbdx.Task("AOP_Strip_Processor")
task2 = gbdx.Task("Some_Other_task")
task2.inputs.<input_name> = task1.outputs.<output_name>.value


# ## Let's put this together and run a more complex workflow

# In[ ]:

data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003"
aoptask = gbdx.Task("AOP_Strip_Processor", data=data, enable_acomp=True, enable_pansharpen=False, enable_dra=False, bands='MS')
pp_task = gbdx.Task("ProtogenPrep",raster=aoptask.outputs.data.value)      # ProtogenPrep task is used to get AOP output into proper format for protogen task
prot_lulc = gbdx.Task("protogenV2LULC", raster=pp_task.outputs.data.value)
workflow = gbdx.Workflow([ aoptask, pp_task, prot_lulc ])
workflow.savedata(prot_lulc.outputs.data.value, location="some_folder_under_your_bucket_prefix")
workflow.execute()

