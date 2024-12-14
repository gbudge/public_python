def test_parameter_creation():
    temp = Temperature(26.0)
    assert temp.value == 26.0
    assert temp.name == "Temperature"
    assert temp.unit == "°C"
    assert len(temp.history) == 1

def test_temperature_calculation():
    temp = Temperature(25.0)
    new_temp = temp.calculate(ambient_temp=26, heater_power=1)
    assert new_temp == 26.1
    assert len(temp.history) == 2

def test_ph_calculation():
    temp = Temperature(26)
    ph = pH(8.2)
    ph.calculate(temperature=temp)
    assert 7 <= ph.value <= 9
    assert len(ph.history) == 2

def test_salinity_calculation():
    salinity = Salinity(35)
    salinity.calculate(top_off_water=1)
    assert 34.9 <= salinity.value <= 35
    salinity.calculate(salt_addition=1)
    assert 34.9 <= salinity.value <= 35.1
    assert len(salinity.history) == 3

def test_ammonia_calculation():
  ammonia = Ammonia()
  ammonia.calculate(fish_load=1)
  assert ammonia.value > 0
  ammonia.calculate(bacteria_level=10)
  assert ammonia.value > 0
  assert len(ammonia.history) == 3

def test_nitrate_calculation():
    ammonia = Ammonia(0.1)
    nitrate = Nitrate()
    nitrate.calculate(ammonia=ammonia)
    assert nitrate.value > 0
    nitrate.calculate(ammonia=ammonia, bacteria_level=10)
    assert nitrate.value > 0
    assert len(nitrate.history) == 3

def test_bacteria_calculation():
    bacteria = Bacteria()
    bacteria.calculate(waste_level=1)
    assert bacteria.value > 0
    assert len(bacteria.history) == 2

def test_aquarium_model_update():
  model = AquariumModel()
  model.update_all(ambient_temp=27, heater_power=1, top_off_water=1, salt_addition=1, fish_load=1, waste_level=1)
  assert model.get_parameter("temperature").value == 27.1
  assert model.get_parameter("ph").value != 8.2
  assert model.get_parameter("salinity").value != 35.0
  assert model.get_parameter("ammonia").value > 0
  assert model.get_parameter("nitrate").value > 0
  assert model.get_parameter("bacteria").value > 0

def test_aquarium_model_get():
  model = AquariumModel()
  temp = model.get_parameter("temperature")
  assert isinstance(temp, Temperature)

def test_aquarium_model_get_all():
    model = AquariumModel()
    all_params = model.get_all_parameters()
    assert len(all_params) == 6
    assert isinstance(all_params["temperature"], Temperature)

def test_aquarium_model_repr():
    model = AquariumModel()
    assert "Aquarium State:" in str(model)
    