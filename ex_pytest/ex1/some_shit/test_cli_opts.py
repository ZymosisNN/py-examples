
def test_my_pytestconfig(pytestconfig):
    print(pytestconfig)
    print(pytestconfig.getoption('my_stubs'))

