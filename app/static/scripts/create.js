let header = document.getElementById('header-id')
header.textContent = 'Create ' + capitalize(header.textContent)
let entity_name = document.getElementById('entity_name').dataset.geocode;
let input_attributes = document.getElementById('input-attributes');
const request = new XMLHttpRequest();
request.open('GET', `/api/models/attributes/${entity_name}`, false);
request.send();
let attributes = JSON.parse(request.response).json_list;

for (let i in attributes) {
    let paragraph = document.createElement('p');

    let label_attribute = document.createElement('label');
    label_attribute.textContent = capitalize(attributes[i]);

    let input_attribute = document.createElement('input');
    input_attribute.type = 'text';
    input_attribute.id = attributes[i];
    input_attribute.className = 'form-control';

    paragraph.appendChild(label_attribute);
    paragraph.appendChild(input_attribute);
    input_attributes.appendChild(paragraph);
}

function add_new_object() {
    const request = new XMLHttpRequest();
    request.open('POST', `/api/models/${entity_name}`, true);
    request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    let json = {};
    for (let i in attributes) {
        json[attributes[i]] = document.getElementById(attributes[i]).value;
    }
    request.send(JSON.stringify(json));
    request.onreadystatechange = function () {
        if (request.readyState === 4) {
            if (request.status === 201) {
                window.location.href = `/sql_decrypter/${entity_name}`;
            } else alert(JSON.parse(request.response).message);
        }
    }
}