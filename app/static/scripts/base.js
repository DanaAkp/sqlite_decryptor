let div_f = document.createElement('div')
div_f.id = 'id-div-field'
fill_entity_list();

function fill_entity_list() {
    const request = new XMLHttpRequest();
    request.open('GET', '/api/models', false);
    request.send();
    if (request.status === 200) {
        let entity_list = document.getElementById('list_entity');
        entity_list.innerText = '';
        let json = JSON.parse(request.response).json_list;
        for (let i in json) {
            let u_list = document.createElement('ul');
            u_list.className = "nav navbar-nav";
            let list_item = document.createElement('li');
            let a = document.createElement('a');
            a.href = `/sql_decrypter/${json[i]}`;
            a.textContent = capitalize(json[i]);

            list_item.appendChild(a);
            u_list.appendChild(list_item);
            entity_list.appendChild(u_list);
        }
        let u_list = document.createElement('ul');
        u_list.className = "nav navbar-nav";
        let list_item = document.createElement('li');
        let a = document.createElement('a');
        a.href = `/sql_decrypter/add_new_table`;
        a.textContent = 'New table';

        list_item.appendChild(a);
        u_list.appendChild(list_item);
        entity_list.appendChild(u_list);
    }
}

function capitalize(s) {
    let buf_list = s.split('_')
    if (buf_list.length === 1) {
        buf_list = s.split(/(?=[A-Z])/).map(x => x.toLowerCase())
    }
    s = buf_list.join(' ').trim()
    return s[0].toUpperCase() + s.slice(1);
}

/* Установите ширину боковой панели на 250 пикселей (показать его) */
function openNav() {
    document.getElementById("mySidepanel").style.width = "250px";
}

function save_file(file_name, url_file) {
    let a = document.createElement("a");
    a.style = "display: none";
    document.body.appendChild(a);
    a.href = url_file;
    a.download = file_name;
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
}


function save_encrypted_db_file() {
    const request = new XMLHttpRequest();
    request.open('GET', '/api/sql_decrypter', false);
    request.send();

    let textData = JSON.parse(request.response).encrypted_file;
    let blobData = new Blob([textData], {type: "text/plain"});
    let url = window.URL.createObjectURL(blobData);
    save_file('example.txt', url);
}


function clear_current_db_file() {
    const request = new XMLHttpRequest();
    request.open('DELETE', '/api/sql_decrypter', false);
    request.send();
    if (request.status === 200) {
        window.location.reload();
        alert('The current database file has been cleaned up successfully.')
    }
}

/* Установите ширину боковой панели в 0 (скройте ее) */
function closeNav() {
    document.getElementById("mySidepanel").style.width = "0";
}


function head3(content, name) {
    let head3 = document.createElement('H3')
    head3.textContent = name
    content.appendChild(head3)
    content.appendChild(document.createElement('br'))
}


