from .primitives import types as primitives
# from .associative_containers import types as associative_containers
# from .collections import types as collections
from .container_adapters import types as container_adapters
from .sequence_containers import types as sequence_containers
from .strings import types as strings
# from .unordered_associative_containers import types as unordered_associative_containers

basic_types = {}
basic_types.update(primitives)
basic_types.update(strings)

container_types = {}
# container_types.update(associative_containers)
# container_types.update(collections)
container_types.update(container_adapters)
container_types.update(sequence_containers)
container_types.update(strings)
# container_types.update(unordered_associative_containers)

