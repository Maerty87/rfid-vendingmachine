#Written for Python3
#This code is intented to catch transactions that could'nt be sent to the DB
#and send them as soon as it is possible
import dbHandler


spoolCache = []
def catch(query = ()):
	spoolCache.append(query)
	with open("spool.spl","a") as writefile:
		writefile.writeln(query)
		writefile.close()
		
	
def showCache():
	counter = 0
	for entry in spoolCache:
		print(f"[{counter}] {entry}")
		counter += 1

def releaseAll():
	for entry in spoolCache:
		buyDrink(entry[0],entry[1], entry[2])
	print("All Queries have been sent.")
