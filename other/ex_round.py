import decimal

cps = 30
n = decimal.Decimal(1 / cps).quantize(decimal.Decimal('1.00'), rounding=decimal.ROUND_UP)
print(n)
print(float(n))
