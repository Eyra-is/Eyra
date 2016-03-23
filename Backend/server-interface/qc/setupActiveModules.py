import re
import sys
import os

import config # grab the names/tasks of the active modules

FILENAME = 'celery_handler.py'
TEMPLATENAME = 'TestModule'
TEMPLATETASK = 'TestTask'

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
        processTemplate = re.sub(r'\n# ', '\n', processTemplate) # remove commenting

        processTasks = '' # the entire code of all the tasks to be placed between
                          # @@CELERYQCPROCESSTASKS markers
        baseTaskImports = '' # same as processTasks for @@CELERYQCBASETASKIMPORTS
        for k, module in config.activeModules.items():
            processingFn = re.sub(TEMPLATENAME, module['name'], processTemplate)
            processingFn = re.sub(TEMPLATETASK, module['task'], processingFn)
            processTasks += processingFn + '\n\n'

            baseTaskImports += 'from .modules.%s import %s' % (module['name'], module['task']) + '\n'
     
        content = re.sub(r'# @@CELERYQCBASETASKIMPORTS(.*)# @@/CELERYQCBASETASKIMPORTS', 
            '# @@CELERYQCBASETASKIMPORTS\n%s# @@/CELERYQCBASETASKIMPORTS' % baseTaskImports,
            content,
            flags=re.DOTALL)
        content = re.sub(r'# @@CELERYQCPROCESSTASKS(.*)# @@/CELERYQCPROCESSTASKS', 
            '# @@CELERYQCPROCESSTASKS%s# @@/CELERYQCPROCESSTASKS' % processTasks,
            content,
            flags=re.DOTALL)

        with open(FILENAME+'.temp', 'w', encoding='utf8') as g:
            g.write(content)

        # now delete the .py file and rename our .temp into .py
        os.remove(FILENAME)
        os.rename(FILENAME+'.temp', FILENAME)

def run():
    if len(sys.argv) < 1:
        print( 
"Usage:\
   %s\n\n\
   Only needed to call if activeModules in config.py is updated.\
   Generates code needed for QC depending on active modules.\
   Modifies files: celery_handler.py\
   Places modified are marked with '\# @@CELERYMOD' at start and\
   '# @@/CELERYMOD' at the end on their own lines." % sys.argv[0]
        )
        return
    else:
        process()

if __name__ == '__main__':
    run()