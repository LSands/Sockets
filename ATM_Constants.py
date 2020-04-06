FAILED = -1
PASSED = 0
# Screen selection codes
DEBIT = 1       # get cash
CREDIT = 2      # make deposit
TRANSFER = 3    # transfer funds
#
LF = "\n"       #line feed
PIN_LENGTH = 4
CARD_LENGTH = 8
# Transaction codes
MESSAGE_ID = 'MESSAGE_ID'   # XML tree element
STOP_APP = 'STOP_APP'       # terminate the application
TEST_MESSAGE = 'TEST_MESSAGE'
MESSAGE_NOT_FOUND = 'MESSAGE_NOT_FOUND'
VALIDATE_PIN = 'VALIDATE_PIN'
GET_CASH = 'GET_CASH'
DEPOSIT_FUNDS = 'DEPOSIT_FUNDS'
TRANSFER_FUNDS = 'TRANSFER_FUNDS'
BALANCE_INQUIRY = 'BALANCE_INQUIRY'
ACCOUNT_SUMMARY = 'ACCOUNT_SUMMARY'
# XML elements
XML_MESSAGE_ID = 'MESSAGE_ID'
XML_CUST_NAME = 'XML_CUST_NAME'
XML_CUST_NBR = 'XML_CUST_NBR'
XML_CARD_NBR = 'CARD_NBR'
XML_CARD_PIN = 'CARD_PIN'
XML_ACCT_NBR = 'ACCT_NBR'     
XML_FROM_ACCT_NBR = 'FROM_ACCT_NBR'     #also use as the account number for BI, Deposit, Withdrawl
XML_TO_ACCT_NBR = 'TO_ACCT_NBR'
XML_AMOUNT = 'AMOUNT'
XML_ACCT_BAL = 'ACCT_BAL'
XML_ACCT_TYPE = 'ACCT_TYPE'
XML_ACCT_NAME = 'ACCT_NAME'
XML_ACCT_COLLECTION = 'ACCOUNT_COLLECTION'  #this is for grouping child elements in the XML message
XML_TEXT = 'XM_TEXT'        # miscellaneous text
#
