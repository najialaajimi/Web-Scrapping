async function searchProduct() {
    const productName = document.getElementById('productName').value;
    if (!productName) {
        alert('Please enter a product name!');
        return;
    }

    const response = await fetch(`http://localhost:5000/api/products/search?name=${encodeURIComponent(productName)}`);

    
    if (!response.ok) {
        alert('Error fetching product data');
        return;
    }

    const products = await response.json();
    console.log("Received products:", products); // Afficher les données reçues
    displayResults(products);
}

function displayResults(products) {
    const tableBody = document.querySelector('#productTable tbody');
    tableBody.innerHTML = '';

    if (!Array.isArray(products)) {
        console.error('Expected an array but got:', products);
        return;
    }

    products.forEach(product => {
        const row = tableBody.insertRow();
        row.insertCell().textContent = product.Name;
        row.insertCell().textContent = product.Price;
        row.insertCell().textContent = product.Availability;
        row.insertCell().textContent = product.Website;
        const urlCell = row.insertCell();
        const link = document.createElement('a');
        link.href = product.URL;
        link.target = "_blank";
        link.textContent = 'View Product';
        urlCell.appendChild(link);
    });
}
