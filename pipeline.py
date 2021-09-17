#kELVIN WHITE TASK
#import print/logging library
import logging,json

#import apache beam library
import apache_beam as beam
#import pipeline options.
from apache_beam.options.pipeline_options import  PipelineOptions

from apache_beam.io.textio import WriteToText


#Set log level to info
root = logging.getLogger()
root.setLevel(logging.INFO)


#Create a pipeline
pipeline = beam.Pipeline(options=PipelineOptions())

#File Path
filePath ='pp-sep.csv'


#Read Dataset From Test 
newDataObject = (pipeline | 'Read Transaction  CSV' >>  beam.io.ReadFromText(filePath))

#Combine Unique value to generate   ID
def GenerateUniqueId(Obj1,Obj2):
    RawUniqueID=str(Obj1)+str(Obj2)
    UniqueID=RawUniqueID.replace('"', '')
    return UniqueID.replace(' ', '')
                   

#function to print the size of a PCollection
def printSize(PColl,PName):
    #Print the number of lines read
    (  PColl
                | 'Counting Lines for  %s' % PName >> beam.CombineGlobally(beam.combiners.CountCombineFn())
                | 'Print Line Count for %s' % PName >> beam.ParDo(lambda c: logging.info('\nTotal Lines in %s = %s \n' , PName,c))  
     )

# #Function to extract Product Type and Price
class ExtractPropertyType(beam.DoFn):
  def process(self, element):
        strArray = element.split(",")
        UniqueID=GenerateUniqueId(strArray[3],strArray[7])
        NewObj= {'id':strArray[0] ,'price':strArray[1],'postcode':strArray[3],'paon':strArray[7],'saon':strArray[9],'street':strArray[11],'locality':strArray[12],'town':strArray[13],'unique_id':UniqueID}
        yield (NewObj)
        


       
PropertyCleanData = ( newDataObject 
                   | 'Extracting DataSet and Cleaning' >> beam.ParDo(ExtractPropertyType())
                   | 'Assign Schema ' >> beam.Map(lambda item: beam.Row(id=item['id'],
                                                                    price=item['price'],
                                                                    postcode=item['postcode'],
                                                                    paon=item['paon'],
                                                                    saon=item['saon'],
                                                                    street=item['street'],
                                                                    locality=item['locality'],
                                                                    town=item['town'],
                                                                    unique_id=item['unique_id'],
                                                                    ))
                    )

# #Group the PCollection
PropertyTypeGroups = ( PropertyCleanData
                | 'Grouping by Unique id ' >> beam.GroupBy(TransID='unique_id')
                )

#Print size of PCollection
printSize(PropertyTypeGroups,'Property Type Groups')

 # WriteToText writes a simple text file with the results.
PropertyTypeGroups | WriteToText(file_path_prefix="output")


# Run the pipeline
result = pipeline.run()
#  wait until pipeline processing is complete
result.wait_until_finish()