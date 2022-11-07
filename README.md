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

For instance to run the similarity analysis between gene-based and comorbidity-based diseasomes (in ICD10 namespace) with default parameters:
```sh
python -m graphsimqt.run_similarity_analysis data/graphs/disease_disease/icd10_est_comorbidity_based.gt data/graphs/disease_disease/icd10_gene_based.gt --dirname disease_gene_vs_disease_comorbidity_ICD10
```

For the analyses of networks with more than 1M edges, we recommend to use a more powerful computing machine than a normal PC (e.g. with 32 GB memory)


## Re-running the entire analyses

Run all the shortest path analyses (running takes a couple of days):

```sh
(graphsimqt) python -m graphsimqt.analyses.run_shortest_path_analyses
```

Run all the similarity analyses based on the graph edit distance (running all possible pair-wise comparisons of diseasomes and drugomes takes 2-3 weeks):

```sh
(graphsimqt) python -m graphsimqt.analyses.run_similarity_analyses
```

The results will be saved in subdirectories of the `results` directory.



## Reproducing results plots for global and local analyses of diseasome and drugomes

Once all results have been computed by re-running the entire analyses (as explained above), you can reproduce the plots shown in the paper by executing all steps in the Jupyter notebooks `notebooks/plots_uniform_EEC.ipynb`, `notebooks/plots_rankBased_EEC.ipynb`, and `notebooks/plots_heatmaps.ipynb`.

If you want to skip running the analyses and instead use our obtained results for reproducing the plots, you need to first download the results from [here](https://api.graphsimviz.net/download_results) and unzip the file under the results directory in the git repo. Then you can use the Jupyter notebooks to plot. Please notice that the result files are large hence they are not deposited to this git repository.


## Viewing the results for global and local analyses

Have a look at the Juptyer notebooks `notebooks/plots_uniform_EEC.ipynb`, `notebooks/plots_rankBased_EEC.ipynb`, and `notebooks/plots_heatmaps.ipynb` (plain markdown, you do not need to re-run anything) for the results of the performed analyses. If you have installed `RISE` as specified in the YAML environment, you can view the notebooks in presentation view.


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
│   │   ├── drug_disease # Drug-disease networks.
│   │   ├── drug_drug # Drug-drug networks.
│   │   ├── drug_protein # Drug-protein networks.
│   │   └── gene_disease # Gene-disease networks.   
│   └── other # Can contain other data for specific node sets analyses.
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
├── notebooks # Contains Jupyter notebooks and plots generated by them.
│   ├── plots_heatmaps.ipynb # A notebook to plot an overview of the results on graphs shipped with GraphSimQT in heatmap format.
│   ├── plots_rankBased_ECC.ipynb # A notebook to plot the results of GED analyses (rank based edge edit cost) on graphs shipped with GraphSimQT.
│   └── plots_uniform_ECC.ipynb # A notebook to plot the results of GED analyses (uniform edge edit cost) on graphs shipped with GraphSimQT.
└── results # Results are stored in subdirectories of this directory.
    └── README.md # An almost empty README file.
```

