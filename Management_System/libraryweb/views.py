from django.shortcuts import render,redirect,get_object_or_404
import json
from django.db.models import Q,Avg,Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView,DetailView,FormView,TemplateView,View
from django.urls import reverse
from .forms import BookRequestForm,SignUpForm,ResetPasswordForm,SignInForm,RatingForm
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.forms import SetPasswordForm
from .models import LibraryUser,BookMain,Request,Rating,UserBorrowed,UserHistory,LateFees
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.views.generic.list import ListView
from django.contrib.auth.hashers import check_password

def check_user_status(request):
    """
    Helper function to check if the user associated with lib_num is active.
    If not, it redirects to the signout page.
    """
    lib_num = request.session.get('lib_num', None)

    if lib_num:
        try:
            # Check if the LibraryUser exists and if the associated user is active
            library_user = LibraryUser.objects.get(lib_num=lib_num)
            user = library_user.user

            if not user.is_active:
                # If the user is inactive, redirect to signout or sign-in page
                return redirect('libraryweb:signout')

        except LibraryUser.DoesNotExist:
            # Redirect if no LibraryUser is found
            return redirect('libraryweb:signout')

        except Exception as e:
            # Handle other unexpected errors
            print(f"Unexpected error: {e}")
            return redirect('libraryweb:signout')

    return None
    

def custom_authenticate(username, password):
    """
    Custom authentication function to authenticate a user by username and password.

    Args:
        username (str): The username of the user.
        password (str): The plaintext password of the user.

    Returns:
        User: The authenticated user object if credentials are valid.
        None: If authentication fails.
    """
    try:
        # Find the user by username
        user = User.objects.get(username=username)
        
        # Check if the password is correct
        if check_password(password, user.password):
            # Return the user if credentials are valid
            return user
        else:
            return None
    except User.DoesNotExist:
        # Return None if the user does not exist
        return None


def error_404(request, exception=None):
    lib_num = request.session.get('lib_num', None)
    return render(request,'error404.html',{'lib_num': lib_num}, status=404)

def error_500(request):
    lib_num = request.session.get('lib_num', None)
    return render(request,'error500.html',{'lib_num': lib_num}, status=500)


