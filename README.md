# pyeloqua-cleanzipcode
pyeloqua example for beginners showing basic cleanup of US zipcodes

# Intro
Python is a cool programming language. Most marketers using automation want to do cool stuff with their data. Enough said? Cool. We built the pyeloqua package to help make it easier.

Let's start simple: take a segment of Eloqua contacts and cleanup their zipcode field. Bad form submissions and uploads can cause poorly formatted junk to creep into this field. Like this:
```
295
12543-2334
32123 NEW ADDRESS
59402
```
Obviously, the last one is in the valid format, and the rest have something non-standard about them. You could fix it using a lookup table, but then you'd have to anticipate every possible way the fields could go wrong (and you'd have to analyze your entire database to determine what is valid vs. invalid and, believe me, that's not a fun task).

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

Remeber that segment we made earlier? It's baaaaack!!! We want to export only the contacts in that segment, so we have to create a filter the API can work with:
```python
myFilter = elq.FilterExists(name='My Zipcodes to clean', existsType='ContactSegment')
```
