from graphsimqt.run_shortest_path_analysis import run_shortest_path_analysis
from graphsimqt.utils.get_directory_paths import get_root_directory_path


def run_shortest_path_analyses():
    graph_dir = get_root_directory_path().joinpath('data').joinpath('graphs')

    run_shortest_path_analysis(graph_dir.joinpath('disease_disease/icd10_est_comorbidity_based.gt'),
                               graph_dir.joinpath('gene_disease/entrez_icd10_without_propagation_with_ppi_edges.gt'),
                               'disease_distances_vs_comorbidities_noPropag', distance_node_id_attribute_name='ID',
                               exclude_as_connectors=('TYPE', 'disease'))

    run_shortest_path_analysis(graph_dir.joinpath('disease_disease/mondo_drug_based.gt'),
                               graph_dir.joinpath('gene_disease/entrez_mondo_with_ppi_edges.gt'),
                               'disease_distances_vs_shared_drugs', distance_node_id_attribute_name='ID',
                               exclude_as_connectors=('TYPE', 'disease'))

    run_shortest_path_analysis(graph_dir.joinpath('disease_disease/mondo_variant_based.gt'),
                               graph_dir.joinpath('gene_disease/entrez_mondo_with_ppi_edges.gt'),
                               'disease_distances_vs_shared_variants', distance_node_id_attribute_name='ID',
                               exclude_as_connectors=('TYPE', 'disease'))

    run_shortest_path_analysis(graph_dir.joinpath('disease_disease/mondo_symptom_based_pruned_below4lev.gt'),
                               graph_dir.joinpath('gene_disease/entrez_mondo_with_ppi_edges.gt'),
                               'disease_distances_vs_shared_symptoms', distance_node_id_attribute_name='ID', reference_node_id_attribute_name='ID',
                               exclude_as_connectors=('TYPE', 'disease'))

    run_shortest_path_analysis(graph_dir.joinpath('drug_drug/drugbank_disease_based.gt'),
                               graph_dir.joinpath('drug_protein/drugbank_uniprot_with_ppi_edges.gt'),
                               'drug_distances_vs_shared_indications', distance_node_id_attribute_name='ID',
                               exclude_as_connectors=('TYPE', 'drug'))

    # run_shortest_path_analysis(graph_dir.joinpath('drug_disease/drugbank_mondo_indications.gt'),
    #                            graph_dir.joinpath('drug_disease/drugbank_mondo_with_ppi_edges.gt'),
    #                            'drug_indication_distances_vs_DrPPD', reference_node_id_attribute_name='ID', distance_node_id_attribute_name='ID',
    #                            exclude_as_connectors=[('TYPE', 'disease'), ('TYPE', 'drug')])


if __name__ == '__main__':
    run_shortest_path_analyses()
