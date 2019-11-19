""" module to test PaaS main """
from main import BuildPipeline

pipeline = BuildPipeline()

pipeline.addService('com0', 'rmq_com.py')
pipeline.addService('com1', 'rmq_com.py', parentName='com0')
pipeline.addService('com2', 'rmq_com.py', parentName='com0')
pipeline.addService('com3', 'rmq_com.py', parentName='com0')
pipeline.addService('com4', 'rmq_com.py', parentName='com2')

pipeline.buildPipeline()

input("Press Enter to shut down the platform...")

pipeline.terminatePipeline()


