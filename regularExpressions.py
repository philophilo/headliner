'''
IDENTIFIERS
\d any number
\D anything but a number
\s space
\S anything but space
\w any character
\W anything but a character
. any character, except for a new line
\b the whitespace around words
\. a period


MODIFIERS
{1,3} we are expecting 1-3
+ Match 1 or more
? Match 0 or 1
* Match 0 or more
$ match the end of a string
^ match the beginning of a string
| either or
[] range or "variance"
{x} expecting "x" amount

WHITESPACE CHARACTERS
\n new line
\s space
\t tab
\e escape
\f form feed
\r return

DONT FORGET
. + * ? [ ] $ ^ ( ) { } | \
'''


import re

exampleString = '''
Jessica is 15 years old and Daniel is 27 years old.
Edward is 97, and his grandfather, Oscar is 120.
'''

ages = re.findall(r'\d{1,3}', exampleString)
names = re.findall(r'[A-Z][a-z]*', exampleString)

print ages
print names

x = 0
ageDict = {}
for eachName in names:
    ageDict[eachName] = age[x]
    x+=1


print names
