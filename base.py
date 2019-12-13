from fields import Field, IntegerField, StringField, AutoPrimaryField
from collections import OrderedDict
from query import Query


class Base(type):

    def __new__(cls, class_name: str, bases: object, attrs: dict):
        fields = list()
        attributes = OrderedDict()
        _fields = OrderedDict()
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
        attributes.update({'_fields_map': _fields_map})
        new_ = type.__new__(cls, class_name, bases, attributes)
        # 元类可直接调用子类的方法
        new_.set_query(attrs.get('__query_class__', Query))
        return new_


class Model(object, metaclass=Base):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        super(Model, self).__init__()

    @classmethod
    def set_query(cls, query_class: type):
        setattr(cls, 'query', query_class(cls))


class Person(Model):

    __table__ = 'person'

    id = AutoPrimaryField(length=11)
    last_name = StringField(length=255)
    first_name = StringField(length=255)
    address = StringField(length=255)
    city = StringField(length=255)


# pp = Person.query.filter(id=1).execute()
#
#
# ppp = Person.query.filter(id=2).execute()
#
# print(pp)
# print(ppp)
# print(pp.one())
# print(ppp.one())
# print(pp.one().id)
# print(ppp.one().id)

# p = Person
# pa = p.query.create(last_name='婉蓉', first_name='赖', address='北京市海淀区上地某嘎达', city='江西省某嘎达市').execute()
# print(p)
# print(pa)

ppp = Person.query.filter(id__IN=(9, 11)).delete().execute()
print(ppp)