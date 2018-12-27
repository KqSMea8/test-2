def protectSql(sql):
    if sql.__class__ is str:
        return sql.replace(' ','').replace(';','')
    else:
        return sql