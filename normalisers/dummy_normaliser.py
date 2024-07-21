import logging

from .model import PoweffModel
from .normaliser import Normaliser


class DummyNormaliser(Normaliser):

    def __init__(self, customer):
        super().__init(customer)

    def normalise(self, sites, device_config, command_data):
        current_device = PoweffModel()
        device = device_config["name"]
        current_device.set_family(device_config["family"])

        self._models.append(poweff_current)

        return self._models
