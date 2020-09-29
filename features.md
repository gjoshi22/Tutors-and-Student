Features that have been used in the project: 

Our final project is titled 'Students-and-Tutors' where students and tutors can create an account and login to their accounts. 
The students once logged in can choose to hire available tutors or delete them. Similarly, tutors one logged in can delete the students 
who have hired them.

The three features that were used in the project are: 

a. An HTML page with a form that can be used to add information to the database. We created an HTML form in the add student or tutor   page where the student or tutor creates a new account if they do not have one and once their account is created, they can use the same 
credentials to login to their respective accounts. In addition to that, students can also hire or delete tutors. Similarly tutors can also delete students who hired them with the help of the form. Once information has been written in the HTML forms, the flask processes the   information that has been added and adds either the student or tutor into the database. If the user tries to submit the form with either   incomplete information or wrong password (when logging in), they get a message saying that their information is either incomplete or   they provided a wrong password. The HTML tag form is used in the project to create input boxes, submit button and the labels.   The form tag also consists of the keyword action which specifies a link to the  page that when we hit the submit button, the page that it is redirected to. The method=post keyword in the form tag specifies that our method is a post request so that the data entered in the form is added to the database as post form data.

b. User accounts which stores the password into the database. The password is hashed and salted for secure storage into the databse. 
Using the HTML form page, a user can create their account and login to their accounts. Our project uses the bcrypt package which makes
hashing and salting convenient. The student and the tutor table consists of the column salt and this salt is generated by bycrypt using
the command 'salt = bcrypt.gensalt()'. This salt is made up of random bits and each user has a unique salt for their password that is being stored in the database. When the password is initially stored in the database, it is hashed using the salt and the salt is 
stored alongside it for verification. The password is hashed and stored as a decoded code using the command   
'bcrypt.hashpw(password.encode(), salt).decode()'. The salt is also decoded simulatenously while storing as they consists of random
bits. So, when a user logs in, the username is looked up and the entered password is verified by checking if the entered password hased using an encoded salt is same as the encoded password (which was hashed using the same salt) that has been saved in the database. We used an if conditional in our project to do so  where if the passwords are matched, it returns the student or tutor id otherwise returns False.  

    if bcrypt.hashpw(password.encode(), id['salt'].encode()) == id['password'].encode():
         return id['tutor_id'] or id['student_id'] {depending on the condition} 
    else:
         return False
                
c. Making websites fancier using CSS and Javascript. The website which utilizes the database has been made fancy and attractive using CSS and Javacript. Each individual html template has its correspoding .css styling which is stored in the static directory. Some of the css styling includes importing an image from a website and setting it as the background image of the webpage. In addition to that, tables are created using the table tag in HTML to display the list of tutors and students present in the database. Each individual buttons have also been incorporated in the webpage so that the user can switch between the webpages. The buttons are also made attractive by setting a background color when a cursor is hovered over the button. The webpages also consist of form and input boxes with a translucent background which have been placed in the middle of the webpage when a student or a tutor chooses to log in or create an account. An option to view the password in the input box is present so that a user can check what they entered in the input box before hitting the submit button. This has been made possible with the help of Javascript. The fonts, the color of the of the text have 
also been changed and indent have been made possible using the tag div which specifies a division of the HTML template that is styled in the css. 