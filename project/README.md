# CS50 Online Bank
#### Video Demo:  <https://youtu.be/Tzm7SnLASCY>
#### Description:

This project is my final project for the CS50's introduction to computer science.
It is an online bank account interface that grants to the customers access to their account wherever they are.

In general, this type of project is very usefull firstly for the bank owners, and secondly for the customers.

For the bank owners, because an online interface of a bank reduce the flux of persons they have to serve face to face or by phone calls,
and that accelerate the process in just some clicks on the web application. it reduce the amount of paper the bank would have had to use.

For the customers, because online sevices prevent them from going physically to the bank to perform a transaction. It gives to them the flexibility to use some services event after the close time of the bank.

My project has severals fonsctionalities:

    - Basics fonctionalities
        1. Create an account
        2. Login to an existing account
        3. Log out

    - Main fonctionalities (Perform transactions)
        1. Make withdrawals (Payment and Bank transfer)
        2. Make deposits (Upload a check)

    - Advance fonctionalities (Settings)
        1. Change username
        2. Change password
        3. Delete account

Description of the fonctionalities

    Create an Account
        Customers can create an account via the register menu with their
        unique account numer, their name as username, and a password.

    Login
        Customers can, after being registered, login to their account and
        have access to all the services listed above.

    Log out
        This fonctionality simply permits to the users to put an end in
        a session and leave their online interface.

    Make withdrawals
        This fonctionality grants access to users to make online payment
        and bank transfer money to other users directly to thier account number.

    Make deposits
        In that part of the project , users can add money on their bank account
        by uploading their pay check. This is the most innovative part of my project.
        Because in my country(Haiti) if someone has a check, they necessarily have to
        go to the bank to make make that type of deposit.

    Change username
        Part of the advance fonctionalities, it gives users the flexibility to change
        their username at anytime.

    Change of password
        This fonctionality allow users to change their password whenever they want to.

    Delete account
        This one allow users to stop using the online services of their bank by deleting
        their account and erased al data linked to the account. But the bank owners can
        still have acces to de data related to the account of the users, since delete
        your online interface does not mean delete the bank account at all.

Files in the project:

    The project contains severals files, each of them has its own fontion and display
    a diffrent fonctionality and/or a diffrent view.

    1. static
        In static folder there is my styles.css file where I give shape to my HTMLs files.

    2. templates
        In templates there are all my HTMLs files where I display datas and/or forms to users.

        - In register.html, I prompt a form to the users in which they can provide some
            informations about them and their bank account to get a personnal interface for their
            account, and then submit them. If they fail to enter informations properly, they will
            see an alert of error and will be reprompt again.

        - In login.html, I prompt a form to the users in which they can provide informations
            about their existing bank account onlin interface to get a personnal interface for their
            account, and then submit them. If they fail to enter informations properly, they will
            see an alert of error and will be reprompt again.

        - In deposits.html, I prompt a form to the users in which they can provide some
            informations about its transactions(deposits), and then submit them. If they fail to enter
            informations properly, they will see an alert of error and will be reprompt again.

        - In withdrawals.html, I prompt a form to the users in which they can provide some
            informations about its transactions(withdraws), and then submit them. If they fail to enter
            informations properly, they will see an alert of error and will be reprompt again.

        - In settings.html, I prompt a form with three options to the users in which they can choose
            what action they want to take, and provide required informations about their  online account
            and finally make a decision by submitting one of the three forms provided by the settings view
            to get their action effective. They can wheter change their username, change their password or
            delete their account at all. If they fail to enter informations properly, they will see an
            alert of error and will be reprompt again.

        - Index.html, is where the users can have a large overview on their account, what have happened,
            the time actions where perfomed, infomations about them and their bank account. For example: username
            balance, account number and all transactions they where performed.

        - layout.html, is where are built the main structure of the web page, head, body, footer, and all of the
            necessary features.

    3. app.py
        app.py is a python file, where I wrote all the codes of the web app, the fonctionalities and the way they
        will be executed. I use frameworks like Flask and Jinja to implement some fonctionalities and link python
        with html file. I use SQL to store information from the web app (front-end) to the back-end.

    4. cs50bank.db
        Using SQL, This is where I stock all the datas of my project, it contains the users informations and all
        the details about transactions history. For exemple: date and time, description, type of transaction,
        account number, ect...

    5. requirements.txt
        in requirements.txt there are
            cs50
            Flask
            Flask-Session
            requests


Languages used:

    - Python
    - html and css
    - SQLite

    Frameworks
        Flask
        Jinja
        Bootstrap 5

