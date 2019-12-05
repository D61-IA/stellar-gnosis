// describe('My First Test', function(){
//     it('Visits the kitchen sink', function(){
//         cy.visit('https://example.cypress.io/');
//
//         cy.contains('type').click();
//         cy.url().should('include', '/commands/actions');
//         cy.get('.action-email')
//             .type('fake@email.com')
//             .should('have.value', 'fake@email.com');
//     })
// });


describe('Logging In - CSRF Tokens', function () {
    const username = 'testadmin';
    const password = 'testadmin';

    // Cypress.Commands.add('loginByCSRF', (csrfToken) => {
    //     cy.request({
    //         method: 'POST',
    //         url: 'http://127.0.0.1:8000/accounts/login/?next=/home/',
    //         failOnStatusCode: false, // dont fail so we can make assertions
    //         form: true, // we are submitting a regular form body
    //         body: {
    //             login: username,
    //             password,
    //             csrfmiddlewaretoken: csrfToken // insert this as part of form body
    //         }
    //     })
    // });

    before(function () {
        // cy.request('http://127.0.0.1:8000/accounts/login/?next=/home/')
        //     .its('body')
        //     .then((body) => {
        //         const $html = Cypress.$(body);
        //         const csrf = $html.find("input[name=csrfmiddlewaretoken]").val();
        //         cy.loginByCSRF(csrf)
        //             .then((resp) => {
        //                 expect(resp.status).to.eq(200);
        //             })
        //     });

        cy.visit('http://127.0.0.1:8000/accounts/login/?next=/home/');
        cy.get('#id_login').type('testadmin');
        cy.get('#id_password').type('testadmin');
        cy.get('button[type="submit"').click();

        cy.visit('http://127.0.0.1:8000/catalog/paper/61/');

    });


    it('title test', function () {
        // check if the title of the page is correct
        cy.get('title').should('have.text', 'Gnosis Research Paper Management')
    });

    it('testFlagUI', function () {

        // assert the flags are outlined for all comments
        cy.get('.open_flag_dialog i.material-icons').each(($el, index, $list) => {
            expect($el).to.have.text('outlined_flag');
            expect($list).to.have.length(2);
        })
    });

    it('testFlagClick', function () {
        // click on the first flag
        cy.get('.open_flag_dialog i.material-icons').first().click();

        // assert the flag form is now visible
        cy.get('#flag_form_dialog').should('be.visible')
    });

    it('testFlagForm', function () {
        var violations = ['spam', 'offensive', 'pornography', 'extremist', 'violence'];
        cy.get('#flag_form').within(() => {
            cy.get('#id_violation > li').each(($el, index, $list) => {
                // console.log(index);
                // assert each label has the correct text
                cy.get($el.children('label')).contains(violations[index])
            });

            cy.get('textarea').should('have.id', 'id_description')
        })
    });

    // ERROR: unable to submit form for some reason
    it('testFlagValidFormSubmit', function () {
        cy.get('#id_violation > li').first().within(() => {
            cy.get('input').click()
        });

        cy.get('#id_description').type('violation description');

        // cy.get('#flag_form').within(() => {
        //     cy.get("input[type='submit']").click();
        // });

        cy.get('#flag_form').submit();
        cy.get('#flag_form_container').should('be.hidden');

        // cy.get('#flag_response').should('not.be.hidden')

    });


});
