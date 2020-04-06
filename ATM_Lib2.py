from ATM_Constants import *
from ATM_XML import *
from ATM_Classes import *
import xml.dom.minidom
from lxml import etree 
import configparser
import mysql.connector
from mysql.connector import Error

my_debug2 = True    #debug print flag

############################################
# This library is for server-side functions
############################################
# Get database configuration info
# pull from config file using 'get_server_config_value'
mySQL_Host = 'localhost'
mySQL_UserName = 'root'
mySQL_Password = 'secret'
mySQL_Database = 'bank' 

############################################
## Get value from client_config.ini
############################################
def get_server_config_value(section_name, key_name, value_name):
    parser = configparser.ConfigParser()
    parser.read('.\\server_config.ini') 
    if section_name == '':      # setup default
        section_name = 'setup'
    try:
        key_value = parser[section_name][key_name]
    except:
        key_value = None
        rc = FAILED      # set return code to False/fail
    else:
        rc = PASSED
        if my_debug1:
            print('* ', __name__)
            print('section=',parser.sections())
            print('key_name=', key_name)
            print('key_value=', key_value)
    return rc
############################################
# RESPONSE: TestConnection_resp
# server side routine to test the tcp/ip connection
# Input: none
# Output: response message
############################################
def TestConnection_resp():
    # build XML response message
    xmlmessage = etree.Element(MESSAGE_ID)     #root message type
    xmlmessage.text = TEST_MESSAGE

    content = etree.SubElement(xmlmessage, XML_TEXT)
    content.text = 'Test Connection Successful'
    xmlmessage.append(content)

    if my_debug2:
        print('* XML_TestConnection_resp:')
        etree.dump(xmlmessage)
    # convert xml tree to a string
    return etree.tostring(xmlmessage, encoding='UTF-8', method='xml')
############################################
# RESPONSE: message_not_found
# server side routine 
# Input: none
# Output: response message
############################################
def stop_server():
    # build XML response message
    xmlmessage = etree.Element(MESSAGE_ID)     #root message type
    xmlmessage.text = STOP_APP

    content = etree.SubElement(xmlmessage, XML_TEXT)
    content.text = 'STOP Server issued'
    xmlmessage.append(content)

    # convert xml tree to a string
    return etree.tostring(xmlmessage, encoding='UTF-8', method='xml')
############################################
# RESPONSE: message_not_found
# server side routine 
# Input: none
# Output: response message
############################################
def message_not_found():
    # build XML response message
    xmlmessage = etree.Element(MESSAGE_ID)     #root message type
    xmlmessage.text = MESSAGE_NOT_FOUND

    # convert xml tree to a string
    return etree.tostring(xmlmessage, encoding='UTF-8', method='xml')
############################################
# RESPONSE: ValidatePIN
# server side routine to build the message
# Input:
#   mycursor = pointer to database
#   card_nbr = INT
#   card_PIN = CHAR(4)
#   cust_data = pointer to customer data of type customer_class
# Output:
#   xmlmessage = message to be sent
############################################
def ValidatePIN_resp(xmlstring):
#def ValidatePIN_resp(mycursor, card_nbr, card_PIN, cust_data):
    
    cn = OpenDatabase()
    if cn == FAILED:
        return FAILED
    else:
        # the 'dictionary=True' is needed to read results by column name
        mycursor = cn.cursor(dictionary=True)
    
    # extract card_nbr, card_PIN from XML data
    card_nbr = getTagContent(xmlstring, XML_CARD_NBR)
    card_PIN = getTagContent(xmlstring, XML_CARD_PIN)

    if my_debug2:
        print('xmlstring=', xmlstring)
        print('card_nbr=',card_nbr)
        print('card_PIN=', card_PIN)

    rows = []
    cust_data = customer_class
    acct_data = []

    # Get account data & balance info for customer
    # **use a join with customer & account tables**
    sql = 'SELECT custName, custNbr, cardNbr, cardPIN \
        FROM customers \
        WHERE CardNbr=%s'
    values = (card_nbr)
    try:
        mycursor.execute(sql, (values,))    # note: must have a ',' after 'values'
    except Error as e:
        print(f"* ValidatePIN error thrown: {e}")
        return FAILED
    rows = mycursor.fetchall()

    if my_debug2:
        print('* ValidatePIN: returned accountNbr data:')
        for x in rows:
            print(x)

    for z in rows:
        cust_data.custName = z['custName'].strip()  # customer name
        cust_data.custNbr  = int(z['custNbr'])      # custNbr
        cust_data.cardNbr = int(z['cardNbr'])       # cardNbr
        cust_data.cardPIN = z['cardPIN'].strip()    # custPIN

    if my_debug2:
        print(" * ValidatePIN: cust_data: ", cust_data.custName, cust_data.custNbr, cust_data.cardNbr, cust_data.cardPIN)
    
    # validate the PIN
    if cust_data.cardPIN != card_PIN:
        return FAILED

    #build xml return stream
    acct_data = GetAccountData(card_nbr)
    
    #xmlmessage = XML_ValidatePIN_resp(cust_data, acct_data)
        # Add customer data to XML stream
    xmlmessage = etree.Element(MESSAGE_ID)     #root message type
    xmlmessage.text = VALIDATE_PIN

    content = etree.SubElement(xmlmessage, XML_CUST_NAME)
    content.text = cust_data.custName
    xmlmessage.append(content)
    
    content = etree.SubElement(xmlmessage, XML_CUST_NBR)
    content.text = str(cust_data.custNbr)
    xmlmessage.append(content)

    content = etree.SubElement(xmlmessage, XML_CARD_NBR)
    content.text = str(cust_data.cardNbr)
    xmlmessage.append(content)

    # Add account data to XML stream
    # loop through the account data and build the XML message
    # note: the text for XML_ACCT_COLLECTION must be done in 2 steps; can't do
    # a double assignment in one statement
    acct = etree.SubElement(xmlmessage, XML_ACCT_COLLECTION)
    for a in acct_data:
        etree.SubElement(acct, XML_FROM_ACCT_NBR).text = str(a.acctNumber)
        etree.SubElement(acct, XML_ACCT_TYPE).text = a.acctType
        etree.SubElement(acct, XML_ACCT_BAL).text = str(a.acctBalance) 
        etree.SubElement(acct, XML_ACCT_NAME).text = a.acctName
    
    if my_debug2:
        print('* ValidatePIN_resp XML message:')
        etree.dump(xmlmessage)

    return etree.tostring(xmlmessage, encoding='UTF-8', method='xml')             
