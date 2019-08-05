# Matching_method

- [Install](#install) 
- [Structure](#structure)
- [Run](#run)

## Install

This will install all the dependencies in the Pipefile by ***Pipenv***

```console
$ pipenv install
```

## Structure

    matching_method/
        ├── edge/                   # Class of "Edge" 
        ├── fog_set/                # Class of "Fog_set", "Fog"      
        ├── constant/               # Class of "Constant"
        ├── m_m_c/                  # Simulation for M/M/c
        ├── pso_settings/           # Parameters in pyswarm 
        ├── distribution/           # Simulation for uniform and exponential distribution 
        ├── script/                 # Execution file in different scenarios
        ├── testcase/               # Input test file
        ├── graph/                  # Output graph 
        └── main.py                 # Original version

## Run

```console
$ pipenv run python {name.py}
```