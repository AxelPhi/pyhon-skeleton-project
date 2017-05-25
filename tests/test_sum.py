from skeleton import sum


def test_sum():
    expected = 9
    test = sum(4, 5)
    assert expected == test
