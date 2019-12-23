SIGN_MAP = {
    "Gt": " > ",
    "Gte": " >= ",
    "It": " < ",
    "Ite": " <= ",
    "Ne": " != ",
    "IN": " in "
}

INSERT = """INSERT INTO {table_name}({fields}) VALUES{values};"""

SELECT = """SELECT {fields} from {table_name} {filter_conditions}"""

DELETE = """DELETE FROM {table_name} {filter_conditions}"""

UPDATE = """UPDATE {table_name} SET {update_conditions} {filter_conditions}"""

JOIN = """ {join_direction} JOIN {join_table_name} {join_conditions}"""
