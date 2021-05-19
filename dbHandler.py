#Written for Python3
#This code is responsible for connecting, fetching and committing data
#to the mariaDB. 

import mariadb
import spooler
import configReader
config = configReader.parseFile("db")

err = None

def isError():
	global err
	return err
try:
	conn = mariadb.connect(
				host=config["dbHost"],
				port=int(config["dbPort"]),
				user=config["dbUser"],
				password=config["dbPassword"],
				database=config["dbDatabase"]
				)
	cur = conn.cursor()
	
except mariadb.Error as error:
	print ("Error conntecting to MariaDB.")
	err = error
	print (err)
	
def setLimitForUser(userID,limit):
	try:
		cur.execute(f"UPDATE mitarbeiter SET INFO={limit} WHERE ID={userID};")
		conn.commit()
		print(f"LIMIT {limit}€ updated for mitarbeiter id {userID}")
	except mariadb.Error as error:
		global err
		err = error
		return err
		
def fetchAllCustomers():
	try:
		cur.execute("SELECT NACHNAME, VORNAME, RFID, ID, INFO FROM mitarbeiter;")
		tmpLst = []
		print("All customers fetched")
		for entry in cur:
			tmpLst.append(entry)
		return tmpLst
	except mariadb.Error as error:
		global err
		err = error
		return err

def setRFID(rfidKey,userID):
	try:
		cur.execute(f"UPDATE mitarbeiter SET RFID='{rfidKey}' WHERE ID={userID};")
		conn.commit()
	except mariadb.Error as error:
		global err
		err = error
		print(err)
		return err
		
def fetchRfid(rfidKey):
	try:
		cur.execute(f"SELECT ID FROM mitarbeiter WHERE RFID='{rfidKey}';")
		tmpID = ()
		for entry in cur:
			tmpID = entry
		return tmpID[0]
		
		return tmpID
		
	except mariadb.Error as error:
		global err
		err = error
		return err
		
def fetchAllDrinks():
		try:
			cur.execute("SELECT g.ID, p.ID, g.Name, p.WERT FROM getraenke g LEFT JOIN preise p ON p.ID = g.PREIS WHERE g.ANGEBOT = 1;")
			tmpLst = []
			print("All drinks fetched")
			for entry in cur:
				tmpLst.append(entry)
			return tmpLst
		except mariadb.Error as error:
			global err
			err = error
			return err
			
def fetchSingleDrink(drinkName):
	try:
		cur.execute(f"SELECT ID FROM getraenke WHERE NAME='{drinkName}';")
		tmpID = ()
		for entry in cur:
			tmpID = entry
		print("rofl")
		return tmpID[0]
	except mariadb.Error as error:
			global err
			err = error
			return err
					
def buyDrink(rfidKey, drinkID, priceID):
		
		try:
			customerID = int(fetchRfid(rfidKey))
			q = (customerID, drinkID, priceID)
			cur.execute(f"INSERT INTO `kaeufe` (MITARBEITER, GETRAENK, PREISID) VALUES ({customerID},{drinkID},{priceID}) ")
			
			conn.commit()
			print("Kauf erfolgreich")
		except mariadb.Error as error:
			global err
			err = error
			return err

def terminateConnection():
	conn.close()
