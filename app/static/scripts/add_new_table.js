function add_new_table() {
    let tbody = document.getElementById('tbody-columns')
    let rows = tbody.children
    let columns = []
    for (let i of rows) {
        let inputs = i.children
        // console.log(inputs[0].children[0].value)
        let col = {
            'column_name': inputs[0].children[0].value,
            'column_type': inputs[1].children[0].value,
            'primary_key': inputs[2].children[0].value,
            'nullable': inputs[3].children[0].value
        }
        columns.push(col)
    }
    // TODO сделать запрос для добавления новой  таблицы
    const request = new XMLHttpRequest();
    request.open('POST', `/api/models`, true);
    request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    request.send(JSON.stringify(columns));
}

function add_column_input() {
    let tbody = document.getElementById('tbody-columns')

    let row = document.createElement('tr')
    let col_name = document.createElement('td')
    let input_name = document.createElement('input')
    input_name.type = 'text'
    input_name.className = 'form-control'
    col_name.appendChild(input_name)
    row.appendChild(col_name)

    let col_type = document.createElement('td')
    let input_type = document.createElement('input')
    input_type.type = 'text'
    input_type.className = 'form-control'
    col_type.appendChild(input_type)
    row.appendChild(col_type)

    let col_pk = document.createElement('td')
    let input_pk = document.createElement('input')
    input_pk.className = 'form-control'
    col_pk.appendChild(input_pk)
    row.appendChild(col_pk)

    let col_nullable = document.createElement('td')
    let input_nullable = document.createElement('input')
    input_nullable.type = 'text'
    input_nullable.className = 'form-control'
    col_nullable.appendChild(input_nullable)
    row.appendChild(col_nullable)

    tbody.appendChild(row)
}