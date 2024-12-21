from rm_storage import CON


tables = (
    ('CREATE TABLE resource_type ('
     'id INTEGER PRIMARY KEY AUTOINCREMENT,'
     'name VARCHAR(50)'
     ');'),
    ('CREATE TABLE user ('
     'id INTEGER PRIMARY KEY AUTOINCREMENT,'
     'name VARCHAR(50)'
     ');'),
    ('CREATE TABLE resource ('
     'id INTEGER PRIMARY KEY AUTOINCREMENT,'
     'type_id INTEGER NOT NULL REFERENCES resource_type(id),'
     'name VARCHAR(50)'
     ');'),
    ('CREATE TABLE reservation ('
     'resource_id INTEGER NOT NULL REFERENCES resource(id) ON DELETE NO ACTION ON UPDATE NO ACTION,'
     'reserved_by INTEGER REFERENCES user(id) ON DELETE NO ACTION ON UPDATE NO ACTION'
     ');'),
)

data = (
    'INSERT INTO user (name) VALUES ("YATF"), ("k.gordeev"), ("a.shevelev"), ("a.naumov");',
    'INSERT INTO resource_type (name) VALUES ("epc_node"), ("enb_node"), ("ue"), ("webui");',
    'INSERT INTO resource (type_id, name) VALUES (1, "EPC-node-1"), (1, "EPC-node-2"), (1, "EPC-node-3");',
    'INSERT INTO resource (type_id, name) VALUES (2, "ENB-node-1"), (2, "ENB-node-2"), (2, "ENB-node-3");',
)


if __name__ == '__main__':
    with CON:
        print('Create tables:')
        for i in tables:
            print(i)
            CON.execute(i)

        print('Add data:')
        for i in data:
            print(i)
            CON.execute(i)
