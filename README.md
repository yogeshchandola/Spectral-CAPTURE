# Spectral-CAPTURE
This pipeline is adapted for spectral line data reduction from the CAPTURE continuum data reduction pipeline for uGMRT (https://github.com/ruta-k/uGMRT-pipeline) developed by Ruta Kale and Ishwar Chandra.
This pipeline is based on modular CASA 6 package which can be installed in a virtual python environment. Using modular CASA 6 makes this pipeline more flexible than original CAPTURE pipeline.
The method to install modular CASA is described in detail in the link 
https://casadocs.readthedocs.io/en/v6.2.0/notebooks/usingcasa.html.


Before running the script, appropriate parameters should be set using the parameter file 'config_example.ini'. Also, because flagging is done using the AOFLAGGER (https://aoflagger.readthedocs.io/en/latest/) for certain steps, it should be installed beforehand.
After the casa6 environment is activated, the script casascriptnew.py can be run on python. 


