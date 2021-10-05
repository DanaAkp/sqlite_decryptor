function add_new_table() {
    let tbody = document.getElementById('tbody-columns')
    let rows = tbody.children
    let columns = []
    for(let i in rows){
        let input = rows[i].children
        let col = {
            'column_name': input[0],
            'column_type': input[1],
            'primary_key': input[2],
            'nullable': input[3]
        }
        columns.push(col)
    }
    // columns
}

function add_column_input() {
    let tbody = document.getElementById('tbody-columns')


}