function fill_encrypt_postgresql_db() {
    let host = document.createElement('input')
    host.type = 'text'
    host.id = "id-input-host"
    host.className = 'form-control'
    host.placeholder = "Enter host"
    div_f.appendChild(host)
    div_f.appendChild(document.createElement('br'))

    let port = document.createElement('input')
    port.type = 'text'
    port.id = "id-input-port"
    port.className = 'form-control'
    port.placeholder = "Enter port"
    div_f.appendChild(port)
    div_f.appendChild(document.createElement('br'))

    let db_name = document.createElement('input')
    db_name.type = 'text'
    db_name.id = 'id-input-db-name'
    db_name.className = 'form-control'
    db_name.placeholder = "Enter database name"
    div_f.appendChild(db_name)
    div_f.appendChild(document.createElement('br'))

    let username = document.createElement('input')
    username.type = 'text'
    username.id = "id-input-username"
    username.className = 'form-control'
    username.placeholder = "Enter username"
    div_f.appendChild(username)
    div_f.appendChild(document.createElement('br'))

    let db_password = document.createElement('input')
    db_password.type = 'text'
    db_password.id = "id-input-db-password"
    db_password.className = 'form-control'
    db_password.placeholder = "Enter database password"
    div_f.appendChild(db_password)
    div_f.appendChild(document.createElement('br'))


    let input_password = document.createElement('input')
    input_password.type = 'password'
    input_password.id = "password-for-encrypt-file"
    input_password.placeholder = "Enter password"
    input_password.className = 'form-control'
    div_f.appendChild(input_password)

    div_f.appendChild(document.createElement('br'))

    let btn = document.createElement('input')
    btn.type = "button"
    btn.id = "button-encrypt-postgresql"
    btn.value = "Encrypt"
    btn.className = 'btn btn-default'
    div_f.appendChild(btn)


    btn.onclick = () => {
        let host = document.getElementById("id-input-host")
        let port = document.getElementById("id-input-port")
        let username = document.getElementById("id-input-username")
        let db_password = document.getElementById("id-input-db-password")
        let db_name = document.getElementById("id-input-db-name")
        let cont = JSON.stringify({
            'host': host.value,
            'port': port.value,
            'username': username.value,
            'db_password': db_password.value,
            'db_name': db_name.value
        })
        let arr = new Uint8Array(cont);
        let hex = to_hex_string(arr);
        const request = new XMLHttpRequest();
        request.open('POST', '/api/sql_encryptor', true);
        request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
        request.send(JSON.stringify({
            'database_file': hex,
            'password': input_password.value
        }));

        request.onreadystatechange = function () {
            if (request.readyState === 4) {
                let response = JSON.parse(request.response);
                if (response.message === undefined) {
                    let textData = JSON.parse(request.response).encrypted_file;
                    let blobData = new Blob([textData], {type: "text/plain"});
                    let url = window.URL.createObjectURL(blobData);
                    save_file('example.txt', url);

                    input_password.value = '';
                    host.value = '';
                    port.value = '';
                    db_name.value = '';
                    db_password.value = '';
                    username.value = '';
                } else alert(response.message);
            }
        }
    }
}


function to_hex_string(byte_array) {
    return Array.prototype.map.call(byte_array, function (byte) {
        return ('0' + (byte & 0xFF).toString(16)).slice(-2);
    }).join('');
}


function checked_sqlite() {
    div_f.innerHTML = ''
    if (document.getElementById('id-checkbox').checked) {
        let div_group = document.createElement('div')
        div_group.className = 'form-control'

        let lbl = document.createElement('label')
        lbl.className = "form-label"
        lbl.textContent = "Choose file"
        div_group.appendChild(lbl)

        let input_file = document.createElement('input')
        input_file.type = "file"
        input_file.className = "form-control"
        input_file.id = "unencrypted-database-file-sql"
        lbl.appendChild(input_file)

        div_f.appendChild(div_group)
        div_f.appendChild(document.createElement('br'))

        let input_password = document.createElement('input')
        input_password.type = 'password'
        input_password.id = "password-for-encrypt-file"
        input_password.placeholder = "Enter password"
        input_password.className = 'form-control'
        div_f.appendChild(input_password)
        div_f.appendChild(document.createElement('br'))

        let btn = document.createElement('input')
        btn.type = "button"
        btn.id = "button-encrypt-sql"
        btn.value = "Encrypt"
        btn.className = 'btn btn-default'


        input_file.onchange = e => {
            btn.onclick = () => {
                let file = e.target.files[0];
                let reader = new FileReader();
                reader.readAsArrayBuffer(file);
                reader.onload = reader_event => {
                    let cont = reader_event.target.result;
                    let arr = new Uint8Array(cont);
                    let hex = to_hex_string(arr);
                    const request = new XMLHttpRequest();
                    request.open('POST', '/api/sql_encryptor', true);
                    request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
                    request.send(JSON.stringify({
                        'database_file': hex,
                        'password': input_password.value
                    }));

                    request.onreadystatechange = function () {
                        if (request.readyState === 4) {
                            let response = JSON.parse(request.response);
                            if (response.message === undefined) {
                                let textData = JSON.parse(request.response).encrypted_file;
                                let blobData = new Blob([textData], {type: "text/plain"});
                                let url = window.URL.createObjectURL(blobData);
                                save_file('example.txt', url);

                                input_password.value = '1234567890123456';
                                input_file.value = '';
                            } else alert(response.message);
                        }
                    }
                }
            }
        }

        div_f.appendChild(btn)
    } else {
        fill_encrypt_postgresql_db()
    }
}


