class Some:
    @property
    def prop(self):
        return 'property with getter only'

    @property
    def var(self):
        print('- run getter')
        return 'some result'

    @var.setter
    def var(self, value):
        print(f'- run setter {value}')

    @var.deleter
    def var(self):
        print('- run deleter')


o = Some()

print(o.prop)

print(o.var)

o.var = 111

del o.var
