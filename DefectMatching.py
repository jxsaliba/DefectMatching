import pandas as pd


#import the 1998 raw ILI listing
ili98 = pd.read_excel('perenco162ili.xlsx', sheet_name='Raw 1998 data')

#import the 2012 raw ILI listing
ili12 = pd.read_excel('perenco162ili.xlsx', sheet_name='Raw 2012_Pipeline  Listing')
ili12 = ili12.iloc[5:]
ili12 = ili12.reset_index(drop=True)

ili12.columns = ['Weld Number', '2012 Abs Distance','2012 Rel Distance','2012 Spool length','2012 Feature Type','2012 Feature identification','2012 Anomaly dim class','2012 Orientation','2012 Nom WT','2012 Length','2012 Width','2012 Peak Depth','2012 Avg Depth','2012 INT/EXT','2012 ERF','2012 Comment','2012 Cluster Identifier','2012 Eastings','2012 Northings','2012 Elevation']

###1998 Listing

#removes the empty columns
ili98 = ili98.drop(['Pressure Ratio', 'Unnamed: 9'], axis=1)

#removes empty rows with no data shown as NaN
ili98 = ili98.dropna()

ili98.columns = ['Weld Number','1998 Rel Distance', '1998 Abs Distance','Int/Ext','1998 Comment','1998 Depth','1998 Length','1998 Orientation','1998 Width']

#create a separate dataframe with only the INTERNAL defects
ili98int = ili98[(ili98['Int/Ext'] == 'INTERNAL')]
ili98int = ili98int.drop(['Int/Ext'], axis=1)

#For this new dataframe remove the defects with less than 10% depth
ili98int10 = ili98int[(ili98int['1998 Depth'] >= 0.1)]

#create a separate dataframe with only the EXTERNAL defects
ili98ext = ili98[(ili98['Int/Ext'] == 'EXTERNAL')]


ili98int10 = ili98int10.drop_duplicates()


### 2012 listing

#keep only the defects and drop the welds
ili12 = ili12[(ili12['2012 Feature Type'] == 'Anomaly (ANOM)')]
ili12int = ili12[(ili12.iloc[:,13] == 'INT ')]



#for this new dataframe remove the defects with less than 10% depth

ili12int10 = ili12int[(ili12int['2012 Peak Depth'] >= 0.1)]
ili12int10 = ili12int10.drop_duplicates()


# merge the two on common weld number
output = pd.merge(ili12int10, ili98int10, how='outer', on='Weld Number' )
#drop possible irrelevant column
output = output.drop(columns=['2012 ERF'])
# drop NaN's and duplicate rows
output = output.dropna()
output = output.drop_duplicates()
#

#compuations to find whether the defects are indeed the same one. Using product
# of Weld number and Rel distance to find a reference factor that will be used
# to merge both listings into one.
#Further operations later will filter out the defects based on hour clock orientation similarity
# Columns A, B, C and D are therefore only to create these operations for filtering
output['A'] = output['Weld Number']*output['1998 Rel Distance']
output['B'] = output['Weld Number']*output['2012 Rel Distance']
output['C'] = output['A']/output['B']

#retain only the rows where the ratio of products of Rel Distance* Weld number is the same for both '98 and '12
output = output[((output['C']) <= 1.5) & ((output['C']) >= 0.75) ]

#this converts the orientation hour clock to a float number type
output['1998 Orientation'] = output['1998 Orientation'].apply(lambda x: int(x[0+1])*10 + int(x[1+1])+  int(x[3+1])*0.1 + int(x[4+1])*0.01)
output['2012 Orientation'] = output['2012 Orientation'].apply(lambda x: int(x[0+1])*10 + int(x[1+1])+  int(x[3+1])*0.1 + int(x[4+1])*0.01)

#find the difference in minutes (in decimal) between hour clock orientations
output['D'] = abs(output['1998 Orientation'] - output['2012 Orientation'])
#difference in hour clock difference to determine whether indeed the defects correspond is set to 30mins
# i.e. 0.5 hours here.
# Could be much less.
output = output[(output['D']) <= 0.5]
output = output.reset_index(drop=True)


#export to excel
output.to_excel("DefectMatchingOutput.xlsx") 