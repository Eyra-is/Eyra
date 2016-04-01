# util functions at the disposal of QC modules
import MySQLdb

# grab dbConst from db_handler from 2 dirs above this one
# thanks, Alex Martelli, http://stackoverflow.com/a/1054293/5272567
import sys
import os.path
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.append(newPath)
from config import dbConst # grab data needed to connect to database
sys.path.remove(newPath)
del newPath

class DbWork():
    def __init__(self):
        self.db = MySQLdb.connect(**dbConst)

    def verifyTokenId(self, tokenId, token):
            """
            Accepts a token id and token and verifies this id
            is correct (comparing to the token in database and its id)

            Parameters:

                tokenId     id of token
                token       token text
            """
            try:
                cur = self.db.cursor()
                cur.execute('SELECT inputToken FROM token WHERE id=%s', (tokenId,))
                tokenFromDb = cur.fetchone()
                if tokenFromDb:
                    tokenFromDb = tokenFromDb[0] # fetchone returns tuple
                    if tokenFromDb == token:
                        return True
                    return False
                return False
            except MySQLdb.Error as e:
                msg = 'Error verifying token id, %d : %s' % (tokenId, token) 
                log(msg, e)
                raise
            else:
                return False