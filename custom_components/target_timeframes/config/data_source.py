async def async_migrate_data_source_config(version: int, data: {}, get_entries):
  new_data = {**data}

  return new_data

def merge_data_source_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

  return config

def validate_source_config(data):
  errors = {}

  return errors