#!/usr/bin/env python
import os
import sys
from fnmatch import fnmatch, fnmatchcase

VERSION_TEXT = """find (GNU findutils) 4.7.0 Copyright (C) 2019
Free Software Foundation, Inc.License GPLv3+: 
GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
            
Written by Adelina-Alicia Mihai."""

HELP_TEXT = """ Usage: find.py [path...] [expression]

default path is the current directory; default expression is -print
expression may consist of: operators, options, tests, and actions:
     
normal options: (always true, specified before other expressions):
      --help 
      --version 
      
tests: 
      -iname PATTERN
      -name PATTERN
      -type [df]
      -empty
      
actions:
      -print
      -quit
"""
# arg suportate
NUMBER_OF_PARAMS = {
    '-help': 0,
    '-version': 0,

    '-iname': 1,
    '-name': 1,
    '-type': 1,
    '-empty': 0,

    '-print': 0,
    '-quit': 0,
}
#creaza o lista din cheile dictionarului
SUPPORTED_ARGS = NUMBER_OF_PARAMS.keys()

def findByPathAndTests(path=".", name="*", type=None, iname="*", stopAfterPrint=False, printOnlyEmpty=False):
    # verificam ca path ul exista
    if not os.path.exists(path):
        print("find.py:", path, ": No such file or directory")
        return

    # if type is set split it into the allowed type options
    types = []
    if type is not None:
        types = type.split(',')
        for type in types:
            if type not in ['f', 'd']:
                print("find.py: Unknown argument to -type: ", type)
                return

    # pt ca iname e case sensitive il facem lowercase sa nu l facem de fiecare data in for
    iname = iname.lower()

    for root, dirs, files in os.walk(path):

        directoryName = root.split(os.sep)[-1]
        # este permis ca -name si -iname sa fie in acelasi timp setate
        if fnmatchcase(directoryName, name) and fnmatch(directoryName.lower(), iname):
            # verific pt comanda empty daca folderul e gol
            # sau nu am cerut sa fie printat onlyEmpty sau e Empty
            if not printOnlyEmpty or len(os.listdir(root)) == 0:
                # afisez directorul daca n avem type sau avem d printre tupurile setate
                if type is None or 'd' in types:
                    print (root)
                    if stopAfterPrint:
                        return


        if type is None or 'f' in types:
            for fileName in files:
                # Daca numele fisierului corespunde cu expresia indicata
                # este permis ca -name si -iname sa fie in acelasi timp setate
                if fnmatchcase(fileName, name) and fnmatch(fileName.lower(), iname):
                    # verific pt comanda empty daca fisierul e gol
                    # sau nu am cerut sa fie printat onlyEmpty sau e Empty
                    filePath = os.path.join(root, fileName)
                    if not printOnlyEmpty or os.stat(filePath).st_size == 0:
                        print(filePath)
                        if stopAfterPrint:
                            return

def extractArgumentValue(commandArguments, argumentName, defaultValue):
    # cautam argumentul argumentName(eg "-name") si valoarea asociata lui
    try:
        argumentIndex = commandArguments.index(argumentName)
    except ValueError:
        # comanda nu contine argumentul argumentName
        return defaultValue

    if argumentIndex >= 0:
        if len(commandArguments) <= argumentIndex + 1:
            print("find: missing argument to '" + argumentName + "'")
            raise ValueError("missing argument")
        # caz de eroare pentru mai mult de 2 parametri
        elif len(commandArguments) >= argumentIndex + 3 and commandArguments[argumentIndex + 2] not in SUPPORTED_ARGS:
            print("find: paths must precede expression:", commandArguments[argumentIndex + 2])
            raise ValueError("paths must precede expression")
        # in cazul in care un numar corect de parametri
        else:
            return commandArguments[argumentIndex + 1]

def executeFindCommand(commandArguments):
    if len(commandArguments) == 0:
        # fara parametrii cauta toate fisierele din radacina sist de operare nu din path ul la care sunt
        findByPathAndTests()
        return

    path = '.'
    try:
        name = extractArgumentValue(commandArguments, '-name', defaultValue="*")
        type = extractArgumentValue(commandArguments, '-type', defaultValue=None)
        iname = extractArgumentValue(commandArguments, '-iname', defaultValue="*")
    except ValueError:
        # format for arguments is invalid
        return

    indexPredicateValidationStart = 0
    if commandArguments[0][0] != '-':
        # listez toate fisierele din path ul trimis ca argument
        path = commandArguments[0]
        indexPredicateValidationStart = 1
    i = indexPredicateValidationStart
    while i < len(commandArguments):
        if commandArguments[i] not in SUPPORTED_ARGS:
            print("find.py: Unknown predicate '" + commandArguments[i] + "'")
            return
        i = i + NUMBER_OF_PARAMS[commandArguments[i]] + 1

    stopAfterPrint = False
    if '-quit' in commandArguments:
        # daca avem doar -quit trebuie doar sa ne oprim
        if '-print' not in commandArguments:
            return
        # daca avem doar -quit dar si -print trebuie sa afisam numai primul rezultat
        else:
            stopAfterPrint = True

    if '-version' in commandArguments:
        print(VERSION_TEXT)
        return

    if '-help' in commandArguments:
        print(HELP_TEXT)
        return

    printOnlyEmpty = False
    if '-empty' in commandArguments:
        printOnlyEmpty = True

    findByPathAndTests(path,
                       name=name,
                       type=type,
                       iname=iname,
                       stopAfterPrint=stopAfterPrint,
                       printOnlyEmpty=printOnlyEmpty)



if __name__ == "__main__":

    # iau toate valorile din lista ignorand o pe cea de pozitia 0
    commandArguments = sys.argv[1:]
    # print(commandArguments)
    executeFindCommand(commandArguments)