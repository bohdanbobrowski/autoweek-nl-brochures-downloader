#!/usr/bin/env python

import os
import re

from os import listdir
from os.path import isfile, join

brochures = []

for f in listdir('./'):
    if isfile(join('./', f)):
        x = re.findall('brochure[0-9]+_([^-]+)-([^\.]+)\.pdf', f) 
        if len(x) == 1:
            directory = './'+str(x[0][0])+'/' 
            if not os.path.exists(directory):
                os.makedirs(directory)
            os.rename(join('./', f), join(directory, f))
            print f,'->',directory+f
