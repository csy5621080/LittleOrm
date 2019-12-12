SIGN_MAP = {
    "Gt": ">",
    "Gte": ">=",
    "It": "<",
    "Ite": "<=",
    "Ne": "!="
}

INSERT = """INSERT INTO {table_name}({fields}) VALUES{values};"""

SELECT = """SELECT {fields} from {table_name} WHERE {filter_conditions}"""

DELETE = """DELETE FROM {table_name} WHERE {filter_conditions}"""
