from fields import Field, IntegerField, StringField
from collections import OrderedDict
from engine.mysql_engine import cursor
from sql import INSERT, SELECT


class Base(type):

    def __new__(cls, class_name, bases, attrs):
        fields = list()
        attributes = OrderedDict()
        _fields = dict()
        _fields_map = dict()
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields.append(key)
                _fields_map[key] = value.name or key
                _fields[key] = value
            else:
                attributes.update({key: value})
        attributes.update({'fields': fields})
        attributes.update({'_fields': _fields})
        attributes.update({'__table__': attrs.get('__table__', class_name)})
        attributes.update({'q': cursor()})
        attributes.update({'_fields_map': _fields_map})
        return type.__new__(cls, class_name, bases, attributes)


class Model(object, metaclass=Base):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        super(Model, self).__init__()
        self.filter_values = self.fields
        self.sql = ''
        self._q = None

    def create(self):
        create_fields = []
        create_values = []
        for field_name in self.fields:
            value = getattr(self, field_name, None)
            if value:
                key = field_name
                create_fields.append(key)
                create_values.append(value)
        sql = INSERT.format(table_name=self.__table__,
                            fields=','.join(create_fields),
                            values=str(tuple(create_values)))
        self.sql += sql
        return self

    def delete(self):
        pass

    def update(self):
        pass

    def get(self):
        pass

    def filter(self, **kwargs):
        filter_conditions = ''
        for k, v in kwargs.items():
            print(k)
            filter_conditions += ' ' + self._fields_map.get(k) + '=' + str(v)
        values = ','.join([self._fields_map.get(value) for value in self.filter_values])
        sql = SELECT.format(fields=values, table_name=self.__table__, filter_conditions=filter_conditions)
        self.sql += sql
        return self

    def values(self, *args):
        self.filter_values = list(args)
        return self

    def first(self):
        self.sql += ' LIMIT 1'
        return self

    def execute(self):
        with self._q as query:
            print(self.sql)
            result = list()
            exec_res = query.execute(self.sql)
            return_result = query.fetchall()
            if exec_res and isinstance(return_result, tuple):
                for single_return in return_result:
                    obj = self.__class__()
                    for idx, sql_res in enumerate(single_return):
                        setattr(obj, self.filter_values[idx], sql_res)
                    result.append(obj)
                return result
            else:
                return exec_res


class Person(Model):
    __table__ = 'person'
    id = IntegerField('id')
    last_name = StringField('last_name')
    first_name = StringField('first_name')
    address = StringField('address')
    city = StringField('city')


p = Person().filter(first_name='杨').first().execute()
print(p[0].first_name)

# p = Person(last_name='迅', first_name='杨', address='河南省商丘市睢县尚屯镇杨庄村', city='睢县')
# p.create()
# res = p.execute()
# p.create()