class BorrowedBooksView(ListView):
    model = UserBorrowed
    template_name = "libraryweb/main/borrowed.html"
    context_object_name = "borrowed_books"

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user is valid and active before proceeding.
        """
        # Get lib_num from the URL
        lib_num = self.kwargs.get('lib_num')

        try:
            # Fetch the LibraryUser
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)

            # Check if the user is active
            if not self.library_user.user.is_active or not self.library_user.is_active:
                messages.error(self.request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')

        except Exception as e:
            print(f"Error occurred: {e}")
            messages.error(self.request, "An error occurred. Please try again later.")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filter borrowed books by the library user.
        """
        return UserBorrowed.objects.filter(user=self.library_user)

    def get_context_data(self, **kwargs):
        """
        Add additional context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['lib_num'] = self.kwargs.get('lib_num')
        return context


class ProfileView(TemplateView):
    template_name = 'libraryweb/main/profile.html'

    def dispatch(self, request, *args, **kwargs):
        # Get lib_num from the URL
        lib_num = self.kwargs.get('lib_num', None)

        try:
            # Get the LibraryUser associated with the lib_num
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)
            self.user = self.library_user.user

            # Check if the user is active
            if not self.user.is_active or not self.library_user.is_active:
                print("User is not active, redirecting to signout")
                messages.error(self.request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')

        except Exception as e:
            # Log and handle unexpected errors
            print(f"Unexpected error: {e}")
            messages.error(self.request, "An error occurred while loading your profile.")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Get the context from the parent class
        context = super().get_context_data(**kwargs)

        # Add lib_num, user, and library_profile to the context
        context['lib_num'] = self.kwargs.get('lib_num', None)
        context['user'] = self.user
        context['library_profile'] = self.library_user

        return context

class UpdateProfileView(View):
    def post(self, request, *args, **kwargs):
        lib_num = kwargs.get('lib_num')
        try:
            library_user = LibraryUser.objects.get(lib_num=lib_num)
            # Parse JSON data from the request body
            data = json.loads(request.body)
            fav_genre = data.get('fav_genre')

            if fav_genre:
                library_user.fav_genre = fav_genre
                library_user.save()
                # Send success response with profile URL
                profile_url = reverse('libraryweb:profile', kwargs={'lib_num': lib_num})
                return JsonResponse({'success': True, 'redirect_url': profile_url})
            
            profile_url = reverse('libraryweb:profile', kwargs={'lib_num': lib_num})
            return JsonResponse({'success': False , 'redirect_url': profile_url})
        except LibraryUser.DoesNotExist:
            return JsonResponse({'success': False})


class HomePageView(ListView):
    model = BookMain
    context_object_name = "popular_books"
    template_name = "libraryweb/main/home.html"
    paginate_by = 10  # Limit to top 10 books

    def get_queryset(self):
        # Annotate books with average rating and borrowed count
        return (
            BookMain.objects.annotate(
                avg_rating=Avg('ratings__rating'),  # Average rating
                borrowed_count=Count('availability__borrowed_instances')  # Borrowed count
            )
            .order_by('-avg_rating', '-borrowed_count', 'title')[:10]  # Limit to top 10
        )

    def dispatch(self, request, *args, **kwargs):
        # Get the library number from the URL
        lib_num = self.kwargs.get('lib_num', None)

        try:
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)
            self.user = self.library_user.user

            if not self.user.is_active or not self.library_user.is_active:
                print("User is not active, redirecting to signout")
                messages.error(self.request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')


        except LibraryUser.DoesNotExist:
            return redirect('libraryweb:signout')

        except Exception as e:
            print(f"Unexpected error: {e}")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Fetch the context from the parent class
        context = super().get_context_data(**kwargs)

        # Add the library number to the context
        context['lib_num'] = self.kwargs.get('lib_num', None)
        return context

#in home page we will use for loop to take out data, later this will be done by real database

    

class HistoryView(ListView):
    model = UserHistory
    template_name = 'libraryweb/main/history.html'  # Specify your template
    context_object_name = 'user_history'  # The name of the context variable
    paginate_by = 10  # Number of items per page

    def get_queryset(self):
        # Get the user based on their library number
        lib_num = self.kwargs['lib_num']
        return UserHistory.objects.filter(user__lib_num=lib_num).order_by('-borrow_date')

    def dispatch(self, request, *args, **kwargs):
        # Get the library number from the URL
        lib_num = self.kwargs.get('lib_num', None)

        try:
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)
            self.user = self.library_user.user

            if not self.user.is_active or not self.library_user.is_active:
                print("User is not active, redirecting to signout")
                messages.error(self.request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')


        except LibraryUser.DoesNotExist:
            return redirect('libraryweb:signout')

        except Exception as e:
            print(f"Unexpected error: {e}")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Fetch the context from the parent class
        context = super().get_context_data(**kwargs)

        # Add the library number to the context
        context['lib_num'] = self.kwargs.get('lib_num', None)
        return context



class SearchPageView(ListView):
    model = BookMain
    context_object_name = "books"
    paginate_by = 10
    template_name = 'libraryweb/main/search.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user is valid and active before proceeding.
        """
        # Get lib_num from the URL
        lib_num = self.kwargs.get('lib_num')

        try:
            # Fetch the LibraryUser
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)
            self.user = self.library_user.user

            # Check if the user is active
            if not self.user.is_active or not self.library_user.is_active:
                print("User is not active, redirecting to signout")
                messages.error(self.request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')

        except Exception as e:
            print(f"Error occurred: {e}")
            messages.error(self.request, "An error occurred. Please try again later.")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filter books based on the search query.
        """
        # Get the search query from the request
        query = self.request.GET.get("query", "")

        # Annotate with average rating and borrowed count
        queryset = BookMain.objects.annotate(
            avg_rating=Avg('ratings__rating'),  # Average rating of the book
            borrowed_count=Count('availability__borrowed_instances')  # Borrowed count
        )

        # Apply search filters if query exists
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(genre__icontains=query) |
                Q(isbn__icontains=query)
            )
        
        # Order by avg_rating (descending), borrowed_count (descending), and title (ascending)
        return queryset.order_by('-avg_rating', '-borrowed_count', 'title')

    def get_context_data(self, **kwargs):
        """
        Add additional context to the template.
        """
        # Get the context from the parent class
        context = super().get_context_data(**kwargs)
        
        # Add lib_num to the context
        context['lib_num'] = self.kwargs.get('lib_num')
        return context
    

    


class DetailPage(DetailView):
    model = BookMain
    context_object_name = "bookdetail"
    template_name = "libraryweb/main/detail.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user is valid and active before proceeding.
        """
        lib_num = self.kwargs.get('lib_num')
        try:
            # Fetch the LibraryUser
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)

            # Check if the user is active
            if not self.library_user.user.is_active or not self.library_user.is_active:
                messages.error(self.request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')

        except Exception as e:
            print(f"Error occurred: {e}")
            messages.error(self.request, "An error occurred. Please try again later.")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        """
        Get the book object based on ISBN.
        """
        isbn = self.kwargs.get("isbn")
        try:
            book = BookMain.objects.get(isbn=isbn)
        except BookMain.DoesNotExist:
            raise Http404("Book Not Found")
        return book

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to submit a rating form.
        """
        # Get the current book
        book = self.get_object()

        # Create the form instance with the POST data
        form = RatingForm(request.POST)
        
        if form.is_valid():
            # If the form is valid, save the rating
            rating = form.save(commit=False)
            rating.user = self.library_user  # Set the current user
            rating.book = book  # Set the current book
            rating.save()  # Save the rating

            # Add a success message and redirect to the same page
            messages.success(request, "Your rating has been submitted!")
            return redirect('libraryweb:detail', lib_num=self.library_user.lib_num, isbn=book.isbn)

        # If the form is not valid, re-render the page with form errors
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Add additional context to the template.
        """
        context = super().get_context_data(**kwargs)

        # Add lib_num to the context
        context['lib_num'] = self.kwargs.get('lib_num')

        # Add rating form and reviews
        context['rating_form'] = RatingForm()
        context['existing_rating'] = Rating.objects.filter(user=self.library_user, book=self.object).first()
        context['all_ratings'] = Rating.objects.filter(book=self.object).select_related('user')

        return context
    

class RequestSuccessView(TemplateView):
    template_name = 'libraryweb/main/success.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user is valid and active before proceeding.
        """
        # Get lib_num from the session or query parameters
        lib_num = self.request.session.get('lib_num', self.request.GET.get('lib_num'))

        try:
            # Fetch the LibraryUser
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)
            self.user = self.library_user.user

            # Check if the user is active
            if not self.user.is_active or not self.library_user.is_active:
                print("User is not active, redirecting to signout")
                messages.error(self.request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')
            
        except Exception as e:
            print(f"Error occurred: {e}")
            messages.error(self.request, "An error occurred. Please try again later.")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Add 'lib_num' to the context.
        """
        context = super().get_context_data(**kwargs)
        
        # Get the 'lib_num' from the session or query parameters
        lib_num = self.request.session.get('lib_num', self.request.GET.get('lib_num'))
        
        # Add 'lib_num' to the context
        context['lib_num'] = lib_num
        
        return context

def book_request_view(request, lib_num):
    # Fetch the LibraryUser and check if the user is active
    try:
        # Fetch the LibraryUser instance using lib_num
        library_user = get_object_or_404(LibraryUser, lib_num=lib_num)
        user = library_user.user  # Assuming LibraryUser has a related User object

        # Check if the user and library user are both active
        if not user.is_active or not library_user.is_active:
            print("User is not active, redirecting to signout")
            messages.error(request, "Your account is inactive. Please sign in again.")
            return redirect('libraryweb:signout')

    except LibraryUser.DoesNotExist:
        # Handle case where LibraryUser is not found (you can redirect or show an error)
        messages.error(request, "User not found.")
        return redirect('libraryweb:signout')

    # Continue with the book request form processing
    request.session['lib_num'] = lib_num
    if request.method == 'POST':
        form = BookRequestForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            isbn = form.cleaned_data.get('isbn')

            try:
                book = BookMain.objects.get(isbn=isbn)
                return redirect(reverse('libraryweb:detail', args=[lib_num, book.isbn]))
            except BookMain.DoesNotExist:
                new_request = Request(
                    user=library_user,
                    isbn=isbn,
                    title=title,
                    author=form.cleaned_data.get('author'),
                )
                new_request.save()
                return redirect(reverse('libraryweb:success', args=[lib_num, isbn]))
        else:
            return render(request, 'libraryweb/main/request.html', {'form': form})

    else:
        form = BookRequestForm()

    return render(request, 'libraryweb/main/request.html', {'form': form, 'lib_num': lib_num})








class CreditsView(TemplateView):
    template_name = "libraryweb/main/credits.html"

    def dispatch(self, request, *args, **kwargs):
        # Fetch lib_num from URL kwargs
        lib_num = kwargs.get('lib_num')

        try:
            # Fetch the LibraryUser
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)

            # Check if the user is active
            if not self.library_user.user.is_active or not self.library_user.is_active:
                messages.error(request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')

        except Exception as e:
            print(f"Error occurred: {e}")
            messages.error(request, "An error occurred. Please try again later.")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

class SignInView(FormView):
    template_name = 'libraryweb/auth/signin.html'
    form_class = SignInForm

    def form_valid(self, form):
        # Extract username and password from the form
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        # Authenticate the user
        user = custom_authenticate(username=username, password=password)


        if user and hasattr(user, 'library_profile'):
            # If the user is authenticated, log them in
            if not user.is_active or not user.library_profile.is_active:
                user.is_active = True
                user.library_profile.is_active = True
                user.save()
                user.library_profile.save()
                self.request.session['lib_num'] = user.library_profile.lib_num

            login(self.request, user)
            return redirect('libraryweb:home', lib_num=user.library_profile.lib_num)
        else:
            # Invalid credentials
            messages.error(self.request, "Invalid username or password.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)
    

class SignUpView(FormView):
    template_name = 'libraryweb/auth/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('libraryweb:signin')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data['gmail']  # Save the email field
        user.save()
        LibraryUser.objects.create(user=user)
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


def reset_password(request):
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            lib_num = form.cleaned_data['lib_num']
            new_password = form.cleaned_data['new_password1']

            try:
                # Check if the user exists with the provided username and lib_num
                user = User.objects.get(username=username)
                userlib = LibraryUser.objects.get(lib_num=lib_num)

                if userlib:
                
                # Update the user's password
                    user.set_password(new_password)
                    user.save()

                    messages.success(request, "Your password has been successfully updated.")
                    return redirect('libraryweb:signin')  # Redirect to login page after success
            except User.DoesNotExist and LibraryUser.DoesNotExist:
                messages.error(request, "No matching user found with the provided Username and LIB Number.")
    else:
        form = ResetPasswordForm()

    return render(request, 'libraryweb/auth/forgot_password.html', {'form': form})



def sign_out(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Set the user's 'is_active' status to False
        user = request.user
        user.is_active = False
        user.library_profile.is_active = False
        user.library_profile.save()
        user.save()
        # Clear the user's session data
        request.session.flush()
        # Log the user out
        logout(request)

    # Redirect to the sign-in page after logging out
    return redirect('libraryweb:signin')

class LateFeesListView(ListView):
    model = LateFees
    template_name = 'libraryweb/main/late.html'
    context_object_name = 'late_fees'

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user is valid and active before proceeding.
        """
        lib_num = self.kwargs['lib_num']
        try:
            # Fetch the LibraryUser based on the lib_num
            self.library_user = get_object_or_404(LibraryUser, lib_num=lib_num)

            # Check if the user is active
            if not self.library_user.user.is_active or not self.library_user.is_active:
                messages.error(self.request, "Your account is inactive. Please sign in again.")
                return redirect('libraryweb:signout')

        except Exception as e:
            print(f"Error occurred: {e}")
            messages.error(self.request, "An error occurred. Please try again later.")
            return redirect('libraryweb:signout')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filter LateFees based on the user's library number (lib_num).
        """
        lib_num = self.kwargs['lib_num']
        # Filtering LateFees based on the related UserBorrowed and LibraryUser models
        return LateFees.objects.filter(user_borrowed__user__lib_num=lib_num).order_by('fee')

    def get_context_data(self, **kwargs):
        """
        Add the current user's library number to the context.
        """
        context = super().get_context_data(**kwargs)
        context['lib_num'] = self.kwargs['lib_num']
        return context