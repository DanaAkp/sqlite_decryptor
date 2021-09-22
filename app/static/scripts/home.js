
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

        let input_decrypt_file_db = document.getElementById('unencrypted-database-file')
        let password_for_encrypt = document.getElementById('password-for-encrypt-file')
        input_decrypt_file_db.onchange = e => {
            document.getElementById('button-encrypt').onclick = () => {
                let file = e.target.files[0];
                let reader = new FileReader();
                reader.readAsArrayBuffer(file);
                reader.onload = reader_event => {
                    let content = reader_event.target.result;
                    let arr = new Uint8Array(content);
                    let hex = to_hex_string(arr);
                    const request = new XMLHttpRequest();
                    request.open('POST', '/api/sqlite_encryptor', true);
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
                                input_decrypt_file_db.value = '';
                            } else alert(response.message);
                        }
                    }
                }
            }
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


        function to_hex_string(byte_array) {
            return Array.prototype.map.call(byte_array, function (byte) {
                return ('0' + (byte & 0xFF).toString(16)).slice(-2);
            }).join('');
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
