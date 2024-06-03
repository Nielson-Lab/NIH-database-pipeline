# This repository was developed with funding from the National Institute of Mental Health (NIMH),
# grant # 1R01MH116156 awarded to Dr. Jessica L. Nielson, PhD at the University of Minnesota.
# ©2024 Regents of the University of Minnesota. All rights reserved.

# This repository is open source and available under Attribution-NonCommercial-NoDerivatives (CC BY-NC-SA):
# (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

#!/bin/bash

pyinstaller -w -D -n NFP \
  --paths=/Users/kirsh012/NFpipeline/venv/lib/python3.8/site-packages \
  --add-data="templates:templates" \
  --add-data="database:database" \
  --add-data="static:static" \
  --hidden-import=gevent \
  --hidden-import=flask \
  --hidden-import=dash \
  --hidden-import=dash_core_components \
  --hidden-import=pkg_resources.py2_warn \
  run_gevent.py -y
