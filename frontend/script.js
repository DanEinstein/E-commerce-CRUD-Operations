const API_URL = "http://127.0.0.1:8000";
const productList = document.getElementById('product-list');
const loadingSpinner = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const refreshBtn = document.getElementById('refreshBtn');
const productForm = document.getElementById('product-form');
const formMessage = document.getElementById('form-message');
const editModal = document.getElementById('edit-modal');
const editForm = document.getElementById('edit-product-form');
const closeModalBtn = document.getElementById('close-modal-btn');


// Function to fetch and display products
const fetchProducts = async () => {
    loadingSpinner.classList.remove('hidden');
    errorMessage.classList.add('hidden');
    productList.innerHTML = ''; // Clear previous content

    try {
        const response = await fetch(`${API_URL}/products`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.products && data.products.length > 0) {
            data.products.forEach(product => {
                const productCard = document.createElement('div');
                productCard.className = 'bg-gray-50 p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300';
                productCard.dataset.productId = product.product_id; // Store product ID

                productCard.innerHTML = `
                    <h3 class="text-xl font-bold text-gray-800">${product.name}</h3>
                    <p class="text-gray-600 mt-2">${product.description || 'No description provided.'}</p>
                    <div class="mt-4 flex items-center justify-between">
                        <span class="text-lg font-semibold text-indigo-600">$${product.price.toFixed(2)}</span>
                        <span class="text-sm text-gray-500">Stock: ${product.stock_quantity}</span>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-200 flex justify-end gap-2">
                        <button class="edit-btn px-3 py-1 text-sm font-medium text-indigo-600 bg-indigo-100 rounded-md hover:bg-indigo-200">
                            Edit
                        </button>
                        <button class="delete-btn px-3 py-1 text-sm font-medium text-red-600 bg-red-100 rounded-md hover:bg-red-200">
                            Delete
                        </button>
                    </div>
                `;
                productList.appendChild(productCard);
            });
        } else {
            productList.innerHTML = '<p class="text-center text-gray-500 col-span-full">No products found. Add some using the form above!</p>';
        }

    } catch (error) {
        console.error("Fetch error:", error);
        // handling network errors
        if (error instanceof TypeError && error.message === 'Failed to fetch') {
            errorMessage.textContent = 'Network error: Could not connect to the backend. Is the server running?';
        } else {
            errorMessage.textContent = `An error occurred: ${error.message}`;
        }
        errorMessage.classList.remove('hidden');    
    } finally {
        loadingSpinner.classList.add('hidden');
    }
};

// Function to handle form submission and add a new product
const handleFormSubmit = async (event) => {
    event.preventDefault();
    formMessage.classList.add('hidden');

    const formData = new FormData(productForm);
    const newProduct = {
        name: formData.get('name'),
        price: parseFloat(formData.get('price')),
        description: formData.get('description'),
        stock_quantity: parseInt(formData.get('stock_quantity'))
    };

    try {
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newProduct)
        });

        const result = await response.json();

        if (response.ok) {
            formMessage.textContent = 'Product added successfully!';
            formMessage.classList.remove('hidden');
            formMessage.classList.remove('text-red-500');
            formMessage.classList.add('text-green-500');
            productForm.reset(); // Clear the form
            fetchProducts(); // Refresh the product list
        } else {
            // Use the detail message from the server if available, otherwise a generic message.
            const errorMessage = result && result.detail 
                ? result.detail 
                : `Failed to add product. Server responded with status: ${response.status}`;
            throw new Error(errorMessage);
        }
    } catch (error) {
        console.error("Error adding product:", error);
        formMessage.textContent = `Error: ${error.message}`;
        formMessage.classList.remove('hidden');
        formMessage.classList.remove('text-green-500');
        formMessage.classList.add('text-red-500');
    }
};

// Function to delete a product
const deleteProduct = async (productId) => {
    if (!confirm('Are you sure you want to delete this product?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/products/${productId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Remove the product card from the DOM
            document.querySelector(`[data-product-id='${productId}']`).remove();
        } else {
            let errorMsg = `Failed to delete product. Status: ${response.status}`;
         
            if (response.headers.get('content-type')?.includes('application/json')) {
                const result = await response.json();
                errorMsg = result.detail || errorMsg;
            }
            throw new Error(errorMsg);
        }
    } catch (error) {
        console.error("Error deleting product:", error);
        alert(`Error: ${error.message}`);
    }
};

// Function to open and populate the edit modal
const openEditModal = async (productId) => {
    try {
        const response = await fetch(`${API_URL}/products/${productId}`);
        if (!response.ok) throw new Error('Failed to fetch product details.');
        
        const { product } = await response.json();

        // Populate the form in the modal
        editForm.querySelector('#edit-product-id').value = product.product_id;
        editForm.querySelector('#edit-name').value = product.name;
        editForm.querySelector('#edit-price').value = product.price;
        editForm.querySelector('#edit-stock_quantity').value = product.stock_quantity;
        editForm.querySelector('#edit-description').value = product.description || '';

        editModal.classList.remove('hidden');
    } catch (error) {
        console.error("Error opening edit modal:", error);
        alert(`Error: ${error.message}`);
    }
};

// Function to handle edit form submission
const handleEditSubmit = async (event) => {
    event.preventDefault();
    const productId = editForm.querySelector('#edit-product-id').value;
    const updatedProduct = {
        name: editForm.querySelector('#edit-name').value,
        price: parseFloat(editForm.querySelector('#edit-price').value),
        stock_quantity: parseInt(editForm.querySelector('#edit-stock_quantity').value),
        description: editForm.querySelector('#edit-description').value
    };

    try {
        const response = await fetch(`${API_URL}/products/${productId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedProduct)
        });

        if (response.ok) {
            editModal.classList.add('hidden');
            fetchProducts(); // Refresh the list to show changes
        } else {
            let errorMsg = `Failed to update product. Status: ${response.status}`;
            // Try to parse JSON only if the server indicates it's sending JSON
            if (response.headers.get('content-type')?.includes('application/json')) {
                const result = await response.json();
                errorMsg = result.detail || errorMsg;
            }
            throw new Error(errorMsg);
        }
    } catch (error) {
        console.error("Error updating product:", error);
        alert(`Error: ${error.message}`);
    }
};

// Event listeners
document.addEventListener('DOMContentLoaded', fetchProducts);
refreshBtn.addEventListener('click', fetchProducts);
productForm.addEventListener('submit', handleFormSubmit);
closeModalBtn.addEventListener('click', () => editModal.classList.add('hidden'));
editForm.addEventListener('submit', handleEditSubmit);

// Event delegation for edit and delete buttons
productList.addEventListener('click', (event) => {
    const productCard = event.target.closest('[data-product-id]');
    
    // Ensure a product card was actually clicked
    if (productCard) {
        const productId = productCard.dataset.productId;
        if (event.target.classList.contains('edit-btn')) {
            openEditModal(productId);
        }
        if (event.target.classList.contains('delete-btn')) {
            deleteProduct(productId);
        }
    }
});