function encrypt_nav() {
    closeNav()
    let content = document.getElementById('id-page-content')
    content.innerHTML = ''
    div_f.innerHTML = ''

    head3(content, 'Upload database for encrypt')

    let lbl_switch = document.createElement('label')
    lbl_switch.className = "switch"

    let input_sqlite = document.createElement('input')
    input_sqlite.type = 'checkbox'
    input_sqlite.id = 'id-checkbox'
    input_sqlite.onclick = checked_sqlite
    lbl_switch.appendChild(input_sqlite)

    let span = document.createElement('span')
    span.className = "slider round"
    lbl_switch.appendChild(span)

    let lbl_sqlite = document.createElement('label')
    lbl_sqlite.textContent = 'SQLite'
    lbl_sqlite.style.marginLeft = '15px'
    lbl_sqlite.style.fontSize = '15px'

    let lbl_postgresql = document.createElement('label')
    lbl_postgresql.textContent = 'PostgreSQL'
    lbl_postgresql.style.marginRight = '15px'
    lbl_postgresql.style.fontSize = '15px'

    content.appendChild(lbl_postgresql)
    content.appendChild(lbl_switch)
    content.appendChild(lbl_sqlite)

    content.appendChild(div_f)

    fill_encrypt_postgresql_db()
}


function decrypt_nav() {
    closeNav()
    let content = document.getElementById('id-page-content')
    content.innerHTML = ''

    head3(content, 'Upload database encrypted file')

    let div_group = document.createElement('div')
    div_group.className = 'form-control'

    let lbl = document.createElement('label')
    lbl.className = "form-label"
    lbl.textContent = "Choose file"
    div_group.appendChild(lbl)

    let input_file = document.createElement('input')
    input_file.type = "file"
    input_file.className = "form-control"
    input_file.id = 'encrypted-file-db'
    lbl.appendChild(input_file)

    content.appendChild(div_group)
    content.appendChild(document.createElement('br'))

    let input_text = document.createElement('input')
    input_text.type = "password"
    input_text.id = "password-for-decrypt-file"
    input_text.className = 'form-control'
    input_text.placeholder = "Enter password"
    content.appendChild(input_text)
    content.appendChild(document.createElement('br'))

    let btn = document.createElement('input')
    btn.type = "button"
    btn.id = "button-upload"
    btn.value = "Upload file"
    btn.className = 'btn btn-default'


    input_file.onchange = e => {
        btn.onclick = () => {
            let file = e.target.files[0];
            let reader = new FileReader();
            reader.readAsText(file);
            reader.onload = reader_event => {
                let content = reader_event.target.result;
                const request = new XMLHttpRequest();
                request.open('POST', '/api/sql_decrypter', true);
                request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
                let json = JSON.stringify({
                    database_file: content,
                    password: input_text.value
                });
                console.log(input_text.value);
                console.log(json);
                request.send(json);
                request.onreadystatechange = function () {
                    if (request.readyState === 4) {
                        let response = JSON.parse(request.response);
                        if (response.result === true) {
                            fill_entity_list();
                            input_text.value = '1234567890123456';
                            input_file.value = '';
                        } else alert(response.message);
                    }
                }
            }
        }
    }

    content.appendChild(btn)
}
