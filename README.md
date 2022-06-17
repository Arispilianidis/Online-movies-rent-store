# Installation #
pip install -r requirements.txt

# Run server #
Run python file website_main.py

# Suggestions #
Better use Postman software to send post request to the server ( see Deus_ex.postman_collection.json)

# Testing #
I couldnt make pytest to work to create the unit tests, because the code required a logged in user, so i created some basic tests with Postman software. The code is inside the Tests tab when opening an HTTP request from the Postman collection <Deus_ex.postman_collection.json>.
The tests do not provide 100% code coverage, they were only used as proof of concept.
