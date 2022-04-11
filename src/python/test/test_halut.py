import functools
import timeit
from test.utils.utils import error_hist_numpy
import numpy as np
import pytest
import halutmatmul.halutmatmul as hm


def helper_halut(
    N: int = 128,
    K: int = 64,
    M: int = 16,
    C: int = 16,
    lut_work_const: int = -1,
    a: float = 1.0,
    b: float = 0.0,
) -> None:
    print("=====TEST=====")
    print(f"params: ({N}, {K}, {M}), C: {C}, a: {a}, b: {b}")
    A = (np.random.random((N, K)) + b) * a
    B = (np.random.random((K, M)) + b) * a
    store_array = hm.learn_halut_offline(A, B, C=C, lut_work_const=lut_work_const)
    new_halut = hm.HalutMatmul()
    new_halut.from_numpy(store_array)

    time_learning = (
        timeit.Timer(functools.partial(hm.learn_halut_offline, *[A, B, C])).timeit(5)
        * 1000
        / 5
    )

    print("Time learning: %.2f ms" % (time_learning))
    print(new_halut.stats())

    # accuracy test
    A_2 = (np.random.random((N // 4, K)) + b) * a
    res_halut = new_halut.matmul_online(A_2)
    res_numpy = np.matmul(A_2, B)

    error_hist_numpy(res_halut, res_numpy)

    time_halut = (
        timeit.Timer(functools.partial(new_halut.matmul_online, *[A_2])).timeit(5)
        * 1000
        / 5
    )

    time_numpy = (
        timeit.Timer(functools.partial(np.matmul, *[A_2, B])).timeit(5) * 1000 / 5
    )

    print(
        "time calculation numpy/halutmatmul fp: %.2f / %.2f ms"
        % (time_numpy, time_halut)
    )

    mse = np.square(res_halut - res_numpy).mean()
    mae = np.abs(res_halut - res_numpy).mean()
    # pylint: disable=E1307
    print("mse: %.4f / mae: %.4f" % (mse, mae))


@pytest.mark.parametrize(
    "N, K, M, C, a, b",
    [
        (N, K, M, C, a, b)
        for N in [2048, 16284]
        for K in [512]
        for M in [16, 64]
        for C in [4, 16, 32, 64]
        for a in [1.0, 5.0]
        for b in [0.0, 10.0]
    ],
)
def test_learn_offline(N: int, K: int, M: int, C: int, a: float, b: float) -> None:
    np.random.seed(4419)
    helper_halut(N, K, M, C, a=a, b=b)