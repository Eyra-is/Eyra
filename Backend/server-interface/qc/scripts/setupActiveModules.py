# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Matthias Petursson <oldschool01123@gmail.com>

import re
import sys
import os

# mv one up from qc/script directory and do relative imports from there.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(newPath)
import config # grab the names/tasks of the active modules
sys.path.remove(newPath)
del newPath

FILENAME = '../celery_handler.py'
TEMPLATENAME = 'MarosijoModule'
TEMPLATETASK = 'MarosijoTask'

def process():
    """
    Modifies celery_handler.py file to account for activeModules in config.py

    Use the template for the processing function which should be located
      between # @@CELERYQCPROCESSTEMPLATE and # @@/ CELERYQCPROCESSTEMPLATE tags in
      celery_handler.py.
      And generates necessary imports from modules/ between the 
      @@CELERYQCBASETASKIMPORTS tags
      and generates the necessary processing functions from the template by using simple 
      text replace (XModule -> MyModule1, MyModule2, etc.) and places 
      between the @@CELERYQCPROCESSTASKS tags
    """
    with open(FILENAME, 'r', encoding='utf8') as f:
        content = f.read()
        processTemplate = re.findall('# @@CELERYQCPROCESSTEMPLATE(.*)# @@/CELERYQCPROCESSTEMPLATE', 
            content, 
            re.S)
        if len(processTemplate) != 1:
            print("Error, didn't find match for # @@CELERYQCPROCESSTEMPLATE")
            return
        processTemplate = processTemplate[0]
        # remove commenting
        processTemplate = logReSubn(re.subn(r'\n# ', '\n', processTemplate),
                            'Removing # from template.', '# removed (expecting > 1).', '')

        processTasks = '' # the entire code of all the tasks to be placed between
                          # @@CELERYQCPROCESSTASKS markers
        baseTaskImports = '' # same as processTasks for @@CELERYQCBASETASKIMPORTS
        for k, module in config.activeModules.items():
            processingFn = logReSubn(
                re.subn(TEMPLATENAME, module['name'], processTemplate),
                'Replacing %s.' % module['name'],
                '%s replaced. (expecting 5)' % module['name'],
                'Error, couldn\'t find %s in code.' % module['name'])
            processingFn = logReSubn(
                re.subn(TEMPLATETASK, module['task'], processingFn),
                'Replacing %s.' % module['task'],
                '%s replaced. (expecting 1)' % module['task'],
                'Error, couldn\'t find %s in code.' % module['task'])
            processTasks += processingFn + '\n\n'

            baseTaskImports += 'from .modules.%s.%s import %s' \
                               % (module['name'], module['name'], module['task']) + '\n'
     
        content = logReSubn(
            re.subn(r'# @@CELERYQCBASETASKIMPORTS(.*)# @@/CELERYQCBASETASKIMPORTS', 
                '# @@CELERYQCBASETASKIMPORTS\n%s# @@/CELERYQCBASETASKIMPORTS' % baseTaskImports,
                content,
                flags=re.DOTALL),
            'Replacing # @@...TASKIMPORTS',
            '# @@...TASKIMPORTS replaced. (expecting 1)',
            'Error, no # @@...TASKIMPORTS found, should be 1.')
        content = logReSubn(
            re.subn(r'# @@CELERYQCPROCESSTASKS(.*)# @@/CELERYQCPROCESSTASKS', 
                '# @@CELERYQCPROCESSTASKS%s# @@/CELERYQCPROCESSTASKS' % processTasks,
                content,
                flags=re.DOTALL),
            'Replacing # @@...PROCESSTASKS',
            '# @@...PROCESSTASKS replaced. (expecting 1)',
            'Error, no # @@...PROCESSTASKS found, should be 1.')

        print('Updating file %s.' % FILENAME)
        # write our new FILENAME to a temp file, which will then replace the original
        with open(FILENAME+'.temp', 'w', encoding='utf8') as g:
            g.write(content)

        # now delete the .py file and rename our .temp into .py
        os.remove(FILENAME)
        os.rename(FILENAME+'.temp', FILENAME)
        print('File modified.')

def logReSubn(subnExpr, preComment, postComment, errorMsg='') -> str:
    """
    Takes in the result of a re.subn call, subnExpr, and
    logs preComment to stdout, then logs postComment and specifies the
    number of subs.
    Prints errorMsg in case of 0 subs.

    Returns the string from subnExpr with replacements made.
    """
    out = subnExpr[0]
    subs = subnExpr[1]
    print(preComment)
    print(str(subs) + ' ' + postComment)
    if (subs == 0 and errorMsg != ''):
        print(errorMsg)
    return out



def run():
    if len(sys.argv) != 1:
        print( 
"Usage:\
   python3 %s\n\n\
   Only needed to call if activeModules in config.py is updated.\n\
   Generates code needed for QC depending on active modules.\n\
   Modifies files: celery_handler.py\n\
   Places modified are marked with '\# @@CELERYMOD' at start and\n\
   '# @@/CELERYMOD' at the end on their own lines.\n" % sys.argv[0]
        )
        return
    else:
        process()

if __name__ == '__main__':
    run()