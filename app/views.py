from datetime import datetime, timedelta
from collections import defaultdict
import random
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from .models import *
from .forms import *
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission
from .serializers import ServiceSerializer, ProviderSerializer, BookingRequestSerializer


@login_required(login_url="admin_login")
def admin_provider(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to manage providers.")
        return redirect("dashboard")

    if request.method == "POST":

        
        if "save_provider" in request.POST:
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            status = True if request.POST.get("status") else False

            
            company_name = "noahsark"
            base_username = f"{first_name.lower()}{company_name}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            auto_password = username + str(random.randint(100, 999))

            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=auto_password,
                first_name=first_name,
                last_name=last_name
            )

            
            UserProfile.objects.create(
                user=user,
                phone=phone,
                role="provider",
                status=status
            )

            
            try:
                subject="Your Provider Account - Noah’s Ark Home Services"
                message=f"""Hi {first_name} {last_name},\n\nYour provider account has been created.\n\nUsername: {username}\nPassword: {auto_password}\n\nPlease login to your provider dashboard.\n]\nBest regards,\nNoah's Ark Team"""
                send_mail(subject,message,settings.EMAIL_HOST_USER,[email],fail_silently=True)
                 
            except:
                pass

            messages.success(request, f"Provider {first_name} {last_name} registered successfully.")
            return redirect("admin_provider")

       
        elif "update_provider" in request.POST:
            pid = request.POST.get("update_provider")
            provider_obj = UserProfile.objects.get(id=pid)
            user = provider_obj.user

            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            status = True if request.POST.get("status") else False

           
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            provider_obj.phone = phone
            provider_obj.status = status
            provider_obj.save()

            messages.success(request, f"Provider {first_name} {last_name} updated successfully.")
            return redirect("admin_provider")

        
        elif "delete_provider" in request.POST:
            pid = request.POST.get("delete_provider")
            provider_obj = UserProfile.objects.get(id=pid)
            provider_obj.user.delete()  
            provider_obj.delete()

            messages.success(request, "Provider deleted successfully.")
            return redirect("admin_provider")

   
    providers = UserProfile.objects.filter(role="provider").order_by("user__first_name")
    return render(request, "admin_page/admin_provider.html", {"providers": providers})




def add_provider(request):
    return render(request,'admin_page/register_provider.html')

def admin_service_section(request, name):
    context = {}

    
    service = Service.objects.get(service_name=name)

    
    if request.method == "POST":
        if 'save' in request.POST:
            titles = request.POST.get('title')
            if titles:  
                ServiceSection.objects.create(service=service, title=titles)

        if 'delete' in request.POST:
            key = request.POST.get('delete')
            titles = ServiceSection.objects.get(id=key)
            titles.delete()

        if'update' in request.POST:
            key = request.POST.get('update')
            titles=ServiceSection.objects.get(id=key)
            title = request.POST['title']
            service = Service.objects.get(service_name=name)
            titles.service=service
            titles.title=title
            titles.save()
    
    sections = ServiceSection.objects.filter(service=service)
    context['title'] = sections
    context['data'] = service

    return render(request, 'admin_page/admin_service_section.html', context)


from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404


