
const generate_table = (page) => {
    // Generate Table Headers
    let table_header = document.querySelector('.table_header')
    const rows = JSON.parse(localStorage.getItem('products'))
    let headers = Object.keys(rows[0])
    let header_html = ''
    headers.forEach((header) => {
        header_html += `<th>${header}</th>`
    })
    header_html += `<th>Action</th>`
    table_header.innerHTML = header_html

    // Generate Pages

    let max_length = 10
    let total_length = Object.keys(rows).length
    let total_pages = Math.ceil(total_length / max_length)
    let current_page = page < 1 ? 1 : page > total_pages ? total_pages : page
    let page_el = document.querySelector('.pagination')
    let page_html = `<li class="disabled" onclick="page_down(${current_page})"><a href="#!"><i class="material-icons">chevron_left</i></a></li>`
    for (let i = 1; i <= total_pages; i++){
        page_html += `<li class="waves-effect ${i == current_page ? 'active orange' : ''}" onclick="page_set(${i})"><a href="">${i}</a></li>`
    }
    page_html += `<li class="waves-effect" onclick="page_up(${current_page})"><a href="#!"><i class="material-icons">chevron_right</i></a></li>`

    page_el.innerHTML = page_html

    // Generate Table Body
    let table_body = document.querySelector('.table_body')
    let body = ''
    let to = ((current_page - 1) * max_length + max_length) < total_length ? ((current_page - 1) * max_length + max_length) : total_length
            
    for (let row of rows.slice((current_page - 1) * max_length, to)) {
        let html = '<tr>'
        let id
        for (let field of headers) {
            if (field == 'id') {
                id = row[field]
            }
            if (field == 'price') {
                row[field] = parseFloat(row[field]).toFixed(2)
            }
            html += `<td>${row[field]}</td>`
        }
        html += `<td onclick="view_item(${id})"><i class="material-icons action">edit</i></td>`
        html += '</tr>'
        body += html
    }
    table_body.innerHTML = body

}

const view_item = (id) => {
    window.location.href = `product-view.html?id=${id}`
}

const page_up = (current_page) => {
    generate_table(current_page + 1)
}

const page_down = (current_page) => {
    generate_table(current_page - 1)
}

const page_set = (page) => {
    generate_table(page)
}

const refresh = () => {
    localStorage.clear()
    window.get_table('products')    
}

if (localStorage.getItem('products') == undefined) {
    window.get_table('products')
}

window.page_up = page_up
window.page_down = page_down
window.page_set = page_set
window.refresh = refresh
window.view_item = view_item

generate_table(1)
