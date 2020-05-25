# Ensemble Generator

Functions for generating and analysing ensembles of geological models.

## Dependencies

- python>3.6
- map2loop

## Install

To install the 'egen' python package locally, clone this repo and navigate into it. Then run the following in a terminal.

```bash
pip install -e .
```

## Docker Dev Environment

To develop and test egen inside a dedicated loop environment, follow the instructions in this [repo](https://github.com/Loop3D/map2loop-2/).

### Known Issues

- egen_config from the master branch was removed because it had Jupyter conventions and hardcoded paths. Some of the other test files still contain absolute paths as well and this no bueno.
- The notebooks have been moved out of the source directory into their own so may cause minor issues.

### References