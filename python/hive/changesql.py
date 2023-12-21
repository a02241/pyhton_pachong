with open('/home/hadoop/output/test.sql', 'r') as file:
    sql_statements = file.read().split(';\n')

with open('/home/hadoop/output/new_test.sql', 'w') as file:
    for sql_statement in sql_statements:
        if sql_statement.strip():
            file.write("SELECT \"Executing SQL: " + sql_statement.strip().replace('\"', '\'') + "\";\n")
            file.write(sql_statement.strip() + ";\n")
