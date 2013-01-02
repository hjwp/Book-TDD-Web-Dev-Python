ROMAN_NUMERALS = ('I', 'V', 'X')
def add(augend, addend):
    if not isinstance(augend, basestring) or not isinstance(addend, basestring):
        raise ValueError

    simple_augend = augend.replace('IV', 'IIII')
    simple_addend = addend.replace('IV', 'IIII')

    simple_sum = simple_augend + simple_addend

    if any(char not in ROMAN_NUMERALS for char in simple_sum):
        raise ValueError

    ordered_sum = ''.join(reversed(sorted(simple_sum)))

    canonicalised_sum = ordered_sum.replace('IIIII', 'V').replace('IIII', 'IV').replace('VV', 'X').replace('VIV', 'IX')
    return canonicalised_sum

