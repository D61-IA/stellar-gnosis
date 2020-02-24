# How To Contribute

We are happy to engage with the community and accept patches to make Stellar-Gnosis the best it can be. Below are some guidelines for contributing to the community.
 
## Contributing Code
 
1. Submit an issue describing your proposed change to the
   [issue tracker](https://github.com/stellargraph/stellar-gnosis/issues).
2. Please don't mix more than one logical change per submittal,
   because it makes the history hard to follow. If you want to make a
   change that doesn't have a corresponding issue in the issue
   tracker, please create one.
3. Coordinate with team members that are listed on the issue in
   question. This ensures that work isn't being duplicated.
4. Fork the stellar-gnosis [repo](https://github.com/stellargraph/stellar-gnosis), develop and test your code changes.
5. Ensure that your code has an appropriate set of unit tests (and integration tests if appropriate) that all pass.
6. Submit a pull request
7. Ensure that you have signed a Contributor License Agreement “CLA”
 
### Contributor License Agreement

In order to contribute to Stellar-Gnosis, please ensure that you have signed a Contributor License Agreement (CLA). Please email stellar.admin@csiro.au to obtain a CLA.

### Be Friendly ###
 
Stellar-Gnosis considers courtesy and respect for others an essential part of the community, and we strongly encourage everyone to be friendly when engaging with others. Please be helpful when people are asking questions, and on technical disagreements ensure that the issues are discussed in a respectful manner.
 
## Test Requirements for Contributors ###
 
If you plan to contribute a patch, you need to ensure that your code is
well tested. Please ensure that your code has adequate test coverage and
contains both unit and integration tests.
 
To make sure your changes work as intended and don't break existing
functionality, you'll want to install and run the existing Stellar-Gnosis
tests with the following line:
 
	python manage.py test
 
All tests should pass before submitting a pull request.