def admin_section_contents(request, id):

    # Get the exact section using its primary key.
    # This completely avoids duplicate-title problems.
    section = get_object_or_404(
        ServiceSection,
        id=id
    )

    if request.method == "POST":

        # =====================================================
        # ADD CONTENT
        # =====================================================

        if "save" in request.POST:

            title = request.POST.get("title", "")
            description = request.POST.get("description", "")
            icon = request.POST.get("icon", "")
            image = request.FILES.get("image")

            try:
                order = int(
                    request.POST.get("order", 0)
                )
            except (TypeError, ValueError):
                order = 0

            ServiceSectionItem.objects.create(
                section=section,
                title=title,
                description=description,
                icon=icon,
                image=image,
                order=order
            )

            return redirect(
                "admin_section_contents",
                id=section.id
            )

        # =====================================================
        # DELETE CONTENT
        # =====================================================

        elif "delete" in request.POST:

            key = request.POST.get("delete")

            item = get_object_or_404(
                ServiceSectionItem,
                id=key,
                section=section
            )

            item.delete()

            return redirect(
                "admin_section_contents",
                id=section.id
            )

        # =====================================================
        # UPDATE CONTENT
        # =====================================================

        elif "update" in request.POST:

            key = request.POST.get("update")

            item = get_object_or_404(
                ServiceSectionItem,
                id=key,
                section=section
            )

            item.title = request.POST.get(
                "title",
                item.title
            )

            item.description = request.POST.get(
                "description",
                item.description
            )

            item.icon = request.POST.get(
                "icon",
                item.icon
            )

            try:
                item.order = int(
                    request.POST.get(
                        "order",
                        item.order
                    )
                )
            except (TypeError, ValueError):
                pass

            image = request.FILES.get("image")

            if image:
                item.image = image

            item.save()

            return redirect(
                "admin_section_contents",
                id=section.id
            )

    # =========================================================
    # GET CONTENT ITEMS
    # =========================================================

    items = (
        ServiceSectionItem.objects
        .filter(section=section)
        .order_by("order")
    )

    grouped_items = defaultdict(list)

    for item in items:
        grouped_items[item.order].append(item)

    grouped_items = dict(grouped_items)

    return render(
        request,
        "admin_page/admin_service_section_contents.html",
        {
            "grouped_items": grouped_items,
            "data": section,
        }
    )

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            auth_login(request, user)
            messages.success(request, f"Welcome Admin {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid admin credentials.")

    return render(request, 'admin_page/admin_login.html')


def admin_logout(request):
    auth_logout(request)
    messages.info(request, "Admin logged out.")
    return redirect('admin_login')







