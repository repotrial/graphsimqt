from diseasomes.permutation_tests import run_permutation_tests
from diseasomes.compute_empirical_p_values import compute_empirical_p_values
from diseasomes.compute_mwu_p_values import compute_mwu_p_values
from diseasomes.summarize_empirical_p_values import summarize_empirical_p_values
from diseasomes.analyze_commrocg import analyze_commrocg
import argparse


def compare_diseasomes(num_permutations):
    run_permutation_tests(num_permutations=num_permutations)
    compute_empirical_p_values()
    compute_mwu_p_values('chapter')
    compute_mwu_p_values('range')
    summarize_empirical_p_values('chapter')
    summarize_empirical_p_values('range')
    analyze_commrocg()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Compare gene- and comorbidity-based diseasomes.')
    parser.add_argument('-n', type=int, default=1000, help='Number of permutations used for permutation tests.')
    args = parser.parse_args()
    compare_diseasomes(args.n)
