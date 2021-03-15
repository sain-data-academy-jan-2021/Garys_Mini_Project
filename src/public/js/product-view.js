const get_item = () => {
    let name_field = document.querySelector('#item_name')    
    let price_field = document.querySelector('#item_price')    
    let cat_field = document.querySelector('#catagory')    
    let item = JSON.parse(localStorage.getItem(`products_${urlParams.get('id')}`))[0]

    name_field.value = item['name'].toUpperCase()
    price_field.value = parseFloat(item['price']).toFixed(2)
    cat_field.value = item['catagory']
}

const refresh = () => {
    localStorage.clear()
    window.get_item('products', urlParams.get('id'))
}


const urlParams = new URLSearchParams(window.location.search)
if (localStorage.getItem(`products_${urlParams.get('id')}`) == undefined) {
    window.get_item('products', urlParams.get('id'))
}

const save = () => {
    let name = document.querySelector('#item_name').value.toLowerCase()
    let price = document.querySelector('#item_price').value
    let catagory = document.querySelector('#catagory').value
    
    let obj = {
        name,
        price,
        catagory
    }

    window.update_item('products', urlParams.get('id'), obj)
    window.location.href = './products.html'
}

window.refresh = refresh
window.save = save

document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});
});

get_item()