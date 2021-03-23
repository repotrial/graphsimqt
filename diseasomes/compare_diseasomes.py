import sys
from pathlib import Path
import uuid
sys.path.append('..')
from diseasomes.permutation_tests import run_permutation_tests
from diseasomes.compute_empirical_p_values import compute_empirical_p_values
from diseasomes.compute_mwu_and_wilcoxon_p_values import compute_mwu_and_wilcoxon_p_values
from diseasomes.utils import get_parser


def compare_diseasomes(path_graph_1: Path, path_graph_2: Path, result_file_prefix: str = None,
                       num_permutations: int = 1000):
    if not result_file_prefix:
        result_file_prefix = uuid.uuid4()
    run_permutation_tests(path_graph_1, path_graph_2, result_file_prefix, num_permutations)
    compute_empirical_p_values(result_file_prefix)
    compute_mwu_and_wilcoxon_p_values(result_file_prefix)


if __name__ == '__main__':
    args = get_parser('Compare two disease networks.').parse_args()
    compare_diseasomes(args.graph_1, args.graph_2, args.p, args.n)
