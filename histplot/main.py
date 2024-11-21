import sys, os
path = sys.path.insert(1, os.path.abspath(os.path.join(os.path.join(__file__, os.pardir), os.pardir)))

from histplot import Start
Start()