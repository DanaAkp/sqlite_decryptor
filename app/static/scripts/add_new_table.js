function add_new_table() {
    let tbody = document.getElementById('tbody-columns')
    let rows = tbody.children
    let columns = []
    for(let i in rows){
        let input = rows[i].children
        console.log(input[0])
        let col = {
            'column_name': input[0],
            'column_type': input[1],
            'primary_key': input[2],
            'nullable': input[3]
        }
        columns.push(col)
    }
    // TODO сделать запрос для добавления новой  таблицы
}

function add_column_input() {
    let tbody = document.getElementById('tbody-columns')

    let row = document.createElement('tr')
    let col_name = document.createElement('td')
    let input_name = document.createElement('input')
    input_name.type = 'text'
    col_name.appendChild(input_name)
    row.appendChild(col_name)

    let col_type = document.createElement('td')
    let input_type = document.createElement('input')
    input_type.type = 'text'
    col_type.appendChild(input_type)
    row.appendChild(col_type)

    let col_pk = document.createElement('td')
    let input_pk = document.createElement('input')
    col_pk.appendChild(input_pk)
    row.appendChild(col_pk)

    let col_nullable = document.createElement('td')
    let input_nullable = document.createElement('input')
    input_nullable.type = 'text'
    col_nullable.appendChild(input_nullable)
    row.appendChild(col_nullable)

    tbody.appendChild(row)
}