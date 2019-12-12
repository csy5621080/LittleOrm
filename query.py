from sql import SIGN_MAP, INSERT, SELECT
from engine.mysql_engine import cursor


class Query(object):

    def __init__(self, model_class):
        self.q = cursor()
        self.model = model_class
        self.filter_values = self.model.fields
        self.sql = ''
        self.model_fields = getattr(self.model, '_fields')
        self.model_fields_map = getattr(self.model, '_fields_map')

    @staticmethod
    def get_sign(filter_key):
        sign = '='
        field_name = filter_key
        if '__' in filter_key:
            field_ = str(filter_key).split('__')
            sign_str = field_[-1:]
            sign = SIGN_MAP.get(sign_str)
            field_name = field_[:-1]
        return sign, field_name

    def fields_handle(self, field_name, field_value):
        field_model = self.model_fields.get(field_name)
        if field_model.__value_type__ is str:
            return """ '{}' """.format(field_value)
        elif field_model.__value_type__ is int:
            return field_value

    def create(self):
        create_fields = []
        create_values = []
        for field_name in self.model.fields:
            value = getattr(self.model, field_name, None)
            if value:
                key = field_name
                create_fields.append(key)
                create_values.append(value)
        sql = INSERT.format(table_name=self.model.__table__,
                            fields=','.join(create_fields),
                            values=str(tuple(create_values)))
        self.sql += sql
        return self

    def filter(self, **kwargs):
        filter_conditions = ''
        for k, v in kwargs.items():
            _sign, field_name = self.get_sign(k)
            v = self.fields_handle(field_name, v)
            filter_conditions += ' ' + self.model_fields_map.get(k) + _sign + str(v)
        values = ','.join([self.model_fields_map.get(value) for value in self.filter_values])
        sql = SELECT.format(fields=values, table_name=self.model.__table__, filter_conditions=filter_conditions)
        self.sql += sql
        return self

    def first(self):
        self.sql += ' LIMIT 1'
        return self

    def delete(self):
        pass

    def update(self):
        pass

    def get(self):
        pass

    def values(self, *args):
        self.filter_values = list(args)
        return self

    def execute(self):
        with self.q as query:
            print(self.sql)
            result = list()
            exec_res = query.execute(self.sql)
            return_result = query.fetchall()
            if exec_res and isinstance(return_result, tuple):
                for single_return in return_result:
                    obj = self.model()
                    for idx, sql_res in enumerate(single_return):
                        setattr(obj, self.filter_values[idx], sql_res)
                    result.append(obj)
                return result
            else:
                return exec_res
