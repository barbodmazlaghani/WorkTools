# Library Calling
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import sys
import socket           #for check internet connection
import tkinter.messagebox as messagebox
#============================================
# Input
FigNum = 0

#============================================
# How to read data from IPCO - Network:

def load_excel_from_network(file_path):
    #### [ check connection
    def check_internet_connection():
        try:
            # Attempt to connect to Google's DNS resolver
            # socket.create_connection(("www.google.com", 80))
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return False
        except OSError:
            pass
        return True
    if check_internet_connection():
        pass
    else:
        messagebox.showerror("Error", "Please disconnect from internet")
        return None
    #### ]

    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print("File not found.")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"Error: {str(e)}")

# The directory of the source excel:
file_path = r"\\fileserver3\Inventory\1- Product Development\10- IPCO data Lake\1-Data Loggers\___Admin___"
logger_status_excel = file_path + "\DashBoard_Source.xlsx"

# The directory of the data:
file_path = r"\\fileserver3\Inventory\1- Product Development\10- IPCO data Lake\1-Data Loggers"


df = load_excel_from_network(logger_status_excel)
#print(df)

if df is None:
   sys.exit()
#    print(df.head())


shape1 = df.shape
#print(shape1[0])
# remove duplicate values in ProductID column
df = df.drop_duplicates(subset=['Code'], keep='first')
shape2 = df.shape
#print(shape2[0])
if (abs(shape1[0] - shape2[0]) !=0 ):
    print("There are duplicate objects",str(abs(shape1[0] - shape2[0])),"objects has been deleted!")

# Reading the excel containing datalake information
# df = pd.read_excel('DashBoard_Source.xlsx')
df = df.to_numpy()
#============================================
# OOP 
class new_featurtes:
    # x1 = df
    # x2 = path
    def __init__(self,x1,x2):
        self.x1 = x1
        self.x2 = x2

    # Size function
    def Size(self):
        size_mat = np.zeros((len(self.x1),1))    

        for i in range (0,len(self.x1)):
            total_size = 0
            start_path = self.x2+'\\'+self.x1[i][0]
            for path, dirs, files in os.walk(start_path):
                for f in files:
                    fp = os.path.join(path, f)
                    total_size += os.path.getsize(fp)
            size_mat[i] = total_size / 1e+06  # Unit:MB

        return(size_mat)    
        
calc = new_featurtes(df,file_path)
files_size = calc.Size()
#print(files_size)


user_list = []
for i in range(0,len(df)):
    user_list = user_list + [df[i][14]]

user_list = np.unique(user_list)
#print(user_list)

user_size_list = np.zeros((len(user_list),1))
#print(user_size_list)

for i in range(0,len(df)):
    for j in range(0,len(user_list)):
        if df[i][14] == user_list[j]:
            user_size_list[j][0] = user_size_list[j][0] + files_size[i][0]
            break

#print(user_size_list)

output1 = np.sum(files_size,axis=0)
output2 = np.sum(user_size_list,axis=0)
#print(output1)
#print(output2)

if abs(output1 - output2) < 1e-04:
    print("All files size has been correctly calculated!")
else:
    print("Error!, Check the size calculation, line 62 & 63 ")


for i in range(0,len(user_size_list)):
    user_size_list[i][0] = user_size_list[i][0]/1000    # MB to GB   



user_size_list = np.transpose(user_size_list) 

#============================================
# Plots: 
for i in range(0,len(user_list)):
    a = user_list[i]
    a = a[::-1]
    user_list[i] = a


FigNum = FigNum + 1
plt.figure(FigNum)
plt.bar(user_list, user_size_list[0], color ='dimgrey',width = 0.75)
plt.xticks(rotation=50)
#plt.xlabel("Drivers",labelpad=20)
plt.ylabel("Data size (GB)",labelpad=30,fontsize=14)
param = float(f'{(output1[0])/1000:.2f}')
plt.title("Total Data Size is" + "  " + str(param) + "  GB", color="deeppink",fontsize=22)
plt.grid(axis = 'y',color = 'black', linestyle = '--', linewidth = 0.5)
plt.show()

for i in range(0,len(user_list)):
    a = user_list[i]
    a = a[::-1]
    user_list[i] = a
    
#============================================
# Output Excel
column1 = []
for i in range(0,len(user_list)):
    column1 = column1 + [user_list[i]]

column2 = []
for i in range(0,len(user_list)):
    column2 = column2 + [float (user_size_list[0][i])]


Output_matrix1 = np.array([column1])
Output_matrix2 = np.array([column2])
Output_matrix1 = np.transpose(Output_matrix1)
Output_matrix2 = np.transpose(Output_matrix2)

Output_matrix1 = pd.DataFrame(Output_matrix1,columns=["Users"])
Output_matrix2 = pd.DataFrame(Output_matrix2,columns=["Size"])

Output_matrix = pd.concat([Output_matrix1, Output_matrix2], axis=1)
#print(Output_matrix)

Output_matrix.to_excel('Output_matrix.xlsx')

