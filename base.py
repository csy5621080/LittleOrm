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
                if value.is_primary_key:
                    attributes.update({'__pk__': key})
            else:
                attributes.update({key: value})
        attributes.update({'fields': fields})
        attributes.update({'_fields': _fields})
        attributes.update({'__table__': attrs.get('__table__', class_name)})
        attributes.update({'_fields_map': _fields_map})
        attributes.update({'__query_class__': attrs.get('__query_class__', Query)})
        new_ = type.__new__(cls, class_name, bases, attributes)
        return new_


class Model(object, metaclass=Base):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.query = self.__query_class__(self)
        super(Model, self).__init__()

    def save(self):
        pk, pkv = self.pk()
        instance_dir = {}
        for field in self.fields:
            value = getattr(self, field, None)
            if value:
                instance_dir.update({field: value})
        if pk and pkv:
            result = self.query.filter(**{pk: pkv}).update(**instance_dir).execute()
        else:
            result = self.query.create(**instance_dir).execute()
        return result

    def pk(self):
        pk_field = getattr(self, '__pk__', None)
        if pk_field:
            return pk_field, getattr(self, pk_field, None)
        return pk_field, None


class Person(Model):

    __table__ = 'person'

    id = AutoPrimaryField(length=11)
    last_name = StringField(length=255)
    first_name = StringField(length=255)
    address = StringField(length=255)
    city = StringField(length=255)