from typing import Type, Any


class AutoOuts:
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)

        mandatory_outs, optional_outs = _get_outs(cls)
        mandatory_outs -= optional_outs
        print('TOTAL:')
        print(f'    {mandatory_outs=}')
        print(f'    {optional_outs=}')

        for out in mandatory_outs:
            try:
                setattr(obj, out, kwargs[out])
            except KeyError as ex:
                raise RuntimeError(f'"{out}" must be defined during creating "{cls.__name__}".'
                                   f' Mandatory attrs: {mandatory_outs}') from ex

        kw_outs = {k: kwargs[k] for k in optional_outs if k in kwargs}
        obj.__dict__.update(kw_outs)

        return obj

    def __init__(self, *args, **kwargs):
        print('INIT:')
        print('    ', self.__dict__)
        print('    ', args, kwargs)


def _get_outs(probed_cls: Type[Any]) -> tuple[set, set]:
    """
    Recursive search for attributes with name starts with "out_"
    :return: 2 sets of outs: from __annotations__ and from __dict__
    """
    if not probed_cls:
        return set(), set()

    mand_outs, opt_outs = _get_outs(probed_cls.__base__)
    print(probed_cls.__name__)
    print('__annotations__', probed_cls.__dict__.get('__annotations__', {}))
    print('__dict__', {attr for attr in probed_cls.__dict__ if attr.startswith('out_')})
    print(f'    {mand_outs=}')
    print(f'    {opt_outs=}')

    this_mand_outs = {attr for attr in probed_cls.__dict__.get('__annotations__', {})
                      if attr.startswith('out_')}
    this_opt_outs = {attr for attr in probed_cls.__dict__ if attr.startswith('out_')}
    mand_outs.update(this_mand_outs)
    opt_outs.update(this_opt_outs)
    print(f'    U {mand_outs=}')
    print(f'    U {opt_outs=}')

    return mand_outs, opt_outs


if __name__ == '__main__':
    class AutoOuts2(AutoOuts):
        out_11: str
        out_12: str = 'out_12'
        out_13 = 'out_13'
        out_21: str
        out_22: str = 'out_22'
        out_23 = 'out_23'

    class AutoOuts3(AutoOuts2):
        out_21 = 'out_211'
        out_22: str = 'out_221'
        out_23: str = 'out_231'
        out_31: str
        out_32: str = 'out_32'
        out_33 = 'out_33'

    AutoOuts3(1, 2, out_11='ZZZZ', out_31='XXXX')
