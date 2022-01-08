encrypt_nav()
let input_encrypted_file_db = document.getElementById('encrypted-file-db');
let password_for_decrypt = document.getElementById('password-for-decrypt-file');
input_encrypted_file_db.onchange = e => {
    document.getElementById('button-upload').onclick = () => {
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
                password: password_for_decrypt.value
            });
            console.log(password_for_decrypt.value);
            console.log(json);
            request.send(json);
            request.onreadystatechange = function () {
                if (request.readyState === 4) {
                    let response = JSON.parse(request.response);
                    if (response.result === true) {
                        fill_entity_list();
                        password_for_decrypt.value = '1234567890123456';
                        input_encrypted_file_db.value = '';
                    } else alert(response.message);
                }
            }
        }
    }
}

let input_decrypt_file_db_sqlite = document.getElementById('unencrypted-database-file-sql')
let password_for_encrypt = document.getElementById('password-for-encrypt-file')
input_decrypt_file_db_sqlite.onchange = e => {
    document.getElementById('button-encrypt-sql').onclick = () => {
        let file = e.target.files[0];
        let reader = new FileReader();
        reader.readAsArrayBuffer(file);
        reader.onload = reader_event => {
            let content = reader_event.target.result;
            let arr = new Uint8Array(content);
            let hex = to_hex_string(arr);
            const request = new XMLHttpRequest();
            request.open('POST', '/api/sql_encryptor', true);
            request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
            request.send(JSON.stringify({
                'database_file': hex,
                'password': password_for_encrypt.value
            }));

            request.onreadystatechange = function () {
                if (request.readyState === 4) {
                    let response = JSON.parse(request.response);
                    if (response.message === undefined) {
                        let textData = JSON.parse(request.response).encrypted_file;
                        let blobData = new Blob([textData], {type: "text/plain"});
                        let url = window.URL.createObjectURL(blobData);
                        save_file('example.txt', url);

                        password_for_encrypt.value = '1234567890123456';
                        input_decrypt_file_db_sqlite.value = '';
                    } else alert(response.message);
                }
            }
        }
    }
}

let host = document.getElementById("id-input-host")
let port = document.getElementById("id-input-port")
let username = document.getElementById("id-input-username")
let db_password = document.getElementById("id-input-db-password")
let db_name = document.getElementById("id-input-db-name")
// let input_decrypt_file_db_postgresql = document.getElementById('unencrypted-database-file-sql')
// // let password_for_encrypt = document.getElementById('password-for-encrypt-file')
// input_decrypt_file_db_postgresql.onchange = e => {
    document.getElementById('button-encrypt-postgresql').onclick = () => {
        // let file = e.target.files[0];
        // let reader = new FileReader();
        // reader.readAsArrayBuffer(file);
        // reader.onload = reader_event => {
            let content = JSON.stringify({
                'host': host.value,
                'port': port.value,
                'username': username.value,
                'db_password': db_password.value,
                'db_name': db_name.value
            })
            let arr = new Uint8Array(content);
            let hex = to_hex_string(arr);
            const request = new XMLHttpRequest();
            request.open('POST', '/api/sql_encryptor', true);
            request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
            request.send(JSON.stringify({
                'database_file': hex,
                'password': password_for_encrypt.value
            }));

            request.onreadystatechange = function () {
                if (request.readyState === 4) {
                    let response = JSON.parse(request.response);
                    if (response.message === undefined) {
                        let textData = JSON.parse(request.response).encrypted_file;
                        let blobData = new Blob([textData], {type: "text/plain"});
                        let url = window.URL.createObjectURL(blobData);
                        save_file('example.txt', url);

                        password_for_encrypt.value = '1234567890123456';
                        input_decrypt_file_db_sqlite.value = '';
                    } else alert(response.message);
                }
            }
        // }
    }
// }

function to_hex_string(byte_array) {
    return Array.prototype.map.call(byte_array, function (byte) {
        return ('0' + (byte & 0xFF).toString(16)).slice(-2);
    }).join('');
}
