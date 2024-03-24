# My Daily Tasks
## Description:

### Initial idea:

Tasks lists are generally useful for a wide variety of things. I know this is a classic project, but it is always useful to make. After doing a Discord Bot for CS50P, I decided to use other languages in addition to Python while sticking to what was taught in CS50. So, I chose to make a web-based application using JavaScript, Python, and SQL while leveraging CS50's custom codespace packages.

### What 'My Daily Tasks' does:

Allows a user to create an account without an email address on a lightweight task-list app. The account stores tasks on a day-by-day basis per user while allowing the user options to create, delete and check-off finished tasks at their discretion.

### app.py:
***
This file begins the Flask app by typing 'flask run' in the project directory. It connects to the 'tasks.db' as well to store all user information. The database has two tables: users and tasks. The users keeps track of log-in information, and the tasks keeps track of every task by date and by user id. I thought about allowing users to permit other users to check-off items on their task lists, but that would have been an entirely different app at that point. I had a lot of: 'Oh, wouldn't it be neat if...' moments that, upon further reflection, would have bloated the app or transformed it into something other than a lightweight personal task tracker.

#### The format for tasks.db is as follows:
***
#### For the users table:
***
- id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL
- username TEXT NOT NULL
- hash TEXT NOT NULL

#### For the tasks table:
***
- id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL
- user_id INTEGER NOT NULL
- date DATE NOT NULL
- task TEXT NOT NULL
- completed BOOL NOT NULL DEFAULT FALSE
- FOREIGN KEY (user_id) REFERENCES users (id)

I did a lot of commenting through the code to describe what each @app.route path does, but I will go over it here as well:

1. @after_request makes sure nothing is cached on the browser side to protect requests after they are made

2. @login_required uses a CS50 helper decorator that I changed around a little bit to make sure the route is only accessible if the user is logged in. If not, the user will get redirected to the log-in page

3. "/" is the index and the main page for an almost single-page app. It will always show today's date by default, and uses the datetime module to get yesterday's and tomorrow's date as well. This proved to be a bit tricky later, as here date.today() is the proper date-type, but later strings of dates needed to be converted to datetime.date objects in other routes. After the dates are sorted, the database is queried and and any tasks for the current user and given date are returned, if any

4. "/add" checks to make sure no funny-business happened on the user-end to bypass browser-side validation before inserting the new task into the database for the given date and current user. Then it redirects to the main page with the updated info and gives the user feedback through Flask's flash

5. "/update" has two kinds of logic. First, if the delete button was pressed for a task in the list, "delete-task" gets passed to the request, and it checks for funny-business on the user's end before deleting the task for the current user and given date

    Otherwise, it is a normal update request and the database will update whether all the current tasks for the given date have been completed or not by whether the user has checked them or not. The list of checked items might not exist, and there was no way that I could tell to send unchecked items with in the request, so this was a little tricky to work around. I ended up using list comprehension to create a list of unchecked item based on what was in the checked list (and if it did not exist with the request, that was caught as well and taken care of). Then the database is updated for all tasks based on whether they are in the checked or unchecked list and the 'completed' column in the tasks table for the given tasks are updated to TRUE (1 in SQLITE) or FALSE (0 in SQLITE). Will provide a flash message if either the delete or update are successful

6. "/getdate" just protects the main page a bit from clutter and allows the rendering of today's date for the "/" route without having to add catches for ['GET'] and ['POST']. The code length would have been the same if this route's logic were added to the "/" route, but I wanted to keep it separated for clarity

7. "/login" forgets the session for the user, then tries to log a user in with proper credentials. Will redirect to the home page with the current date and a flash message if successful

8. "/logout" forgets the session for the user, the redirects them to the login page with a flash message if successful

9. "/register" makes sure there was no funny business client-side and, after server-side validation, creates a new user in the users table of tasks.db. Will then redirect to the login page with a successful flash message. I wasn't sure if I would even have a users table early on and the register, login and logout routes. The idea of more than one person using the same computer for the app made me create a simple email-less registration, just in case


### layout.html:
***
Using the templates directory to store the main layout that other pages extend saves a lot of redundant code. Bootstrap was the primary styling choice for this project, as I enjoyed working with it for my homepage. I got a clipboard favicon to represent my app, and a static title for all pages of 'My Daily Tasks'

The body leverages Bootstrap's container-fluid, among other classes, to make the app responsive on mobile as well. This was important to me since having a lightweight task tracker display properly on mobile should be a no-brainer in this day and age. The navbar is conditionally rendered based on whether a user is logged in (session['user_id]) or not, and styled using Bootstrap. I added a date picker to the navbar for quicker navigation to past or future dates, and it collapses at smaller screen sizes. Flashed messages are checked here as well, and if any exist, the will be displayed at the top of the page in a header to give user feedback

### index.html:
***
The yesterday and tomorrow buttons flank the h1 which displays the date for the currently selected task list. All of these are together in a single Bootsrap component and the 'col-md' makes sure the get put stacked atop one another for smaller screen sizes. The quick navigation buttons occurred to me later, and needed some fiddling with datetime to get right. Computers are not happen with dates, as I have heard many times, but I got it to work as intended and am happy with the result

Then is the form to add a new task along with a submit button next to it. Nothing too special here: it just provides client-side error checking, and is styled by Bootstrap.

Next, comes the conditional rendering with Jinja. If any rows were sent along with render_template, they show up here as a clickable, screen-wide, list item, and a delete button off to the side. I thought about adding confirmation checking to the delete button, but then I considered what kind of app this is and how irritating it would be to have to confirm deleting an entire day's worth of tasks with an additional prompting. It is not overly-sensitive data, so I ended up just deleting a task if the button is clicked. Another tricky part was to get the button clickable when the screen-wide label was clickable. I ended up using CSS to position the button relative to the other components and set its z-index to move its layer to be over the clickable item

The conditional line-through text-decoration was also a pain. It was about this time I came across more modern web architecture (React, and the like), and realized this probably would have been smoother to implement there. But, I had committed to what was taught in the course, and am happy I stuck it out. This ended up being possible using Javascript without a refresh. The code at the bottom fetches and the checkboxes for the current date, as well as the corresponding tasks. Then, an anonymouse function is run for each item in the list to see if it has been 'checked'. If it has, use the checkbox's index, since it is paired with the label, and set the task at the given index to have a text-decoration of 'line-through'. It was such a small aesthetic feature, but I learned that those seemed to be the most painful to implement throughout this project

Finally, there is a button at the end to mass update all tasks based on their current checked status, which I discussed above in the "/update" route.

If no tasks exist, an h2 is rendered in place of the task list to inform the user

### login.html & register.html:
***
These are simple form pages without much else going on. They will provide feedback upon successful login or registration using Flask's flash

### apology.html:
***
This uses CS50's helper function to render an apology page. This should be very difficult to get to for this app because of client-side checking, but it is here just in case something goes terribly awry

### styles.css:
***
I already touched on the most important piece of styling: that for the delete-button class. This allowed it to be clickable above another clickable item.

Bootstrap uses SCSS which I did not touch, so the way to change it with basic CSS was through the weird syntax to get at the background for body elements in Bootstrap. All I did was change the background to a grey I thought was easier on the eyes and that paired with blue. I am not the most aesthetically inclined individual, but I think it looks nice and clean

Other than that, I chose a different font and underlined that date selected