############################################
# RESPONSE: build account summary message
# server side routine to build the message
# Input:
#   card_nbr = int
#   acct_data 
# Output:
#   xmlmessage = message to be sent
############################################
def BuildAccountSummary(xmlstring):
    
    acct_data = [] 
    
    # extract card_nbr, card_PIN from XML data
    card_nbr = getTagContent(xmlstring, XML_CARD_NBR)

    if my_debug2:
        print('* BuildAccountSummary: returned accountNbr data:')
        for x in acct_data:
            print(x)

    if my_debug2:
        for obj in acct_data:
            print(" * acct_data: ", obj.acctNumber, obj.acctType, obj.acctBalance, obj.acctName)
    
    # Build XML message
    xmlmessage = etree.Element(MESSAGE_ID)
    xmlmessage.text = ACCOUNT_SUMMARY

    # add card number
    xmlcard_nbr = etree.SubElement(xmlmessage, XML_CARD_NBR)
    xmlcard_nbr.text = str(card_nbr)
    
    # loop through the card data and build the XML message
    # note: the text for XML_ACCT_COLLECTION must be done in 2 steps; can't do
    # a double assignment in one statement
    acct = etree.SubElement(xmlmessage, XML_ACCT_COLLECTION)
    for a in acct_data:
        etree.SubElement(acct, XML_FROM_ACCT_NBR).text = str(a.acctNumber)
        etree.SubElement(acct, XML_ACCT_TYPE).text = a.acctType
        etree.SubElement(acct, XML_ACCT_BAL).text = str(a.acctBalance)
        etree.SubElement(acct, XML_ACCT_NAME).text = a.acctName

    if my_debug2:
        print('* BuildAccountSummary:')
        etree.dump(xmlmessage)

    return etree.tostring(xmlmessage, encoding='UTF-8', method='xml') 
############################################
# Get  account summary data
# server side routine to build the structure
# Input:
#   card_nbr = int
# Output:
#   acct_data = list of account_class data
############################################
def GetAccountData(card_nbr):
    #fetch the account data
    rows = []
    acct_data = [] 

    cn = OpenDatabase()
    if cn == FAILED:
        return FAILED
    else:
        # the 'dictionary=True' is needed to read the results by column name
        mycursor = cn.cursor(dictionary=True)

    # Get account data & balance info for customer
    # **use a join with customer & account tables**
    sql = 'SELECT \
        customers.cardNbr, \
        accounts.acctNbr, \
        accounts.acctType, \
        accounts.acctBalance, \
        accounts.acctName \
        FROM customers \
        INNER JOIN accounts ON customers.cardNbr = accounts.acctCardNbr \
        WHERE customers.cardNbr=%s'
    values = (card_nbr)
    try:
        mycursor.execute(sql, (values,))    # note: must have a ',' after 'values'
    except Error as e:
        print(f"* GetAccountData error thrown: {e}")
        return FAILED
    rows = mycursor.fetchall()

    if my_debug2:
        print('* GetAccountData: returned accountNbr data:')
        for x in rows:
            print(x)

    # extract account details in the collection
    for z in rows:
        acct_data.append(account_class(
            int(z["acctNbr"]),       # number
            z["acctType"].strip(),   # type
            float(z["acctBalance"]), # balance
            z["acctName"].strip()    # name
            ))

    if my_debug2:
        for obj in acct_data:
            print(" * acct_data: ", obj.acctNumber, obj.acctType, obj.acctBalance, obj.acctName)
    
    return acct_data
