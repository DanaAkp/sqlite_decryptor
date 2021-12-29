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
