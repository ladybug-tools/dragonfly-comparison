# coding=utf-8
"""Model Comparison Properties."""
from dragonfly.extensionutil import model_extension_dicts


class ModelComparisonProperties(object):
    """Comparison Properties for Dragonfly Model.

    Args:
        host: A dragonfly_core Model object that hosts these properties.

    Properties:
        * host
    """

    def __init__(self, host):
        """Initialize Model Comparison properties."""
        self._host = host

    @property
    def host(self):
        """Get the Model object hosting these properties."""
        return self._host

    def apply_properties_from_dict(self, data):
        """Apply the comparison properties of a dictionary to the host Model of this object.

        Args:
            data: A dictionary representation of an entire dragonfly-core Model.
                Note that this dictionary must have ModelComparisonProperties in order
                for this method to successfully apply the comparison properties.
        """
        assert 'comparison' in data['properties'], \
            'Dictionary possesses no ModelComparisonProperties.'
        # collect lists of comparison property dictionaries
        _, _, room2d_c_dicts, _ = \
            model_extension_dicts(data, 'comparison', [], [], [], [])
        # apply comparison properties to objects using the comparison property dictionaries
        for room, r_dict in zip(self.host.room_2ds, room2d_c_dicts):
            if r_dict is not None:
                room.properties.comparison.apply_properties_from_dict(r_dict)

    def to_dict(self):
        """Return Model comparison properties as a dictionary."""
        base = {'comparison': {'type': 'ModelComparisonProperties'}}
        return base

    def duplicate(self, new_host=None):
        """Get a copy of this Model.

        Args:
            new_host: A new Model object that hosts these properties.
                If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        return ModelComparisonProperties(_host)

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Model Comparison Properties: {}'.format(self.host.identifier)
