import voluptuous as vol

def get_schema_keys(schema):
  keys = []
  for k in schema.keys():
      if isinstance(k, vol.Marker):  # Required/Optional wrapper
          keys.append(k.schema)      # actual key name
      else:
          keys.append(k)
  return keys

def assert_errors_not_present(errors, default_keys: list[str], key_to_ignore: str = None):
  assert len(default_keys) > 0
  
  for key in default_keys:
    if key_to_ignore is not None and key == key_to_ignore:
      continue
      
    assert key not in errors