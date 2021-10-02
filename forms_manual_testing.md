# Testing the Candidate Review Forms feature

This is a document outlining how to manually test candidate review forms in Mayan. We will test that the forms feature displays on the main page and that the user can fill in the fields to score candidates.

---
**NOTE**

The forms feature as of now is a basic prototype so a lot of functionality that we plan to add later is missing. Currently our team has not gotten to implementing the backend for our feature. This will be accounted for in this manual testing script.


---

## Manual testing instructions

+ Start Mayan
+ Enter username and password to log in
    - After this, you should be able to see the home page. At the top should be a form labeled "Candidate Review Form".
+ Fill in the fields on the form
    - The form has dropdown fields (such as for the Skills score) and text fields (such as for the Candidate Name field) that the reviewer can fill out. 
        * Verify that when selecting a dropdown menu option that the corresponding menu changes to reflect the selected value.
        * Verify that when typing something into a text field that the text is persistent upon navigating to the next field in the form.
+ Press Enter to submit the form
    - It is expected if this causes an error because we currently do not have our backend or database communication set up.


## Manual testing evaluation

After performing the steps, if all of the items below were fulfilled then the feature is working as intended.

- Candidate Review Form showed up on main page after logging in
- All fields display properly
    * First Name
    * Last Name
    * Email address
    * Experience Score
    * Skills Score
    * GPA Score
    * Essay Score
    * Additional Comments
    * Reviewer Name
    * Final Decision
<!--TODO: add new form fields here after they are added-->
- User was able to fill in fields and see review reflected in form before pressing Submit

