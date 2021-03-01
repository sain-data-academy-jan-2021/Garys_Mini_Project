import * as templates from './templates.js'

const get_orders = () => {
    fetch('http://localhost:5000/orders')
        .then(res => res.json())
        .then(data => on_got_data('orders', data))
}

const get_table = (table) => {
    fetch(`http://localhost:5000/view/${table}`, {method: 'GET'})
        .then(res => res.json())
        .then(data => on_got_data(table, data))
    return false
}

const get_item = (table, id) => {
    fetch(`http://localhost:5000/view/${table}/${id}`)
        .then(res => res.json())
        .then(data => on_got_data(table + '_' + id, data))
    return false
}

const update_item = (table, id, data) => {
    fetch(`http://localhost:5000/view/${table}/${id}`, {
        method: 'POST',
        body: JSON.stringify(data),
        mode: 'no-cors',
        referrerPolicy: 'no-referrer',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(data => console.log(data))
    return false
}

const on_got_data = (name, data) => {
    localStorage.setItem(name, JSON.stringify(data))
}

const load_templates = () => {
    document.querySelectorAll('.template')
        .forEach(template => {
            let temp_name = template.textContent
            load_template(template, temp_name)
    })
}

const load_template = (node, name) => {
    node.innerHTML = templates[name]()
}

// Bind Global functions to window object
window.get_orders = get_orders
window.get_table = get_table
window.get_item = get_item
window.update_item = update_item

load_templates()

document.addEventListener('DOMContentLoaded', function () {
    let elems = document.querySelectorAll('.collapsible');
    let instances = M.Collapsible.init(elems, { accordion: false });
    instances.forEach((inst) => {
        inst.open()
    })
});