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

    def create(self):
        sql = INSERT.format(table_name=self.__table__,
                            fields='({fields})'.format(fields=','.join([self._fields_map.get(field) for field in self.fields])),
                            values=str(tuple([getattr(self, field_name) for field_name in self.fields])))
        with self.q as query:
            print(sql)
            query.execute(sql)
            # query.close()
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
            filter_conditions += ' ' + self._fields_map.get(k) + '=' + str(v)
        values = ','.join([self._fields_map.get(value) for value in self.filter_values])
        sql = SELECT.format(fields=values, table_name=self.__table__, filter_conditions=filter_conditions)
        with self.q as query:
            print(sql)
            result = list()
            res = query.execute(sql)
            if res:
                for sql_return in query.fetchall():
                    obj = self.__class__()
                    for idx, sql_res in enumerate(sql_return):
                        setattr(obj, self.filter_values[idx-1], sql_res)
                    result.append(obj)
                return result
            else:
                raise Exception('不知道数据库查询出了个啥错，反正出错了。')

    def values(self, *args):
        self.filter_values = list(args)
        return self


class Person(Model):
    __table__ = 'Persons'
    id = IntegerField('Id_P')
    last_name = StringField('LastName')
    first_name = StringField('FirstName')
    address = StringField('Address')
    city = StringField('City')


p = Person().values('last_name', 'first_name').filter(id=1)
print(p)
print(p[0].last_name)