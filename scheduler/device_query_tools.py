# ---------- Python's Libraries ---------------------------------------------------------------------------------------
from influxdb_client import InfluxDBClient

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------

# ---------- Created Tools --------------------------------------------------------------------------------------------
from apps.settings import INFLUX_URL, INFLUX_TOKEN


class InfluxClient():

    def __init__(self, url=INFLUX_URL, token=INFLUX_TOKEN, org=""):
        self._client = InfluxDBClient(url=url, token=token, org=org)

    @staticmethod
    def gen_filter_field(list_field, condition):
        if not list_field:
            return ""
        elif "all" in list_field:
            return ""
        else:
            key_list = [f'r._field == "{field}"' for field in list_field]

            list_filter = f" {condition} ".join(key_list)
            return f'filter(fn: (r) => {list_filter})'

    @staticmethod
    def gen_filter_tag(dict_tag, condition):
        if not dict_tag:
            return ""
        elif "all" in dict_tag:
            return ""
        else:
            tag_list = [f'r.{k} == "{v}"' for k, v in dict_tag.items()]
            list_filter = f" {condition} ".join(tag_list)
            return f'filter(fn: (r) => {list_filter})'

    def get_buckets(self, **kwargs):
        return self._client.buckets_api().find_buckets(**kwargs)

    def get_measurements(self, query):
        return self._client.query_api().query(query)

    def get_measurement_data_frame(self, query):
        return self._client.query_api().query_data_frame(query)

    def list_measurement_param(self, **kwargs):
        return self._client.buckets_api().find_buckets(**kwargs)

    def list_measurements(self, bucket) -> list:
        query = f'''
            import "influxdata/influxdb/schema"

            schema.measurements(bucket: "{bucket}")
        '''

        return [r[0] for r in self._client.query_api().query(query).to_values(columns=['_value'])]

    def list_tag_keys(self, bucket, mac_address) -> list:
        query = f'''
            import "influxdata/influxdb/schema"
            import "experimental/array"

            execpt_key = ["_start", "_stop", "_field", "_measurement"]      
            schema.tagKeys(bucket: "{bucket}", predicate: (r) => (r.mac_address == "{mac_address}"))
                    |> filter(fn: (r) => not contains(value: r._value, set: execpt_key))
        '''
        return [r[0] for r in self._client.query_api().query(query).to_values(columns=['_value'])]
    
    def list_tag_values(self, bucket, key_tag) -> list:
        query = f'''
            import "influxdata/influxdb/schema"
            import "experimental/array"
   
            schema.tagValues(bucket: "{bucket}", tag: "{key_tag}")
        '''
        return [r[0] for r in self._client.query_api().query(query).to_values(columns=['_value'])]

    def list_fields(self, bucket) -> list:
        query = f'''
            import "influxdata/influxdb/schema"
            
            schema.fieldKeys(bucket: "{bucket}")
        '''

        return [r[0] for r in self._client.query_api().query(query).to_values(columns=['_value'])]


    def list_field_device_param(self, bucket, mac_addresss) -> list:
        query = f'''
            import "influxdata/influxdb/schema"
            
            schema.fieldKeys(bucket: "{bucket}", 
                            predicate: (r) => r.mac_address == "{mac_addresss}")
        '''
        return [r[0] for r in self._client.query_api().query(query).to_values(columns=['_value'])]

    def list_field_measurement(self, bucket, measurement) -> list:
        query = f'''
            import "influxdata/influxdb/schema"
            
            schema.measurementFieldKeys(bucket: "{bucket}", measurement: "{measurement}")
        '''
        return [r[0] for r in self._client.query_api().query(query).to_values(columns=['_value'])]
