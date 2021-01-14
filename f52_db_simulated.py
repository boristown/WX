import mypsw
import mysql.connector
import common

def save_result(simulate_id, simulate_result):
    myconnector, mycursor = common.init_mycursor()
    statement = '''
    insert into
    `simulated` ( `simulate_id`, `simulate_result` )
    values ( %d, "%s" )
    ON DUPLICATE KEY UPDATE
    `simulate_id` = VALUES(`simulate_id`), 
    `simulate_result` = VALUES(`simulate_result`)
    ;
    ''' % (
        int(simulate_id),
        simulate_result
        )
    mycursor.execute(statement)
    myconnector.commit()
    return mycursor.rowcount

def read_result(simulate_id):
    myconnector, mycursor = common.init_mycursor()
    statement = '''
    select
    `simulate_id`,
    `simulate_result`
    from 
    `simulated`
    where 
    `simulate_id` = %d
    ;
    ''' % (
        int(simulate_id)
        )
    mycursor.execute(statement)
    list_results = mycursor.fetchall()
    simulate_result = ""
    for list_result in list_results:
        simulate_result = list_result[1]
    return simulate_result

def get_max_id():
    myconnector, mycursor = common.init_mycursor()
    statement = '''
    select max(`simulate_id`)
    from 
    `simulated`
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
