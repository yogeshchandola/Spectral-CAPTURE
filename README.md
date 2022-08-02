# Spectral-CAPTURE
This pipeline is adapted for spectral line data reduction from the CAPTURE continuum data reduction pipeline for uGMRT (https://github.com/ruta-k/uGMRT-pipeline) developed by Ruta Kale and Ishwar Chandra.
This pipeline is based on modular CASA 6 package which can be installed in a virtual python environment. Using modular CASA 6 makes this pipeline more flexible than original CAPTURE pipeline.
The method to install modular CASA is described in detail in the link https://casadocs.readthedocs.io/en/stable/notebooks/introduction.html#Modular-Packages.
A short description of steps for installing modular CASA 6 packages is given below.


$: python3 -m venv myvenv

$: source myvenv/bin/activate

(myvenv) $: pip install --upgrade pip wheel

Now pick whichever subset of the available CASA packages you are interested in. Package dependencies are handled automatically by pip, with the exception of casadata which must be explicitly installed and updated by the user (see External Data). The following packages are available:

(myvenv) $: pip install casatools==6.5.1.23

(myvenv) $: pip install casatasks==6.5.1.23

(myvenv) $: pip install casaplotms==1.7.3

(myvenv) $: pip install casaviewer==1.5.2

(myvenv) $: pip install casampi==0.5.0

(myvenv) $: pip install casashell==6.5.1.23

(myvenv) $: pip install casadata==2022.7.18

(myvenv) $: pip install casaplotserver==1.2.1

(myvenv) $: pip install almatasks==1.5.2

(myvenv) $: pip install casatestutils==6.5.1.23

Before running the script, appropriate parameters should be set using the parameter file 'config_example.ini'. Also, because flagging is done using the AOFLAGGER (https://aoflagger.readthedocs.io/en/latest/) for certain steps, it should be installed beforehand.
After the casa6 environment is activated, the script casascriptnew.py can be run on python. 


