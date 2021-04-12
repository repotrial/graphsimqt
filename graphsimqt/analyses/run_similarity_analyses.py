from graphsimqt.run_similarity_analysis import run_similarity_analysis
from graphsimqt.utils.get_directory_paths import get_root_directory_path


def run_similarity_analyses():
    graph_dir = get_root_directory_path().joinpath('data').joinpath('graphs')
    other_dir = get_root_directory_path().joinpath('other')
    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_gene_based_with_propagation.gt'),
                            graph_dir.joinpath('disease_disease/icd10_est_comorbidity_based.gt'),
                            result_directory_name='disease_gene_vs_disease_est_comorbidity',
                            paths_to_node_sets=[other_dir.joinpath('custom_disease_sets.json'),
                                                other_dir.joinpath('icd10_chapters_and_ranges.tsv')])
    run_similarity_analysis(graph_dir.joinpath('disease_disease/mondo_gene_based.gt'),
                            graph_dir.joinpath('disease_disease/mondo_drug_based.gt'),
                            result_directory_name='disease_gene_vs_disease_drug')
    run_similarity_analysis(graph_dir.joinpath('drug_drug/drugbank_disease_based.gt'),
                            graph_dir.joinpath('drug_drug/drugbank_target_based.gt'),
                            result_directory_name='drug_disease_vs_drug_target')


if __name__ == '__main__':
    run_similarity_analyses()
