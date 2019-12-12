VARCHAR = 'varchar'
INTEGER = 'int'


class Field(object):

    def __init__(self, name=None, column_type=None, length=None):
        self.name = name
        self.column_type = column_type
        self.length = length

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)


class StringField(Field):

    __value_type__ = str

    def __init__(self, name=None, length=255):
        super(StringField, self).__init__(name, VARCHAR, length)


class IntegerField(Field):

    __value_type__ = int

    def __init__(self, name=None, length=11, auto_increment=False):
        self.auto_increment = auto_increment
        super(IntegerField, self).__init__(name, INTEGER, length)


class AutoPrimaryField(IntegerField):

    def __init__(self, name=None, length=11):
        super(AutoPrimaryField, self).__init__(name, length, True)