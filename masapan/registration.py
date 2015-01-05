
registry = {}


def register(path, case):
    #if registry is None:
    #    registry = {}

    if registry.get(path):
        registry[path] = registry.path.append(case)
    else:
        registry[path] = [case]
