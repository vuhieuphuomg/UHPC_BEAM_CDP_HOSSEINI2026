# Python 2.7-compatible environment probe. Invoke via `abaqus python ...`.
from __future__ import print_function
import sys, platform
print('Python:',sys.version)
print('Platform:',platform.platform())
try:
 import odbAccess
 print('odbAccess: AVAILABLE')
except Exception as exc:
 print('odbAccess: NOT_AVAILABLE',str(exc))
try:
 from abaqusConstants import ON
 print('abaqusConstants: AVAILABLE')
except Exception as exc:
 print('abaqusConstants: NOT_AVAILABLE',str(exc))
