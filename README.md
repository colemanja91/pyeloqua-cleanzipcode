# pyeloqua-cleanzipcode
pyeloqua example for beginners showing basic cleanup of US zipcodes

# Intro
Python is a cool programming language. Most marketers using automation want to do cool stuff with their data. Enough said? Cool. We built the pyeloqua package to help make it easier.

Let's start simple: take a segment of Eloqua contacts and cleanup their zipcode field. Bad form submissions and uploads can cause poorly formatted junk to creep into this field. Like this:
```
295
12543-2334
32123 NEW ADDRESS
00001
59402
```
Obviously, the last one is in the valid format, and the rest have something non-standard about them. The next to last one only looks valid. You could fix it using a lookup table, but then you'd have to anticipate every possible way the fields could go wrong (and you'd have to analyze your entire database to determine what is valid vs. invalid and, believe me, that's not a fun task).

If we use python, we can write a few lines of code to cover all the above cases and only output valid zipcode values. Eloqua's Bulk API 2.0 gives a nice platform for importing/exporting the data we want to edit.

## Setup
First, you'll need to install python and pip, a package manager:

[For Linux](http://docs.python-guide.org/en/latest/starting/install/linux/)
[For Mac/OS X](http://docs.python-guide.org/en/latest/starting/install/osx/)
[For Windows](http://docs.python-guide.org/en/latest/starting/install/win/)

Now install the packages we need (within your command terminal, or an IDE like Eclipse or PyCharm):
```
pip install requests
pip install pyeloqua
pip install zipcode
```
## Create an Eloqua segment
We don't want to export all the contacts in our database, just a segment of them. I setup this segment which we'll use later during the export:

![alt-text](https://github.com/colemanja91/pyeloqua-cleanzipcode/blob/master/segmentTestZipcode.png "Our test segment")

## Export segment using pyeloqua
Let's start by opening a python session by typing `python` in your terminal window or command prompt (or you can open your IDE).
Now load in the requisite packages:
```python
import re ## comes standard with python and includes tools for working with strings
import zipcode ## Includes functions for validating and working with zipcodes. Handy, right?
from pyeloqua import Eloqua ## for working with Eloqua's Bulk API
```
Use our login credentials to setup an Eloqua session:
```python
elq = Eloqua(company='mycompany', username='colemanja91', password='mypassword')
```
check to make sure it worked:
```python
elq.siteId ## outputs your Eloqua instance Site ID
elq.userDisplay ## your Eloqua user display name
```
If you couldn't get in, you may not have the right user account permissions.

Exporting data through the Bulk API requires a two pieces of information: the fields to export, and the filters to apply. It also requires that they be given in a certain format. pyeloqua has built-in functions to put the information in a language the API understands.

First the fields; we'll keep it simple and only export the two that we need, Email Address and Zip Code.
```python
findTheseFields = ['Email Address', 'Zip or Postal Code'] ## a list of fields we want from Eloqua
myFields = elq.CreateFieldStatement(entity='contacts', fields = findTheseFields, useInternalName=False)
print(myFields)
```
The output will show the two fields above in the format the API expects.

Remember that segment we made earlier? It's baaaaack!!! We want to export only the contacts in that segment, so we have to create a filter the API can work with:
```python
myFilter = elq.FilterExists(name='My Zipcodes to clean', existsType='ContactSegment')
print(myFilter)
```
Now that these are defined, we can create our export:
```python
myExport = elq.CreateDef(entity='contacts', defType='exports', fields=myFields, filters=myFilter, defName="My zipcode export")
```
Then tell the API to sync the data so we can get it:
```python
mySync = elq.CreateSync(defObject=myExport)
status = elq.CheckSyncStatus(syncObject=mySync)
print(status)
```
When all the data is ready, the `print(status)` command should output `success`. Download all the data!!!
```python
data = elq.GetSyncedData(defObject=myExport)
print(len(data)) ## tells you how many records were exported; should match the number from our segment
print(data[0]) ## show us the first row of data
```
Shazam!

## Do the fun data stuff
Now we can clean our data. We'll tell python to go through each record and update the zipcode value using the rules we give it:
```python
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

```
How cool is that? We just covered all the scenarios listed at the beginning without having to actually create a table of all possible values. Could we do more? Yes, but it's getting late and I'm getting tired. Let's put these values back in Eloqua.

## Import back to Eloqua
This is pretty similar to what we did before: give the API a list of fields, then send over the data.
```python
importDef = elq.CreateDef(entity='contacts', defType='imports', fields=myFields, defName='My zipcode import', identifierFieldName="Email Address")
postInData = elq.PostSyncData(data=data, defObject=importDef)
```

And that's it! We just used python to clean up the zipcode field for a segment of contacts!!!!

## Running it faster
OK, we did that once by manually typing all that code. What if we want to repeat the exact same thing in the future, but don't want to write it all? We can put everything we did in a python script, then it's just one line of code to run. I even attached it in this git repo, so you just have to clone or copy/paste to follow along.

```
python Contacts.CleanZipcode.py
```

That will automatically run the exact code we used above, and will output to the terminal what it's doing. You could also open it in an IDE and run a few lines at a time - your choice. Just make sure you replace the dummy Eloqua credentials at the beginning with your own.

# Hope this was helpful!
