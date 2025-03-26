import logging
from homeassistant.helpers import storage

from pydantic import BaseModel

from ..utils.data_source_data import DataSourceItem

_LOGGER = logging.getLogger(__name__)

class DataSourceData(BaseModel):
  data: list[DataSourceItem]

async def async_load_cached_data_source_data(hass, data_source_id: str) -> list[DataSourceItem] | None:
  store = storage.Store(hass, "1", f"target_timeframes.{data_source_id}_data_source")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached data source data for {data_source_id}")
      return DataSourceData.parse_obj(data).data
  except:
    return None
  
async def async_save_cached_data_source_data(hass, data_source_id: str, data: list[DataSourceItem]):
  if data is not None:
    store = storage.Store(hass, "1", f"target_timeframes.{data_source_id}_data_source")
    await store.async_save(DataSourceData(data=data).dict())
    _LOGGER.debug(f"Saved data source data for {data_source_id}")