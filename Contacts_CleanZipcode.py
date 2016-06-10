import re ## comes standard with python and includes tools for working with strings
import zipcode ## Includes functions for validating and working with zipcodes. Handy, right?
from pyeloqua import Eloqua ## for working with Eloqua's Bulk API

print("try to connect...")
elq = Eloqua(company='mycompany', username='colemanja91', password='mypassword')

print("Eloqua Site ID: " + elq.siteId) ## outputs your Eloqua instance Site ID
print("Eloqua User: " + elq.userDisplay) ## your Eloqua user display name
print("Connected!")

print("Create a field statement for the API")
findTheseFields = ['Email Address', 'Zip or Postal Code'] ## a list of fields we want from Eloqua
myFields = elq.CreateFieldStatement(entity='contacts', fields = findTheseFields, useInternalName=False)
print(myFields)

print("Create a filter for the API")
myFilter = elq.FilterExists(name='My Zipcodes to clean', existsType='ContactSegment')
print(myFilter)

print("Tell the API what we want to export")
myExport = elq.CreateDef(entity='contacts', defType='exports', fields=myFields, filters=myFilter, defName="My zipcode export")
print("Start syncing the data for export")
mySync = elq.CreateSync(defObject=myExport)
status = elq.CheckSyncStatus(syncObject=mySync)
print(status)

print("Get the data...")

data = elq.GetSyncedData(defObject=myExport)
print("Data has " + str(len(data)) + " records") ## tells you how many records were exported; should match the number from our segment
print("First row: ")
print(data[0]) ## show us the first row of data

print("Clean up the zipcode values")
for row in data:
  if (row['Zip or Postal Code']!=''): ## Only process if the zipcode field is not blank
    zip_old = row['Zip or Postal Code'] # get the value from the field
    zip_clean = re.split('[^0-9]', zip_old)[0] # if there are any spaces, dashes or breaks, get only the first string of numbers i.e.; '12345-123' becomes '12345', and '87890 NEW ADDRESS' becomes '87890'
    zip_clean = zip_clean[:5] # trim down to only the first five digits
    zip_clean = zip_clean.zfill(5) # if the string is shorter than 5 digits, add 0's to the left side
    if (zipcode.isequal(zip_clean)): # check if zipcode is valid
      row['Zip or Postal Code'] = zip_clean # put the value back on the contact record
    else:
      row['Zip or Postal Code'] = '' # If not valid, set to blank

print("Import the updated data back into Eloqua...")
importDef = elq.CreateDef(entity='contacts', defType='imports', fields=myFields, defName='My zipcode import', identifierFieldName="Email Address")
postInData = elq.PostSyncData(data=data, defObject=importDef)
print("All done!")
