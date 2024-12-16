const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');
const { MongoClient } = require('mongodb');

const app = express();
const port = 5000;

// Middleware
app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Serve the front-end
app.use(express.static(path.join(__dirname, 'public')));

// Connexion à MongoDB
const client = new MongoClient('mongodb://localhost:27017');
const dbName = 'product_comparator';
let db, collection;

client.connect()
    .then(() => {
        db = client.db(dbName);
        collection = db.collection('products');
    })
    .catch(err => console.error('Error connecting to MongoDB', err));

app.get('/api/products/search', (req, res) => {
    const productName = req.query.name;
    console.log('Product Name:', productName);

    // Vérifier si les produits existent déjà dans la base de données
    collection.find({ 'Name': new RegExp(productName, 'i') }).toArray()
        .then(products => {
            if (products.length > 0) {
                return res.json(products);  // Si produits trouvés, renvoyer les produits existants
            } else {
                // Si le produit n'existe pas, appeler le script de scraping
                exec(`python scrapping.py ${productName}`, (error, stdout, stderr) => {
                    if (error) {
                        console.error(`exec error: ${error}`);
                        return res.status(500).json({ error: 'Error while running the Python script' });
                    }
                    if (stderr) {
                        console.error(`stderr: ${stderr}`);
                        return res.status(500).json({ error: 'Python script stderr: ' + stderr });
                    }
                    try {
                        const products = JSON.parse(stdout);
                        res.json(products);
                    } catch (err) {
                        console.error("Error parsing JSON:", err);
                        res.status(500).json({ error: "Error parsing Python output" });
                    }
                });
            }
        })
        .catch(err => {
            console.error('Error fetching products:', err);
            res.status(500).json({ error: 'Error fetching products from the database' });
        });
});

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
