# Analyzes of gene- and comorbidity-based diseasomes

## Installation

Download the repository.

```sh
git clone https://github.com/dbblumenthal/diseasomes
cd diseasomes
```

Install all dependencies via [conda](https://docs.conda.io/en/latest/) and activate the environment:

```sh
conda env create -f environment.yml
conda activate diseasomes
```

## Running the tests

Compare the two diseasomes via permutation tests:

```sh
(diseasomes) cd diseasomes
(diseasomes) python compare_diseasomes.py -n <NUM-PERMUTATIONS>
```

Depending on the number of permutations, this might take a while. The results can be found in the `results` directory.

## Visualizing the results

Once all results have been computed, you can visualize them using a Jupyter Notebook:

```sh
(diseasomes) jupyter notebook playground.ipynb
```

