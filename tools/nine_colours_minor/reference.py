"""Read Claude Final v1 components without changing shared engine modules."""
import sys
import types
from p3d import api
from prepare import CLAUDE


def package():
    name = 'nine_reference_p3d'
    if name not in sys.modules:
        module = types.ModuleType(name)
        module.__path__ = [str(CLAUDE / 'engine/p3d')]
        sys.modules[name] = module
        # Share the renderer's value types (not its actor or word modules).
        sys.modules[name+'.api'] = api
    return name


package()
