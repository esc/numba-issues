import numba


@numba.njit
def _calculate_res_dense() -> int:
    def clac_clipped_res_dense(gene: int) -> int:
        return gene
    return 1


_calculate_res_dense()
