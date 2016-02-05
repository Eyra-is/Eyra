
# Usage: python tokens_to_sql.py src dest 
#
# turns tokens in src, 1 on each line, into sql ready to be run and placed into database
#
# Example: run on 'go
#                  get
#                  some
#                  pie' 
#              -> 'insert into token (inputToken)
#                  values
#                  ('go'),
#                  ('get'),
#                  ('some'),
#                  ('pie');'

import sys

def process(src, dest):
    with open(src, 'r', encoding='utf8') as f:
        text = f.read().splitlines()
        with open(dest, 'w', encoding='utf8') as g:
            g.write('insert into token (inputToken)\nvalues\n')
            for i, t in enumerate(text):
                if (i == len(text) - 1):
                    g.write('(\''+t+'\');')
                else:
                    g.write('(\''+t+'\'),\n')

def run():
    if len(sys.argv) < 3:
        print( 
'Usage: python %s src dest\n\
Description: Creates sql from src ready to be put into a token ' % sys.argv[0]
+
'table, src being tokens 1 on each line.\
' 
             )
        return
    else:
        process(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    run()