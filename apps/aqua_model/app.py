import pytest
import datetime


class Parameter:
    """Base class for all aquarium parameters."""

    def __init__(self, initial_value, name=None, unit=None, history=None):
        self.value = initial_value
        self.name = name
        self.unit = unit
        self.history = history if history else []
        self._add_history(initial_value)

    def _add_history(self, value):
        self.history.append((datetime.datetime.now(), value))
    
    def update(self, new_value):
        """Updates the parameter value and adds to history."""
        self.value = new_value
        self._add_history(new_value)

    def calculate(self, **kwargs):
         """Placeholder for parameter-specific calculations."""
         pass

    def __repr__(self):
        return f"{self.name}: {self.value} {self.unit}"


class Temperature(Parameter):
    """Temperature in Celsius."""

    def __init__(self, initial_value=25.0):
        super().__init__(initial_value, name="Temperature", unit="°C")

    def calculate(self, ambient_temp=None, heater_power=0):
      if ambient_temp:
        self.update(ambient_temp + (heater_power*0.1)) # Simplified calculation
      return self.value



class pH(Parameter):
    """pH level."""

    def __init__(self, initial_value=8.2):
        super().__init__(initial_value, name="pH", unit="")

    def calculate(self, temperature):
        """Simulates pH change due to temperature."""
        temp_effect = (temperature.value - 25) * -0.01  # Example logic
        self.update(max(7, min(9, self.value + temp_effect)))
        return self.value


class Salinity(Parameter):
    """Salinity in ppt."""

    def __init__(self, initial_value=35.0):
        super().__init__(initial_value, name="Salinity", unit="ppt")

    def calculate(self, top_off_water=0, salt_addition=0):
        """Simulates salinity change due to water changes."""
        if top_off_water:
          self.update(max(20, min(40, self.value - (top_off_water * 0.1))))
        if salt_addition:
          self.update(max(20, min(40, self.value + (salt_addition * 0.1))))
        return self.value


class Ammonia(Parameter):
    """Ammonia level in ppm."""

    def __init__(self, initial_value=0.0):
        super().__init__(initial_value, name="Ammonia", unit="ppm")
    
    def calculate(self, fish_load =0, bacteria_level=0):
      if fish_load:
          self.update(min(1, self.value + (fish_load * 0.01) - (bacteria_level * 0.005)))
      return self.value

class Nitrate(Parameter):
    """Nitrate level in ppm."""

    def __init__(self, initial_value=0.0):
       super().__init__(initial_value, name="Nitrate", unit="ppm")
    
    def calculate(self, ammonia, bacteria_level=0):
       if ammonia:
          self.update(min(50, self.value + (ammonia.value * 0.5) - (bacteria_level * 0.1)))
       return self.value

class Bacteria(Parameter):
    """Bacteria level, arbitrary units."""
    def __init__(self, initial_value=1.0):
      super().__init__(initial_value, name="Bacteria Level", unit="units")
    
    def calculate(self, waste_level):
        if waste_level:
          self.update(min(20, self.value + (waste_level * 0.2))) # Simplified model
        return self.value


class AquariumModel:
    """Container for all parameters."""
    def __init__(self):
      self.parameters = {
        "temperature": Temperature(),
        "ph": pH(),
        "salinity": Salinity(),
        "ammonia": Ammonia(),
        "nitrate": Nitrate(),
        "bacteria": Bacteria()
    }

    def update_all(self, ambient_temp=None, heater_power=0, top_off_water=0, salt_addition=0, fish_load=0, waste_level=0):
      """Updates all parameters in the model."""
      
      self.parameters["temperature"].calculate(ambient_temp=ambient_temp, heater_power=heater_power)
      self.parameters["ph"].calculate(temperature=self.parameters["temperature"])
      self.parameters["salinity"].calculate(top_off_water=top_off_water, salt_addition=salt_addition)
      self.parameters["bacteria"].calculate(waste_level=waste_level)
      self.parameters["ammonia"].calculate(fish_load=fish_load, bacteria_level=self.parameters["bacteria"].value)
      self.parameters["nitrate"].calculate(ammonia=self.parameters["ammonia"], bacteria_level=self.parameters["bacteria"].value)


    def get_parameter(self, name):
        """Returns a specific parameter instance."""
        return self.parameters.get(name)
      
    def get_all_parameters(self):
        """Returns all parameters"""
        return self.parameters

    def __repr__(self):
       return f"Aquarium State:\n" + "\n".join([str(p) for p in self.parameters.values()])