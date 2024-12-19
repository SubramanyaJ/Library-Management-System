Steps Done to make the project Using Django 

1. Create a virtual enviroment so that the project is isolated from changes outside

2. Create the project using django-admin in virtual enviroment (project : library_management_system)

3. Create an app for all the webpages of project to integrate (app : libraryweb)

Note : Apps is used to have different functionalities in a website and make codes reusable later on
but here since this is a simple management system with not much depth we are using only 1 app

4.Database and admin panel will be added later for now we are doing only frontend part

5.Create a base html to have a basic common page for all webpages

6.Create a home page html and notification page html extending from base html

Note: each html page uses tailwind through which we are using grid system to 
align and make it look simple and neat

7.link home page through views in libraryweb and using urls in (app)libraryweb and urls.py in 
(main project urls file)library_management_system
heres how it goes
-make url for the main project in main urls.py of project folder
-connect it to urls.py of app folder

8.then add views from app to urls.py of libraryweb

9.Make a notifications html and link in urls.py of app folder

10.Make a static/css and static/js folder under which css of each html page will be implemented

11.learn about django template tags to understand whats happening in each html page

12.create a middleware(basically an outside function to make some changes) here its used to make the 
urls case insensitive and also add it in settings middleware datadictionary.

13.refined homepage and notification page using tailwind css

14.created a pagination for the use in the book search webpage

15.created temporary form in search webpage later will be dynamic using forms of django

16.Create a detail page which would redirect from home page or search page

17.Add a request book webpage which redirects to book if book available else gives a message request 
sucess page and accepts data (database will be done later)

18.Created a simple credits page

19.Created non functional signup signin and forgot password page 

20.Created custom error page that only works when Debug is False in settings

21.Databases created

22.Fully functional authentication stuff done i.e signup,signin and forgot password

23.signup automatically creates LibNum which is used to access a session when user is active

24.created two middlewares inactivitymiddleware which automatically signouts user if he isn't using website more than 5 mins

25.the other is if User is set inactive by admin automatically log out ie activeusermiddleware

26.created a dynamic context_processor that allows libnum to be accessable to all pages if a session of it is created

27.admin page automatically created by Django website

29.Created dynamic error pages that redirects based on whether user is in session(loggedin) or not
-if logged in redirects to home page
-else redirects to signin page

30.added History , latefees , borrowed books , profile page


Tasks left
3. Making it run on domain i.e. deploying the website(optional)
