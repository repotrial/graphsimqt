import sys
import argparse
sys.path.append('..')
from diseasomes.permutation_tests import run_permutation_tests
from diseasomes.compute_empirical_p_values import compute_empirical_p_values
from diseasomes.compute_mwu_p_values import compute_all_mwu_p_values
from diseasomes.compute_wilcoxon_p_values import compute_all_wilcoxon_p_values


def compare_diseasomes(num_permutations):
    run_permutation_tests(num_permutations=num_permutations)
    compute_empirical_p_values()
    compute_all_mwu_p_values()
    compute_all_wilcoxon_p_values()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Compare gene- and comorbidity-based diseasomes.')
    parser.add_argument('-n', type=int, required=True, help='Number of permutations used for permutation tests.')
    args = parser.parse_args()
    compare_diseasomes(args.n)
