def add(augend, addend):
    if not isinstance(augend, basestring) or not isinstance(addend, basestring):
        raise ValueError
    simple_sum = augend + addend
    if any(char != 'I' for char in simple_sum):
        raise ValueError
    return simple_sum

