# mCAPTURE
modified CAPTURE pipeline for GMRT data reduction
This pipeline is adapted from the CAPTURE data reduction pipeline for GMRT.
This pipeline is based on modular CASA package which can be installed in a virtual python environment for 
which the method is described in detail in the link https://casadocs.readthedocs.io/en/stable/notebooks/introduction.html#Modular-Packages
We give a short description of installing modular CASA packages as below.

Pip wheels for casatools and casatasks are available as Python 3 modules. This allows simple installation and import into standard Python environments. The casatools wheel is necessarily a binary wheel so there may be some compatibility issues for some time as we work toward making wheels available for important Python configurations.

Make sure you have set up your machine with the necessary prerequisite libraries first. Then a la carte installation of desired modules (from a Linux terminal window) as follows:

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


After the virtual environment is created, it can be activated in the command line by typing

source myenv/bin/activate

After the casa6 environment is activated, you can run the file 


