# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """ Test reading a product """
        product = ProductFactory()
        logging.info("Testing reading %s", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """ Test updating a product """
        product = ProductFactory()
        logging.info("Testing updating %s", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # update
        product.description = "this couldnt possibly have been generated"
        original_id = product.id
        product.update()
        self.assertEqual(original_id, product.id)
        self.assertEqual("this couldnt possibly have been generated", product.description)
        # get all products
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "this couldnt possibly have been generated")

    def test_delete_a_product(self):
        """ Test deleting a product """
        product = ProductFactory()
        product.create()
        # confirm one product in the system
        products = Product.all()
        self.assertEqual(len(products), 1)
        # time to delete the product
        product.delete()
        # check for product deletion
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """ Test listing all products """
        products = Product.all()
        self.assertEqual(len(products), 0)
        for _ in range(5):
            product = ProductFactory()
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """ Test finding product by name """
        for _ in range(5):
            product = ProductFactory()
            product.create()
        products = Product.all()
        product_name = products[0].name
        count = len([product for product in products if product.name == product_name])
        found = Product.find_by_name(product_name)
        self.assertEqual(count, found.count())
        for product in found:
            self.assertEqual(product.name, product_name)

    def test_find_product_by_availability(self):
        """ Test finding product by availability """
        for _ in range(10):
            product = ProductFactory()
            product.create()
        products = Product.all()
        product_availability = products[0].available
        availability_count = len([product for product in products if product.available == product_availability])
        found = Product.find_by_availability(product_availability)
        self.assertEqual(availability_count, found.count())
        for product in found:
            self.assertEqual(product.available, product_availability)

    def test_find_product_by_category(self):
        """ Test finding product by category """
        for _ in range(10):
            product = ProductFactory()
            product.create()
        products = Product.all()
        product_category = products[0].category
        category_count = len([product for product in products if product.category == product_category])
        found = Product.find_by_category(product_category)
        self.assertEqual(category_count, found.count())
        for product in found:
            self.assertEqual(product.category, product_category)
