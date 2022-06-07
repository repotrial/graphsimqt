from graphsimqt.run_similarity_analysis import run_similarity_analysis
from graphsimqt.utils.get_directory_paths import get_root_directory_path


def run_similarity_analyses():
    graph_dir = get_root_directory_path().joinpath('data').joinpath('graphs')
    # other_dir = get_root_directory_path().joinpath('data').joinpath('other')

    # similarity analyses of disease-disease networks in MONDO namespace
    run_similarity_analysis(graph_dir.joinpath('disease_disease/mondo_gene_based.gt'),
                            graph_dir.joinpath('disease_disease/mondo_drug_based.gt'),
                            result_directory_name='disease_gene_vs_disease_drug', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/mondo_gene_based.gt'),
                            graph_dir.joinpath('disease_disease/mondo_variant_based.gt'),
                            result_directory_name='disease_gene_vs_disease_variant', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/mondo_gene_based.gt'),
                            graph_dir.joinpath('disease_disease/mondo_symptom_based_pruned_below4lev.gt'),
                            result_directory_name='disease_gene_vs_disease_symptom', node_id_attribute_name = 'ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/mondo_drug_based.gt'),
                            graph_dir.joinpath('disease_disease/mondo_variant_based.gt'),
                            result_directory_name='disease_drug_vs_disease_variant', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/mondo_drug_based.gt'),
                            graph_dir.joinpath('disease_disease/mondo_symptom_based_pruned_below4lev.gt'),
                            result_directory_name='disease_drug_vs_disease_symptom', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/mondo_symptom_based_pruned_below4lev.gt'),
                            graph_dir.joinpath('disease_disease/mondo_variant_based.gt'),
                            result_directory_name='disease_symptom_vs_disease_variant', node_id_attribute_name='ID')

    # similarity analyses of drug-disease networks in MONDO namespace
    run_similarity_analysis(graph_dir.joinpath('drug_disease/drugbank_mondo_indications.gt'),
                            graph_dir.joinpath('drug_disease/drugbank_mondo_viaP_distance2.gt'),
                            result_directory_name='GED_drug_indication_distances_vs_DrPPD', node_id_attribute_name = 'ID')

    # similarity analyses of drug-drug networks
    run_similarity_analysis(graph_dir.joinpath('drug_drug/drugbank_disease_based.gt'),
                            graph_dir.joinpath('drug_drug/drugbank_target_based.gt'),
                            result_directory_name='drug_disease_vs_drug_target', node_id_attribute_name='ID')

    # similarity analyses of disease-disease networks in ICD-10 namespace
    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_gene_based.gt'),
                            graph_dir.joinpath('disease_disease/icd10_est_comorbidity_based.gt'),
                            result_directory_name='disease_gene_vs_disease_comorbidity_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_drug_based.gt'),
                            graph_dir.joinpath('disease_disease/icd10_est_comorbidity_based.gt'),
                            result_directory_name='disease_drug_vs_disease_comorbidity_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_variant_based.gt'),
                            graph_dir.joinpath('disease_disease/icd10_est_comorbidity_based.gt'),
                            result_directory_name='disease_variant_vs_disease_comorbidity_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_symptom_based_pruned_below4lev.gt'),
                            graph_dir.joinpath('disease_disease/icd10_est_comorbidity_based.gt'),
                            result_directory_name='disease_symptom_vs_disease_comorbidity_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_gene_based.gt'),
                            graph_dir.joinpath('disease_disease/icd10_drug_based.gt'),
                            result_directory_name='disease_gene_vs_disease_drug_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_gene_based.gt'),
                            graph_dir.joinpath('disease_disease/icd10_variant_based.gt'),
                            result_directory_name='disease_gene_vs_disease_variant_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_drug_based.gt'),
                            graph_dir.joinpath('disease_disease/icd10_variant_based.gt'),
                            result_directory_name='disease_drug_vs_disease_variant_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_gene_based.gt'),
                            graph_dir.joinpath('disease_disease/icd10_symptom_based_pruned_below4lev.gt'),
                            result_directory_name='disease_gene_vs_disease_symptom_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_drug_based.gt'),
                            graph_dir.joinpath('disease_disease/icd10_symptom_based_pruned_below4lev.gt'),
                            result_directory_name='disease_drug_vs_disease_symptom_ICD10', node_id_attribute_name='ID')

    run_similarity_analysis(graph_dir.joinpath('disease_disease/icd10_symptom_based_pruned_below4lev.gt'),
                            graph_dir.joinpath('disease_disease/icd10_variant_based.gt'),
                            result_directory_name='disease_symptom_vs_disease_variant_ICD10', node_id_attribute_name='ID')

    # similarity analyses of drug-disease networks in ICD-10 namespace
    run_similarity_analysis(graph_dir.joinpath('drug_disease/drugbank_icd10_indications.gt'),
                            graph_dir.joinpath('drug_disease/drugbank_icd10_viaP_distance2.gt'),
                            result_directory_name='GED_drug_indication_distances_vs_DrPD_ICD10', node_id_attribute_name='ID')


if __name__ == '__main__':
    run_similarity_analyses()
