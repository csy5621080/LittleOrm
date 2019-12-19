from sql import SIGN_MAP, INSERT, SELECT, UPDATE, DELETE
from engine.mysql_engine import connection


class Query(object):

    class QueryType(object):

        __select__ = SELECT
        __insert__ = INSERT
        __update__ = UPDATE
        __delete__ = DELETE

    def __init__(self, model_class):
        """
            conn: 连接池链接.
            model: 模型对象. obj: base.Model
            filter_values: 查询的字段集合.如 “SELECT id, name FROM table” 语句中的id和name
            sql: 生成的sql语句.
            model_fields: 模型的字段对象集合.
            model_fields_map: 模型字段名称映射.
            query_type: C R U D类型
            filter_conditions: 条件. 即 WHERE 语句的逻辑部分.
            order_condition: 排序条件.
            limit: 分页参数.
            create_values: INSERT 语句的VALUES部分.
            create_fields: INSERT 语句的字段部分.
            updater: UPDATE 语句的SET 部分
        """
        self.conn = connection
        self.model = model_class
        self.filter_values = self.model.fields
        self.sql = ''
        self.model_fields = getattr(self.model, '_fields')
        self.model_fields_map = getattr(self.model, '_fields_map')
        self.query_type = self.QueryType.__select__
        self.filter_conditions = {}
        self.order_conditions = {}
        self.limits = tuple()

        self.create_values = []
        self.create_fields = []

        self.updater = dict()

    @staticmethod
    def get_sign(filter_key: str) -> tuple:
        sign = '='
        field_name = filter_key
        if '__' in filter_key:
            field_ = str(filter_key).split('__')
            sign_str = field_[-1]
            sign = SIGN_MAP.get(sign_str)
            field_name = '__'.join(field_[:-1])
        return sign, field_name

    def fields_handle(self, field_name: str, field_value: str) -> tuple or str:
        field_model = self.model_fields.get(field_name)
        if field_model.__value_type__ is str:
            if isinstance(field_value, list) or isinstance(field_value, tuple):
                field_value = [""" '{}' """.format(field_v) for field_v in field_value]
                return tuple(field_value)
            else:
                return """ '{}' """.format(str(field_value))
        elif field_model.__value_type__ is int:
            if isinstance(field_value, list):
                field_value = tuple(field_value)
            elif isinstance(field_value, int):
                field_value = str(field_value)
            return field_value

    def create(self, **kwargs: dict) -> object:
        self.query_type = self.QueryType.__insert__
        for field_name in self.model.fields:
            value = kwargs.get(field_name, None)
            if value:
                key = field_name
                self.create_fields.append(key)
                self.create_values.append(value)
        return self

    def filter(self, **kwargs: dict) -> object:
        self.filter_conditions.update(**kwargs)
        return self

    def first(self) -> object:
        self.limits = (1, )
        return self

    def delete(self) -> object:
        self.query_type = self.QueryType.__delete__
        return self

    def update(self, **kwargs: dict) -> object:
        self.query_type = self.QueryType.__update__
        self.updater.update(**kwargs)
        return self

    def get(self):
        pass

    def values(self, *args: tuple or list) -> object:
        self.filter_values = list(args)
        return self

    def execute(self) -> int or list:
        self.handle_query()
        with self.conn() as conn:
            print(self.sql)
            cursor = conn.cursor()
            exec_res = cursor.execute(self.sql)
            return_result = cursor.fetchall()
            if exec_res and return_result and isinstance(return_result, tuple):
                result = ArrayQueryResult()
                for single_return in return_result:
                    obj = SingleQueryResult()
                    for idx, sql_res in enumerate(single_return):
                        setattr(obj, self.filter_values[idx], sql_res)
                    obj.model = self.model
                    result.append(obj)
            else:
                result = exec_res
            self.query_clear()
            cursor.close()
            return result

    def query_clear(self) -> None:
        # 此处重置模型内的query对象为一个新的对象
        setattr(self.model, 'query', Query(self.model))

    def get_condition(self) -> str:
        filter_conditions = ''
        for k, v in self.filter_conditions.items():
            _sign, field_name = self.get_sign(k)
            v = self.fields_handle(field_name, v)
            if filter_conditions:
                filter_conditions += ' and ' + self.model_fields_map.get(field_name) + _sign + str(v)
            else:
                filter_conditions += self.model_fields_map.get(field_name) + _sign + str(v)
        return filter_conditions

    def handle_query(self) -> str:
        if self.query_type == self.QueryType.__select__:
            if self.filter_conditions:
                filter_conditions = self.get_condition()
                values = ','.join([self.model_fields_map.get(value) for value in self.filter_values])

                if filter_conditions:
                    filter_conditions = ' WHERE ' + filter_conditions

                sql = self.query_type.format(fields=values, table_name=self.model.__table__,
                                             filter_conditions=filter_conditions)
                self.sql += sql
            if len(self.limits) == 1:
                self.sql += ' LIMIT {limits}'.format(limits=str(self.limits[0]))
            elif len(self.limits) == 2:
                self.sql += ' LIMIT {limits}'.format(limits=str(self.limits[0]) + ', ' + str(self.limits[1]))
        elif self.query_type == self.QueryType.__insert__:
            sql = self.query_type.format(table_name=self.model.__table__,
                                         fields=','.join(self.create_fields),
                                         values=str(tuple(self.create_values)))
            self.sql += sql
        elif self.query_type == self.QueryType.__update__:
            updaters = []
            for updater_k, updater_v in self.updater.items():
                single_updater = updater_k + '=' + self.fields_handle(updater_k, updater_v)
                updaters.append(single_updater)
            update_conditions = ','.join(updaters)
            filter_conditions = self.get_condition()
            if filter_conditions:
                filter_conditions = ' WHERE ' + filter_conditions

            sql = self.query_type.format(table_name=self.model.__table__, update_conditions=update_conditions,
                                         filter_conditions=filter_conditions)
            self.sql = sql
        elif self.query_type == self.QueryType.__delete__:
            filter_conditions = self.get_condition()

            if filter_conditions:
                filter_conditions = ' WHERE ' + filter_conditions

            sql = self.query_type.format(table_name=self.model.__table__, filter_conditions=filter_conditions)
            self.sql = sql


class SingleQueryResult(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def instance(self, **kwargs: dict) -> object:
        instance = getattr(self, 'model')
        if instance:
            iter_instance = self.__dict__
            copy_instance = iter_instance.copy()
            copy_instance.pop('model')
            copy_instance.update(kwargs)
            for key, value in copy_instance.items():
                setattr(instance, key, value)
            return instance
        else:
            raise Exception('SingleQueryResult object has no attribute <model>. 明白不！就是没有model这玩意. ')

    def __str__(self):
        return '<query.SingleQueryResult object at {pk}>'.format(pk=str(id(self)))


class ArrayQueryResult(list):

    def __init__(self):
        super(ArrayQueryResult, self).__init__()

    def __str__(self):
        return '<query.ArrayQueryResult object at {pk}>'.format(pk=str(id(self)))

    def one(self):
        if len(self):
            return self[0]
        return None