# Customer #
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if User.objects.filter(username=username, userprofile__role='customer').exists():
            messages.error(request, "Username already exists. Please choose a different one.")
            return render(request, 'customer_page/register.html')

        if User.objects.filter(email=email, userprofile__role='customer').exists():
            messages.error(request, "Email already registered.")
            return render(request, 'customer_page/register.html')

        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

       
        UserProfile.objects.create(
            user=user,
            phone=phone,
            role='customer',
            status=True
        )

    

      
        try:
            subject = 'Welcome to Noah’s Ark Home Services'
            message = f""" Hi {username}, Thank you for registering wit Noah’s Ark Home Services! We are excited to have you onboard.
        Best regards,
        Noah’s Ark Team
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=True)
        except:
            pass

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'customer_page/register.html')



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if the user is a customer (not staff, not provider)
            profile = getattr(user, 'userprofile', None)
            if profile and profile.role == 'customer':
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('index')
            else:
                messages.error(request, "Invalid login for this portal.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'customer_page/login.html')


def logout(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')



@login_required(login_url='login')
def request_rework(request, request_id):
    """Customer requests rework once after completion."""
    booking_request = get_object_or_404(
        Booking_Request, id=request_id, customer__user_profile__user=request.user
    )

    if request.method == "POST" and booking_request.status == "completed":
        if booking_request.rework_count >= 1:
            messages.warning(request, "Rework already used for this booking.")
            return redirect('bookings')

        message = request.POST.get("rework_message")
        booking_request.status = "rework_pending"
        booking_request.rework_message = message
        booking_request.rework_count += 1
        booking_request.is_rework = True
        booking_request.save()

        messages.success(request, "Rework request submitted successfully.")
        return redirect('bookings')

    messages.error(request, "Invalid request or booking not eligible for rework.")
    return redirect('bookings')



#Providers#

def provider_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            profile = getattr(user, 'userprofile', None)
            if profile and profile.role == 'provider':
                auth_login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('provider_dashboard')
            else:
                messages.error(request, "Invalid login for provider portal.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'provider_page/provider_login.html')


def provider_logout(request):
    auth_logout(request)
    messages.info(request, "Provider logged out.")
    return redirect('provider_login')




@login_required(login_url='provider_login')
def provider_bookings(request):
 
    auto_cancel_expired()

    profile = getattr(request.user, 'userprofile', None)

    
    if not profile or profile.role != 'provider':
        messages.error(request, "Access denied. Only providers can access this page.")
        return redirect('provider_login')

    provider = Provider.objects.filter(user_profile=profile).first()


    booking_requests = Booking_Request.objects.filter(provider=provider).order_by('-id')

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        booking_request = get_object_or_404(Booking_Request, id=booking_id, provider=provider)

      
        if action == 'accept' and booking_request.status == 'pending':
            if booking_request.type == 'normal':
                accepted_count = Booking_Request.objects.filter(
                    provider=provider, date=booking_request.date, status='accepted'
                ).count()
                if accepted_count >= 6:
                    messages.error(request, "Capacity full for this date.")
                    return redirect('provider_bookings')

                service_date = timezone.make_aware(
                    timezone.datetime.combine(booking_request.date, timezone.now().time())
                )
            else:
                service_date = timezone.now()

            booking_request.status = 'accepted'
            booking_request.save()

            Booking.objects.get_or_create(
                booking_request=booking_request,
                defaults={'service_date': service_date}
            )
            messages.success(request, "Booking accepted successfully.")

      
        elif action == 'complete' and booking_request.status == 'accepted':
            booking = getattr(booking_request, 'booking', None)
            if booking and booking.is_paid:
                booking_request.status = 'completed'
                booking_request.save()
                messages.success(request, "Booking marked as completed.")
            else:
                messages.warning(request, "Customer has not completed payment yet.")

      
        elif action == 'accept_rework' and booking_request.status == 'rework_pending':
            booking_request.status = 'rework_accepted'
            booking_request.save()
            messages.success(request, "Rework request accepted.")

     
        elif action == 'rework_done' and booking_request.status == 'rework_accepted':
            booking_request.status = 'rework_completed'
            booking_request.is_rework = False
            booking_request.save()
            messages.success(request, "Rework completed successfully.")
        else:
            messages.warning(request, "Invalid action or status transition.")

        return redirect('provider_bookings')

    return render(request, 'provider_page/provider_bookings.html', {
        'booking_requests': booking_requests,
        'user_profile': profile,
        'provider': provider,
    })






@login_required(login_url='admin_login')
def dashboard(request):
   

   
    if not request.user.is_superuser:
        return redirect('admin_login')

    context={}
    service=Service.objects.all()
    context['service']=service
    context['service_count']=service.count()
    provider_count=UserProfile.objects.filter(role='provider').count()
    context['provider_count']=provider_count
    total_amount = Payment.objects.filter(payment_status='Success').aggregate(
        total=Sum('amount')
    )['total'] or 0

    context['total_amount'] = total_amount
    bookings=Booking.objects.all()
    context['bookings']=bookings
    reviews = Review.objects.all().order_by('-created_at')
    context['reviews']=reviews
    enquiries=Enquiry.objects.all()
    context['enquiries']=enquiries
    providers = Provider.objects.filter(service__isnull=False).distinct()
    context['providers']=providers
    context['booking_count']=bookings.count()
    
    


    return render(request, "admin_page/dashboard.html",context)



@login_required(login_url='provider_login')
def provider_dashboard(request):
    
    profile = getattr(request.user, 'userprofile', None)

    
    if not profile or profile.role != 'provider':
        messages.error(request, "Access denied. Only providers can access this page.")
        return redirect('provider_login')

    
    provider = Provider.objects.filter(user_profile=profile).first()
    booking_count=Booking.objects.all().count()
    bookings=Booking.objects.all()
    reviews = Review.objects.all().order_by('-created_at')
    total_amount = Payment.objects.filter(payment_status='Success').aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'service': Service.objects.all(),
        'service_count': Service.objects.count(),
        'provider_count': UserProfile.objects.filter(role='provider').count(),
        'user_profile': profile,
        'provider': provider, 
        'booking_count': booking_count,
        'total_amount': total_amount,
        'bookings': bookings,
        'reviews': reviews,
    }

    return render(request, "provider_page/provider_dashboard.html", context)



def index(request):
    
    services = Service.objects.filter(providers__isnull=False).distinct()

    providers = Provider.objects.filter(service__isnull=False).distinct()

    locations = Provider.objects.filter(service__isnull=False).values_list('location',flat=True).distinct()

    context = {
        'services': services,
        'providers': providers,
        'locations': locations,
    }

    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None
        context['user_profile'] = user_profile

    if request.method=="POST":
        if'save' in request.POST:
            name=request.POST.get('name')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            message=request.POST.get('message')
            enquiries=Enquiry.objects.create(name=name,email=email,phone=phone,message=message)
            enquiries.save()
            return HttpResponse("<script>alert('⚠️ Enquiries submitted successfully!'); window.location.href='';</script>")
           


    enquiry=Enquiry.objects.all()
    context['enquiry']=enquiry

    return render(request, "customer_page/index.html", context)

def contact(request):
    context={}
    services = Service.objects.filter(providers__isnull=False).distinct()

    providers = Provider.objects.filter(service__isnull=False).distinct()

    locations = Provider.objects.filter(service__isnull=False).values_list('location',flat=True).distinct()

    context = {
        'services': services,
        'providers': providers,
        'locations': locations,
    }
    if request.method=="POST":
        if'save' in request.POST:
            name=request.POST.get('name')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            message=request.POST.get('message')
            enquiries=Enquiry.objects.create(name=name,email=email,phone=phone,message=message)
            enquiries.save()
            return HttpResponse("<script>alert('⚠️ Enquiries submitted successfully!'); window.location.href='';</script>")
    enquiry=Enquiry.objects.all()
    context['enquiry']=enquiry

    return render(request, "customer_page/contact-us.html", context)
        

def about(request):
    services = Service.objects.filter(providers__isnull=False).distinct()

    providers = Provider.objects.filter(service__isnull=False).distinct()

    locations = Provider.objects.filter(service__isnull=False).values_list('location',flat=True).distinct()

    context = {
        'services': services,
        'providers': providers,
        'locations': locations,
    }
    return render(request,'customer_page/about.html',context)

def services(request):
    context={}
    locations = Provider.objects.filter(service__isnull=False).values_list('location',flat=True).distinct()
    services=Service.objects.all()
    context['services']=services
    context['locations']=locations
    return render(request,'customer_page/services.html',context)

def providers(request):
    context={}
    services = Service.objects.filter(providers__isnull=False).distinct()
    providers = Provider.objects.filter(service__isnull=False).distinct()
    locations = Provider.objects.filter(service__isnull=False).values_list('location',flat=True).distinct()
    context['providers']=providers
    context['services']=services
    context['locations']=locations
    return render(request,'customer_page/providers.html',context)



def service_view(request, name):
    service = get_object_or_404(Service, service_name=name)
    sections = ServiceSection.objects.filter(service=service).prefetch_related('items')
    providers = Provider.objects.filter(service=service)
    locations = providers.values_list('location', flat=True).distinct()

    # Get selected provider
    selected_provider = request.GET.get('provider')

    # Filter reviews by provider (if selected)
    reviews = Review.objects.filter(service=service).order_by('-created_at')
    if selected_provider:
        reviews = reviews.filter(provider_id=selected_provider)

    # Paginate after filtering
    paginator = Paginator(reviews, 6)  # 6 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'service': service,
        'sections': sections,
        'providers': providers,
        'reviews': page_obj,
        'selected_provider': selected_provider,
        'locations':locations,
    }
    return render(request, 'customer_page/service_view.html', context)

@login_required(login_url="admin_login")
def admin_services(request):

    if request.method == "POST":

        # =========================
        # ADD SERVICE
        # =========================
        if "save" in request.POST:

            service_name = request.POST.get("service_name", "").strip()
            price = request.POST.get("price", "").strip()
            image = request.FILES.get("image")

            if not service_name:
                messages.error(request, "Service name is required.")
                return redirect("admin_services")

            if not price:
                messages.error(request, "Service price is required.")
                return redirect("admin_services")

            Service.objects.create(
                service_name=service_name,
                price=price,
                image=image
            )

            messages.success(
                request,
                f"Service '{service_name}' added successfully."
            )

            # IMPORTANT
            return redirect("admin_services")


        # =========================
        # UPDATE SERVICE
        # =========================
        elif "update" in request.POST:

            service_id = request.POST.get("update")

            if not service_id:
                messages.error(request, "Service ID is missing.")
                return redirect("admin_services")

            service = get_object_or_404(
                Service,
                id=service_id
            )

            service_name = request.POST.get(
                "service_name",
                service.service_name
            ).strip()

            price = request.POST.get(
                "price",
                service.price
            )

            if not service_name:
                messages.error(request, "Service name is required.")
                return redirect("admin_services")

            service.service_name = service_name
            service.price = price

            # Only replace image if a new image was selected
            new_image = request.FILES.get("image")

            if new_image:
                service.image = new_image

            service.save()

            messages.success(
                request,
                f"Service '{service_name}' updated successfully."
            )

            # IMPORTANT
            return redirect("admin_services")


        # =========================
        # DELETE SERVICE
        # =========================
        elif "delete" in request.POST:

            service_id = request.POST.get("delete")

            if not service_id:
                messages.error(request, "Service ID is missing.")
                return redirect("admin_services")

            service = get_object_or_404(
                Service,
                id=service_id
            )

            service_name = service.service_name

            service.delete()

            messages.success(
                request,
                f"Service '{service_name}' deleted successfully."
            )

            # IMPORTANT
            return redirect("admin_services")


    # =========================
    # NORMAL PAGE LOAD
    # =========================

    services = Service.objects.all().order_by("id")
    providers = Provider.objects.all()

    context = {
        "services": services,
        "providers": providers,
    }

    return render(
        request,
        "admin_page/admin_services.html",
        context
    )
# def service_view(request):
#     context = {}
#     services = Service.objects.all()   # fetch all services
#     context['service'] = services
#     try:
#         user_profile=UserProfile.objects.get(user=request.user)
#         context['user_profile']=user_profile
#     except UserProfile.DoesNotExist:
#         context['user_profile']=None
#     return render(request, 'admin_page/admin_service_view.html', context)

def admin_service_add(request):
    return render(request,'admin_page/admin_service_add.html')

def admin_service_update(request):
    return render(request,'admin_page/admin_service_update.html')

@login_required(login_url="admin_login")
def admin_provider_view(request, id):
    provider = Provider.objects.get(user_profile__id=id)

    return render(request, "admin_page/admin_provider_view.html", {"provider": provider})




def admin_provider_view_update(request, id):
    provider = get_object_or_404(Provider, id=id)

    if request.method == "POST":
        if 'update' in request.POST:
            provider.location = request.POST.get('location')
            provider.experience_years = request.POST.get('experience_years')

            service_id = request.POST.get('service')
            if service_id:  
                try:
                    provider.service = Service.objects.get(id=service_id)
                except Service.DoesNotExist:
                    provider.service = None
            else:
                provider.service = None

            if request.FILES.get('photo'):
                provider.photo = request.FILES['photo']

            provider.save()
            messages.success(request, "Provider details updated successfully.")
            
            

    services = Service.objects.all()
    context = {
        'services': services,
        'provider': provider,
    }
    return render(request, 'admin_page/admin_provider_view_update.html', context)


def admin_service_provider(request, id):
    service = Service.objects.get(id=id)
    providers = service.providers.all()  

    context = {
        'service': service,
        'providers': providers
    }

    print(providers) 
    return render(request, 'admin_page/admin_service_provider.html', context)





def auto_cancel_expired():
    now = timezone.now()

    expired_requests = Booking_Request.objects.filter(status='pending', accept_deadline__lt=now)
    for req in expired_requests:
        req.status = 'cancelled'
        req.save()
        try:
            send_mail(
                subject='Booking Cancelled (No Provider Response)',
                message=f'Your booking for {req.service} on {req.date} was cancelled because the provider did not respond in time.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[req.customer.user_profile.user.email],
                fail_silently=True,
            )
        except Exception:
            pass

   
    unpaid_bookings = Booking.objects.filter(is_paid=False, payment_deadline__lt=now)
    for b in unpaid_bookings:
        req = b.booking_request
        if req.status not in ['completed', 'rework_pending', 'rework_accepted', 'rework_completed']:
            req.status = 'cancelled'
            req.save()
            try:
                send_mail(
                    subject='Booking Cancelled (Payment Not Received)',
                    message=f'Your booking for {req.service} on {req.date} was cancelled due to non-payment.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[req.customer.user_profile.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass


from django.db.models import DateField
from django.db.models.functions import Cast

@login_required(login_url='login')
def bookings(request):
    auto_cancel_expired()
    customer = get_object_or_404(Customer, user_profile__user=request.user)

    selected_service = request.GET.get('service', '').strip()
    selected_date = request.GET.get('date', '').strip()

    booking_requests = Booking_Request.objects.filter(customer=customer).order_by('-id')

    if selected_service:
        booking_requests = booking_requests.filter(service__service_name__iexact=selected_service)

    if selected_date:
        booking_requests = booking_requests.annotate(
            date_only=Cast('date', output_field=DateField())
        ).filter(date_only=selected_date)

    all_dates = (
        Booking_Request.objects.annotate(date_only=Cast('date', output_field=DateField()))
        .values_list('date_only', flat=True)
        .distinct()
        .order_by('-date_only')
    )

    services = Service.objects.all()
    locations = Provider.objects.filter(service__isnull=False).values_list('location',flat=True).distinct()

    return render(request, 'customer_page/bookings.html', {
        'booking_requests': booking_requests,
        'services': services,
        'all_dates': all_dates,
        'selected_service': selected_service,
        'selected_date': selected_date,
        'locations':locations,
    })


@login_required(login_url='login')
def check_availability(request):
    if request.method == 'POST':

        # Get values from the form
        service_name = request.POST.get('service', '').strip()
        location = request.POST.get('location', '').strip()
        booking_type = request.POST.get('booking_type')
        date_str = request.POST.get('date')

        # Find selected service
        try:
            service = Service.objects.get(
                service_name__iexact=service_name
            )
        except Service.DoesNotExist:
            return HttpResponse(
                "<script>"
                "alert('❌ This service is not provided.');"
                "window.history.back();"
                "</script>"
            )

        date = None

        # Normal booking requires a date
        if booking_type == 'normal' and date_str:
            try:
                date = timezone.datetime.strptime(
                    date_str,
                    '%Y-%m-%d'
                ).date()
            except ValueError:
                return HttpResponse(
                    "<script>"
                    "alert('⚠️ Invalid date format!');"
                    "window.history.back();"
                    "</script>"
                )

        # Find providers offering this service at this location
        providers = Provider.objects.filter(
            service=service,
            location__iexact=location
        ).distinct()

        # Check provider capacity for normal booking
        if booking_type == 'normal' and date:

            available_providers = []

            for provider in providers:

                count = Booking_Request.objects.filter(
                    provider=provider,
                    date=date,
                    status__in=['pending', 'accepted']
                ).count()

                if count < 6:
                    available_providers.append(provider)

            providers = available_providers

        elif booking_type == 'emergency':
            providers = list(providers)

        # No providers available
        if not providers:
            return HttpResponse(
                "<script>"
                "alert('❌ No available providers found for this service and location.');"
                "window.history.back();"
                "</script>"
            )

        # Emergency booking uses today's date
        if booking_type == 'emergency':
            date = timezone.now().date()

        return render(
            request,
            'customer_page/book_service.html',
            {
                'selected_service': service,
                'selected_location': location,
                'providers': providers,
                'booking_type': booking_type,
                'date': date,
            }
        )

    return redirect('index')


@login_required(login_url='login')
def book_service(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        provider_id = request.POST.get('provider')
        location = request.POST.get('location')
        req_type = request.POST.get('type')
        date_str = request.POST.get('date')

        service = get_object_or_404(Service, id=service_id)
        provider = get_object_or_404(Provider, id=provider_id)
        customer = get_object_or_404(Customer, user_profile__user=request.user)

        date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

        Booking_Request.objects.create(
            customer=customer,
            provider=provider,
            service=service,
            location=location,
            date=date,
            type=req_type,
            status='pending'
        )

        return HttpResponse("<script>alert('✅ Booking created successfully!'); window.location.href='/bookings/';</script>")

    return redirect('index')



@login_required(login_url='login')
def customer_pay(request, booking_id):
  
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        booking_request__customer__user_profile__user=request.user
    )

    amount = int(booking.booking_request.service.price * 100)

  
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.booking_request.service.price,
            'payment_status': 'Pending',
        }
    )

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    payment.provider_order_id = order['id']
    payment.save()

    context = {
        'booking': booking,
        'payment': payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
    }

    return render(request, 'customer_page/payment.html', context)



@csrf_exempt
def payment_callback(request):
    """Handles Razorpay payment verification and updates booking status."""
    if request.method == 'POST':
        data = request.POST
        order_id = data.get('razorpay_order_id')
        payment_id = data.get('razorpay_payment_id')
        signature = data.get('razorpay_signature')

        try:
            payment = Payment.objects.get(provider_order_id=order_id)
        except Payment.DoesNotExist:
            return HttpResponse("<script>alert('Payment record not found.'); window.location.href='/bookings/';</script>")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            })

            payment.payment_status = 'Success'
            payment.razorpay_payment_id = payment_id
            payment.signature_id = signature
            payment.save()

            booking = payment.booking
            booking.is_paid = True
            booking.save()

            booking.booking_request.save()

         
            send_mail(
                subject='Payment Successful',
                message=f'Your payment for {booking.booking_request.service} was successful.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.booking_request.customer.user_profile.user.email],
                fail_silently=True,
            )

            return HttpResponse("<script>alert('✅ Payment successful!'); window.location.href='/bookings/';</script>")

        except razorpay.errors.SignatureVerificationError:
            payment.payment_status = 'Failure'
            payment.save()
            return HttpResponse("<script>alert('❌ Payment verification failed.'); window.location.href='/bookings/';</script>")

    return HttpResponse("<script>alert('Invalid request.'); window.location.href='/bookings/';</script>")






@login_required(login_url='login')
def cancel_booking(request, request_id):
    booking_request = get_object_or_404(Booking_Request, id=request_id, customer__user_profile__user=request.user)
    if hasattr(booking_request, 'booking') and booking_request.booking.is_paid:
        return HttpResponse("<script>alert('Cannot cancel after payment!'); window.location.href='/bookings/';</script>")
    booking_request.status = 'cancelled'
    booking_request.save()
    return HttpResponse("<script>alert('Booking cancelled'); window.location.href='/bookings/';</script>")




@login_required(login_url='login')
def leave_review(request, booking_id):  
    booking_request = get_object_or_404(Booking_Request, id=booking_id)
    booking = getattr(booking_request, 'booking', None)

    if not booking:
        messages.error(request, "No booking found for this request.")
        return redirect('bookings')

    service = booking_request.service
    provider = booking_request.provider
    customer = booking_request.customer

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        
        if not rating or not comment.strip():
            messages.error(request, "Please fill in all fields.")
        else:
            Review.objects.create(
                booking=booking,
                service=service,
                provider=provider,
                customer=customer,
                rating=int(rating),
                comment=comment.strip()
            )
            messages.success(request, "Review submitted successfully.")
         
            return redirect('leave_review', booking_request.id)

    reviews = Review.objects.filter(service=service).order_by('-created_at')
    locations = Provider.objects.filter(service__isnull=False).values_list('location',flat=True).distinct()

    return render(request, 'customer_page/review.html', {
        'service': service,
        'booking': booking,
        'booking_request': booking_request,
        'provider': provider,
        'reviews': reviews,
        'locations': locations,
    })




@login_required(login_url='login')
def all_reviews(request):
    
    services = Service.objects.all()
    providers = UserProfile.objects.filter(role='provider')

    selected_service = request.GET.get('service')
    selected_provider = request.GET.get('provider')

    reviews = Review.objects.select_related('service', 'provider', 'customer').order_by('-created_at')
    locations = Provider.objects.filter(service__isnull=False).values_list('location',flat=True).distinct()

    # ✅ Apply filters only if valid
    if selected_service and selected_service != 'None':
        reviews = reviews.filter(service_id=selected_service)
    if selected_provider and selected_provider != 'None':
        reviews = reviews.filter(provider_id=selected_provider)

  
    paginator = Paginator(reviews, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customer_page/review_display.html', {
        'reviews': page_obj,
        'services': services,
        'providers': providers,
        'selected_service': selected_service,
        'selected_provider': selected_provider,
        'locations':locations,
    })


@login_required(login_url="admin_login")
def admin_booking_list(request):
    
    bookings = Booking.objects.select_related(
        "booking_request__customer__user_profile__user",
        "booking_request__provider__user_profile__user",
        "booking_request__service"
    ).order_by("-booking_date")

    
    service_id = request.GET.get("service")
    provider_id = request.GET.get("provider")
    booking_type = request.GET.get("type")
    date = request.GET.get("date")

    
    if service_id and service_id != "":
        bookings = bookings.filter(booking_request__service_id=service_id)

    if provider_id and provider_id != "":
        bookings = bookings.filter(booking_request__provider_id=provider_id)

    if booking_type and booking_type != "":
        bookings = bookings.filter(booking_request__type=booking_type)

    if date and date != "":
        bookings = bookings.filter(booking_request__date=date)

    
    services = Service.objects.all()
    providers = Provider.objects.all()

    context = {
        "bookings": bookings,
        "services": services,
        "providers": providers,
        "selected_service": service_id,
        "selected_provider": provider_id,
        "selected_type": booking_type,
        "selected_date": date,
    }

    return render(request, "admin_page/admin_booking_list.html", context)


@login_required(login_url="admin_login")
def admin_booking_detail(request, id):
    booking = get_object_or_404(Booking, id=id)
    return render(request, "admin_page/admin_booking_detail.html", {"booking": booking})

@login_required(login_url='admin_login')
def admin_customer_list(request):
 
    customers = Customer.objects.select_related('user_profile__user').all()

    for customer in customers:
        customer.total_bookings = Booking.objects.filter(booking_request__customer=customer).count()

    context = {
        'customers': customers,
    }
    return render(request, 'admin_page/admin_customer_list.html', context)

@login_required(login_url='admin_login')
def admin_enquiry_list(request):
    enquiries = Enquiry.objects.all().order_by('-created_at')
    return render(request, 'admin_page/admin_enquiry_list.html', {'enquiries': enquiries})

@login_required(login_url='admin_login')
def admin_enquiry_detail(request, id):
    enquiry = get_object_or_404(Enquiry, id=id)
    return render(request, 'admin_page/admin_enquiry_detail.html', {'enquiry': enquiry})

@login_required(login_url="admin_login")
def admin_payment_list(request):
    payments = Payment.objects.select_related(
        "booking__booking_request__customer__user_profile__user",
        "booking__booking_request__provider__user_profile__user",
        "booking__booking_request__service"
    ).order_by("-payment_date")

    return render(request, "admin_page/admin_payment_list.html", {"payments": payments})

@login_required(login_url="admin_login")
def review_list(request):
    services = Service.objects.all()
    providers = Provider.objects.all()

  
    service_filter = request.GET.get('service')
    provider_filter = request.GET.get('provider')

    reviews = Review.objects.all().order_by('-created_at')

    if service_filter and service_filter != '':
        reviews = reviews.filter(service__id=service_filter)
    if provider_filter and provider_filter != '':
        reviews = reviews.filter(provider__id=provider_filter)

    context = {
        'reviews': reviews,
        'services': services,
        'providers': providers,
        'selected_service': service_filter,
        'selected_provider': provider_filter,
    }
    return render(request, 'admin_page/review_list.html', context)

@login_required(login_url="provider_login")
def provider_service(request):
    context={}
    services = Service.objects.filter(providers__isnull=False)
    context['services']=services
    profile = getattr(request.user, 'userprofile', None)



    provider = Provider.objects.filter(user_profile=profile).first()
    context['userprofile']=profile
    context['provider']=provider

    return render(request,'provider_page/provider_service.html',context)

@login_required(login_url="provider_login")
def provider_review(request):
    services = Service.objects.filter(providers__isnull=False)
    providers = Provider.objects.all()
    reviews = Review.objects.all().order_by('-created_at')
    profile = getattr(request.user, 'userprofile', None)

    provider = Provider.objects.filter(user_profile=profile).first()
    context = {
        'reviews': reviews,
        'services': services,
        'providers': providers, 
        'userprofile': profile,
        'provider': provider,
    }
    return render(request, 'provider_page/provider_review.html', context)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('id')
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['service_name']

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all().order_by('id')
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['location']

class IsBookingCustomer(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.customer.user_profile.user == request.user


class BookingRequestViewSet(viewsets.ModelViewSet):
    queryset = Booking_Request.objects.select_related(
        'customer',
        'provider',
        'service'
    ).all().order_by('id')

    serializer_class = BookingRequestSerializer

    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsBookingCustomer
    ]

    filterset_fields = [
        'status',
        'type',
        'is_rework'
    ]

    search_fields = ['location']

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            return queryset.filter(
                customer__user_profile__user=self.request.user
            )

        return queryset.none()

    def perform_create(self, serializer):
        profile = UserProfile.objects.get(
            user=self.request.user,
            role='customer'
        )

        customer = Customer.objects.get(
            user_profile=profile
        )

        serializer.save(customer=customer)