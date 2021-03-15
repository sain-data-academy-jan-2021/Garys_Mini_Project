export let nav_template = () => {
    return `<div class="navbar-fixed">
        <nav>
            <div class="nav-wrapper blue lighten-2">
                <a href="./" class="brand-logo center">F&B Ordering</a>
            </div>
        </nav>
    </div>`
}

export let side_nav = () => {
    return `<div class="side_nav">
            <ul class="collapsible">
                <li>
                    <div class="collapsible-header">
                        <i class="material-icons">dashboard</i>
                        Dashboard
                    </div>
                    <div class="collapsible-body">
                        <a href="./index.html"><i class="material-icons">home</i> Home</a>
                        <a href="#"><i class="material-icons">list</i> View Open Orders</a>
                        <a href="#"><i class="material-icons">person_pin_circle</i> Courier Status</a>
                    </div>
                </li>
                <li>
                    <div class="collapsible-header">
                        <i class="material-icons">add_circle_outline</i>
                        Update
                    </div>
                    <div class="collapsible-body">
                        <a href="./products.html"><i class="material-icons">playlist_add</i> Products</a>
                        <a href="./couriers.html"><i class="material-icons">person_add</i> Couriers</a>
                        <a href="#"><i class="material-icons">assignment</i> Orders</a>
                    </div>
                </li>
                <li>
                    <div class="collapsible-header">
                        <i class="material-icons">settings</i>
                        System Maintainance
                    </div>
                    <div class="collapsible-body">
                        <a href="./products.html"><i class="material-icons">playlist_add_check</i> Products</a>
                        <a href="./couriers.html"><i class="material-icons">person_pin</i> Couriers</a>
                    </div>
                </li>
            </ul>
        </div>
    `
}