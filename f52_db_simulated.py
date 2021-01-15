import mypsw
import mysql.connector
import common

def save_result(simulate_id, simulate_result):
    myconnector, mycursor = common.init_mycursor()
    statement = '''
    insert into
    `simulate` ( `simulate_id`, `simulate_result` )
    values ( %s, %s )
    ON DUPLICATE KEY UPDATE
    `simulate_id` = VALUES(`simulate_id`), 
    `simulate_result` = VALUES(`simulate_result`)
    ;
    '''
    print(simulate_result)
    mycursor.execute(statement, (str(simulate_id), simulate_result.encode("utf-8")))
    myconnector.commit()
    return mycursor.rowcount

def read_result(simulate_id):
    myconnector, mycursor = common.init_mycursor()
    statement = '''
    select
    `simulate_id`,
    `simulate_result`
    from 
    `simulate`
    where 
    `simulate_id` = %s
    ;
    '''
    mycursor.execute(statement, (str(simulate_id), ))
    list_results = mycursor.fetchall()
    simulate_result = ""
    for list_result in list_results:
        simulate_result = list_result[1].decode("utf-8")
    return simulate_result

def get_max_id():
    myconnector, mycursor = common.init_mycursor()
    statement = '''
    select max(`simulate_id`)
    from 
    `simulate`
    ;
    '''
    mycursor.execute(statement)
    list_results = mycursor.fetchall()
    max_id = 0
    for list_result in list_results:
        if list_result[0]:
            max_id = int(list_result[0])
    return max_id

if __name__ == '__main__':
    max_id = get_max_id()
    print("max = " + str(max_id))
    next_id = max_id + 1
    save_result(next_id, "test result 001")
    result = read_result(next_id)
    print("result = " + result)
