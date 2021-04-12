# GraphSimQT: A Graph Similarity Quantification Tool



## Installation

Download the repository.

```sh
git clone https://github.com/repotrial/graphsimqt
cd graphsimqt
```

Install all dependencies via [conda](https://docs.conda.io/en/latest/) and activate the environment:

```sh
conda env create -f environment.yml
conda activate graphsimqt
```



## Results for network-based drug repurposing

Have a look at the Juptyer notebook `notebooks/presentation.ipynb` (plain markdown, you do not need to re-run anything). If you have installed `RISE` as specified in the YAML environment, you can view the notebook in presentation view.



## Re-running the analyses

Run the shortest path analyses (takes a while):

```sh
(graphsimqt) python -m graphsimqt.analyses.run_shortest_path_analyses
```

Run the similarity analyses based on the graph edit distance (takes even longer):

```sh
(graphsimqt) python -m graphsimqt.analyses.run_similarity_analyses
```

The results can be found in subdirectories of the `results` directory.



## Plotting the results

Once all results have been computed, you can plot by executing all steps in the Jupyter notebook `notebooks/plots.ipynb`.



## Using GraphSimQT for custom input

Each Python module `MODULE_NAME.py` contained in the `graphsimqt` package can be used from the command line or as a library function. For information on the required input parameters, print the help messages of the command line interfaces:

```sh
(graphsimqt) python -m graphsimqt.MODULE_NAME -h
```

Alternatively, display the docstring of the library functions:

```python
import graphsimqt
help(graphsimqt.MODULE_NAME)
```



## License

GraphSimQT is licensed under the [GNU General Public License, Version 3](https://www.gnu.org/licenses/gpl-3.0.en.html).



## Repository structure

```sh
.
├── LICENSE # The license.
├── README.md # This file.
├── data # Contains data shipped with GraphSimQT.
│   ├── graphs # Contains networks shipped with GraphSimQT (in graph_tool.gt format).
│   │   ├── disease_disease # Disease-disease networks.
│   │   ├── drug_drug # Drug-drug networks.
│   │   ├── drug_protein # Drug-protein networks.
│   │   ├── gene_disease # Gene-disease networks.
│   │   └── gene_gene # Gene-gene networks.
│   └── other # Contains other data shipped with GraphSimQT.
├── environment.yml # YAML environment with dependencies.
├── graphsimqt # The main Python package.
│   ├── __init__.py # Init file.
│   ├── analyses # Subpackage with scrips to run analyses on graphs shipped with GraphSimQT.
│   │   ├── __init__.py # Init file.
│   │   ├── run_shortest_path_analyses.py # Runs the shortest path analyses.
│   │   └── run_similarity_analyses.py # Runs the similarity analyses.
│   ├── analyze_shortest_path_distances.py # Analyzes shortest path distances.
│   ├── compute_empirical_p_values.py # Computes empirical p-values.
│   ├── compute_mwu_p_values.py # Computes MWU p-values.
│   ├── compute_shortest_path_distances.py # Computes shortest path distances.
│   ├── normalize_graph.py # Normalizes input graph.
│   ├── run_permutation_tests.py # Runs permutation tests.
│   ├── run_shortest_path_analysis.py # Runs the entire shortest path analyses pipeline.
│   ├── run_similarity_analysis.py # Runs the entire similarity analysis pipeline.
│   └── utils # Subpackage contraining helper functions.
├── img # Contains plots for results on graphs shipped with GraphSimQT.
├── notebooks # Contains Jupyter notebooks.
│   ├── plots.ipynb # A notebook to plot the results on graphs shipped with GraphSimQT.
│   └── presentation.ipynb # A presentation of the most important findings.
└── results # Results are stored in subdirectories of this directory.
    └── README.md # An almost empty README file.
```

