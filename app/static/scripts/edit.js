let header = document.getElementById('header-id')
header.textContent = 'Edit ' + capitalize(header.textContent)
let entity_name = document.getElementById('entity_name').dataset.geocode;
        let id = document.getElementById('entity_id').dataset.geocode;
        let input_attributes = document.getElementById('input-attributes');

        const request = new XMLHttpRequest();
        request.open('GET', `/api/models/attributes/${entity_name}`, false);
        request.send();
        let attributes = JSON.parse(request.response).json_list;

        request.open('GET', `/api/models/${entity_name}/${id}`, false);
        request.send();
        console.log(request.response);
        let object_data = JSON.parse(request.response);

        for (let i in attributes) {
            let paragraph = document.createElement('p');
            console.log(attributes[i]);
            let label_attribute = document.createElement('label');
            label_attribute.textContent = capitalize(attributes[i]);

            let input_attribute = document.createElement('input');
            input_attribute.type = 'text';
            input_attribute.id = attributes[i];
            input_attribute.className = 'form-control';

            input_attribute.value = object_data[attributes[i]];

            paragraph.appendChild(label_attribute);
            paragraph.appendChild(input_attribute);
            input_attributes.appendChild(paragraph);
        }

        function edit_object() {
            const request = new XMLHttpRequest();
            request.open('PUT', `/api/models/${entity_name}/${id}`, true);
            request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
            let json = {};
            for (let i in attributes) {
                json[attributes[i]] = document.getElementById(attributes[i]).value;
            }
            request.send(JSON.stringify(json));
            request.onreadystatechange = function () {
                if (request.readyState === 4) {
                    console.log(request.response);
                    if (request.status === 200) {
                        window.location.href = `/sql_decrypter/${entity_name}`;
                    } else alert(JSON.parse(request.response).message);
                }
            }
        }

        function cancel() {
            window.location.href = `/sql_decrypter/${entity_name}`;
        }