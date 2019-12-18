from re import *

raw = open('words', 'r').read()

data = findall(r'[a-z]+', raw)

for item in sorted(data):
    print '<entry pos="V" word="' + item + '" macros="@pres @non-3rd @sg"/>'
