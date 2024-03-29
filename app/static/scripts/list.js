let header = document.getElementById('header-id')
header.textContent = capitalize(header.textContent)
let entity_name = document.getElementById('entity_name').dataset.geocode;
create_table();

function create_table() {
    let table = document.getElementById('table-entity');
    if (table.childElementCount !== 0) {
        table.removeChild(table.lastElementChild);
        table.removeChild(table.lastElementChild);
    }
    let t_head = document.createElement('thead');
    const request = new XMLHttpRequest();
    request.open('GET', `/api/models/attributes/${entity_name}`, false);
    request.send();
    let json = JSON.parse(request.response).json_list;
    for (let i in json) {
        let th = document.createElement('th');
        th.textContent = capitalize(json[i]);
        th.className = "my_th"
        t_head.appendChild(th);
    }
    table.appendChild(t_head);

    request.open('GET', `/api/models/${entity_name}`, false);
    request.send();
    json = JSON.parse(request.response).json_list;
    let t_body = document.createElement('tbody');
    for (let i in json) {
        let row = document.createElement('tr');
        for (let j in json[i]) {
            let td = document.createElement('td');
            td.textContent = json[i][j];
            td.className = "my_td";
            row.appendChild(td);
        }
        const request_primary_key = new XMLHttpRequest();
        request_primary_key.open('GET', `/api/models/primary_key/${entity_name}`, false);
        request_primary_key.send();

        let id = json[i][JSON.parse(request_primary_key.response).primary_key];
        console.log(id);

        let column_edit = document.createElement('td');
        let input_edit = document.createElement('input');
        input_edit.type = 'button';
        input_edit.className = 'button_edit';
        let edit = edit_function(id);
        input_edit.onclick = function () {
            edit()
        };
        column_edit.appendChild(input_edit);
        row.appendChild(column_edit);

        let column_delete = document.createElement('td');
        let input_delete = document.createElement('input');
        input_delete.type = 'button';
        input_delete.className = 'button_delete';
        let del = delete_function(id);
        input_delete.onclick = function () {
            del()
        };
        column_delete.appendChild(input_delete);
        row.appendChild(column_delete);

        t_body.appendChild(row);
    }
    table.appendChild(t_body);
}

function delete_function(id) {
    return function () {
        const request = new XMLHttpRequest();
        request.open('DELETE', `/api/models/${entity_name}/${id}`, false);
        request.send();
        if (request.status !== 200)
            alert(JSON.parse(request.response).message);
        else {
            alert('Record deleted success.');
            create_table();
        }
    }
}

function edit_function(id) {
    return function () {
        window.location.href = `/sql_decrypter/edit/${entity_name}/${id}`
    }
}

function create_function() {
    window.location.href = `/sql_decrypter/create/${entity_name}`;
}