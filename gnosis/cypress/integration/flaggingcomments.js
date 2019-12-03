describe('Logging In - CSRF Tokens', function () {
    const username = 'testuser';
    const password = 'testpassword';

    Cypress.Commands.add('loginByCSRF', (csrfToken) => {
        cy.request({
            method: 'POST',
            url: 'http://127.0.0.1:8000/accounts/login/?next=/home/',
            failOnStatusCode: false, // dont fail so we can make assertions
            form: true, // we are submitting a regular form body
            body: {
                login: username,
                password,
                csrfmiddlewaretoken: csrfToken // insert this as part of form body
            }
        })
    });

    before(function () {
        cy.request('http://127.0.0.1:8000/accounts/login/?next=/home/')
            .its('body')
            .then((body) => {
                const $html = Cypress.$(body);
                const csrf = $html.find("input[name=csrfmiddlewaretoken]").val();
                cy.loginByCSRF(csrf)
                    .then((resp) => {
                        expect(resp.status).to.eq(200);
                    })
            })
    });

    it('foo test', function () {
        cy.visit('http://127.0.0.1:8000/catalog/paper/61/')
    })

});