############################################
# RESPONSE: build balance inquiry message
############################################
def BuildBalanceInquiry(xmlstring): 

    rows = []
    acct_data = [] 

    # extract card_nbr, card_PIN from XML data
    card_nbr = getTagContent(xmlstring, XML_CARD_NBR)
    acct_nbr = getTagContent(xmlstring, XML_ACCT_NBR)

    cn = OpenDatabase()
    if cn == FAILED:
        return FAILED
    else:
        # the 'dictionary=True' is needed to read the results by column name
        mycursor = cn.cursor(dictionary=True)

    # Get account data & balance info for customer
    # **use a join with customer & account tables**
    sql = 'SELECT \
        customers.cardNbr, \
        accounts.acctNbr, \
        accounts.acctType, \
        accounts.acctBalance, \
        accounts.acctName \
        FROM customers \
        INNER JOIN accounts ON customers.cardNbr = accounts.acctCardNbr \
        WHERE customers.cardNbr=%s AND accounts.acctNbr=%s'
    values = (card_nbr, acct_nbr)
    try:
        mycursor.execute(sql, (values,))    # note: must have a ',' after 'values'
    except Error as e:
        print(f"* BuildBalanceInquiry error thrown: {e}")
        return FAILED
    rows = mycursor.fetchall()
    
    # extract account details in the collection
    for z in rows:
        acct_data.append(account_class(
            int(z["acctNbr"]),       # number
            z["acctType"].strip(),   # type
            float(z["acctBalance"]), # balance
            z["acctName"].strip()    # name
            ))

    # Build XML message
    xmlmessage = etree.Element(MESSAGE_ID)
    xmlmessage.text = BALANCE_INQUIRY

    # add card number
    xmlcard_nbr = etree.SubElement(xmlmessage, XML_CARD_NBR)
    xmlcard_nbr.text = str(card_nbr)
    
    # loop through the card data and build the XML message
    # note: the text for XML_ACCT_COLLECTION must be done in 2 steps; can't do
    # a double assignment in one statement
    acct = etree.SubElement(xmlmessage, XML_ACCT_COLLECTION)
    for a in acct_data:
        etree.SubElement(acct, XML_FROM_ACCT_NBR).text = str(a.acctNumber)
        etree.SubElement(acct, XML_ACCT_TYPE).text = a.acctType
        etree.SubElement(acct, XML_ACCT_BAL).text = str(a.acctBalance)
        etree.SubElement(acct, XML_ACCT_NAME).text = a.acctName

    if my_debug2:
        print('* BuildBalanceInquiry:')
        etree.dump(xmlmessage)

    return etree.tostring(xmlmessage, encoding='UTF-8', method='xml') 
############################################
# connect to the database
# returns cursor to the database
############################################
def OpenDatabase():
    """
    to call this function, use this code:
    import mysql.connector
    cn = OpenDatabase()
    mycursor = cn.cursor(dictionary=True)
    """
    config = {
        "user": mySQL_UserName,
        "password": mySQL_Password,
        "host": mySQL_Host,
        "database": mySQL_Database
    }
    try:
        c = mysql.connector.connect(**config)
        if my_debug2:
            print("Connection to MySQL successful")
        return c
    except Error as e:
        print (f"connection error: {e}" )
        return FAILED
"""
# example of how to call the routines
"""    
if __name__ == "__main__":
    xmldata = """\
    <MESSAGE_ID>VALIDATE_PIN
    <CARD_NBR>11</CARD_NBR>
    <CARD_PIN>1111</CARD_PIN>
    </MESSAGE_ID>
    """
    '''
    #mycursor = OpenDatabase()
    card_nbr=11
    card_PIN='1111'
    card_data = []  # create pointer for card data list
    acct_data = []  # create pointer for acct data list
    '''
    #mycursor = OpenDatabase()

    rc = ValidatePIN_resp(xmldata)
    #rc = BuildAccountSummary(mycursor, card_nbr, acct_data)
    # build the XML message
    #xmlmessage = XML_AccountSummary_resp(card_nbr, acct_data)
