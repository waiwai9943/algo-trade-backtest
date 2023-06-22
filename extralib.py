
def get_variable_name(var):
    varName = ""
    variables = dict(globals())
    for name in variables:
        if variables[name] is var:
            varName = name
            break
    return varName
fuckyou = 123
print(get_variable_name(fuckyou))