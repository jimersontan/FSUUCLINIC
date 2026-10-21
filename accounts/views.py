import json

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from admin_dashboard.models import Appointment, Doctor, InventoryItem

from .forms import LoginForm, RegisterForm
from .models import Message, User, UserRole
from .utils import is_default_admin


def landing_page(request):
    if request.user.is_authenticated:
        if is_default_admin(request.user):
            return redirect('admin_dashboard')
        if request.user.role == UserRole.STAFF:
            return redirect('staff_dashboard')
        if request.user.role == UserRole.ADMIN:
            return redirect('admin_dashboard')

    doctors = [doctor for doctor in Doctor.objects.filter(is_archived=False).order_by('name') if doctor.is_publicly_visible()]
    return render(
        request,
        'landing.html',
        {
            'doctors': doctors,
            'login_form': LoginForm(request),
            'register_form': RegisterForm(),
        },
    )


def home_view(request):
    return landing_page(request)


def register_view(request):
    if request.user.is_authenticated:
        if request.user.role == UserRole.ADMIN:
            return redirect('admin_dashboard')
        return redirect('patient_dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your account was created successfully.')
        return redirect('patient_dashboard')

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if is_default_admin(request.user):
            return redirect('admin_dashboard')
        if request.user.role == UserRole.STAFF:
            return redirect('staff_dashboard')
        if request.user.role == UserRole.ADMIN:
            return redirect('admin_dashboard')
        return redirect('patient_dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Welcome back, {request.user.username}!')
        if is_default_admin(request.user):
            return redirect('admin_dashboard')
        if request.user.role == UserRole.STAFF:
            return redirect('staff_dashboard')
        if request.user.role == UserRole.ADMIN:
            return redirect('admin_dashboard')
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('patient_dashboard')

    return render(request, 'registration/login.html', {
        'form': form,
        'next_url': request.POST.get('next') or request.GET.get('next', ''),
    })


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def messages_page(request):
    if request.user.role in {UserRole.ADMIN, UserRole.STAFF}:
        contacts = User.objects.filter(role=UserRole.PATIENT).order_by('username')
        home_url = '/admin-dashboard/'
    else:
        contacts = User.objects.filter(role=UserRole.ADMIN).order_by('username')
        home_url = '/dashboard/'

    contact_id = request.GET.get('recipient') or (contacts.first().id if contacts.exists() else None)
    selected_contact = None
    thread = []
    selected_contact_profile_url = '#profile-modal'
    selected_contact_recent_appointments = []
    unread_counts = {}
    for contact in contacts:
        unread_counts[contact.id] = Message.objects.filter(
            recipient=request.user,
            sender=contact,
            is_read=False,
            is_unsent=False,
            deleted_by_recipient=False,
        ).count()

    if contact_id:
        selected_contact = User.objects.filter(pk=contact_id).first()
        if selected_contact:
            thread = Message.objects.filter(
                (Q(sender=request.user, recipient=selected_contact) & Q(deleted_by_sender=False)) |
                (Q(sender=selected_contact, recipient=request.user) & Q(deleted_by_recipient=False))
            ).order_by('created_at')
            Message.objects.filter(recipient=request.user, sender=selected_contact, is_read=False, is_unsent=False).update(is_read=True)
            unread_counts[selected_contact.id] = 0

            if selected_contact.role == UserRole.PATIENT and request.user.role in {UserRole.ADMIN, UserRole.STAFF}:
                selected_contact_profile_url = f'/admin/patient/{selected_contact.id}/'
            elif selected_contact.role == UserRole.ADMIN and request.user.role == UserRole.PATIENT:
                selected_contact_profile_url = f'/profile/view/{selected_contact.id}/'
            elif selected_contact.role == UserRole.ADMIN and request.user.role == UserRole.ADMIN:
                selected_contact_profile_url = '#profile-modal'
            else:
                selected_contact_profile_url = '#profile-modal'

            recent_appt_qs = None
            if request.user.role in {UserRole.ADMIN, UserRole.STAFF} and selected_contact.role == UserRole.PATIENT:
                recent_appt_qs = selected_contact.appointments.filter(status__in=['COMPLETED', 'CONFIRMED', 'CANCELLED']).order_by('-date', '-time')[:3]
            elif request.user.role == UserRole.PATIENT and selected_contact.role in {UserRole.ADMIN, UserRole.STAFF}:
                recent_appt_qs = selected_contact.appointments.filter(status__in=['COMPLETED', 'CONFIRMED', 'CANCELLED']).order_by('-date', '-time')[:3]

            if recent_appt_qs is not None:
                selected_contact_recent_appointments = list(recent_appt_qs.select_related('doctor'))

    return render(
        request,
        'messages.html',
        {
            'contacts': contacts,
            'selected_contact': selected_contact,
            'thread': thread,
            'unread_counts': unread_counts,
            'home_url': home_url,
            'selected_contact_profile_url': selected_contact_profile_url,
            'selected_contact_recent_appointments': selected_contact_recent_appointments,
        },
    )


@login_required
def send_message(request):
    if request.method != 'POST':
        return redirect('messages_page')

    recipient_id = request.POST.get('recipient')
    body = (request.POST.get('body') or '').strip()
    subject = (request.POST.get('subject') or 'New message').strip() or 'New message'

    if not recipient_id or not body:
        messages.error(request, 'Please select a person and write a message before sending.')
        return redirect('messages_page')

    recipient = User.objects.filter(pk=recipient_id).first()
    if not recipient:
        messages.error(request, 'The recipient could not be found.')
        return redirect('messages_page')

    if request.user.role in {UserRole.ADMIN, UserRole.STAFF} and recipient.role != UserRole.PATIENT:
        messages.error(request, 'Clinic staff can only message patients.')
        return redirect('messages_page')
    if request.user.role == UserRole.PATIENT and recipient.role not in {UserRole.ADMIN, UserRole.STAFF}:
        messages.error(request, 'Patients can only message clinic staff.')
        return redirect('messages_page')

    Message.objects.create(sender=request.user, recipient=recipient, subject=subject, body=body)
    messages.success(request, 'Message sent successfully.')
    return redirect(f"/messages/?recipient={recipient.id}")


@login_required
def notification_payload(request):
    unread_messages = Message.objects.filter(
        recipient=request.user,
        is_read=False,
        is_unsent=False,
        deleted_by_recipient=False,
    )
    unread_count = unread_messages.count()
    items = []
    notification_count = 0

    if request.user.role in {UserRole.ADMIN, UserRole.STAFF}:
        pending_appointments = Appointment.objects.filter(
            status=Appointment.Status.PENDING,
            is_archived=False,
        ).select_related('patient', 'doctor').order_by('-created_at')
        low_stock_items = InventoryItem.objects.filter(quantity__lte=10).order_by('quantity', 'name')

        pending_count = pending_appointments.count()
        low_stock_count = low_stock_items.count()
        notification_count = pending_count + low_stock_count

        appointment_url = (
            reverse('staff_dashboard')
            if request.user.role == UserRole.STAFF
            else f"{reverse('admin_dashboard')}?tab=appointments"
        )
        items.extend(
            {
                'title': 'New appointment booking',
                'description': (
                    f"{appointment.patient.get_full_name() or appointment.patient.username} "
                    f"booked {appointment.doctor.name} for {appointment.date:%b %d, %Y}."
                ),
                'url': appointment_url,
                'icon': 'bi-calendar-check',
                'variant': 'success',
            }
            for appointment in pending_appointments[:5]
        )
        items.extend(
            {
                'title': 'Out of stock' if item.quantity == 0 else 'Low stock',
                'description': f'{item.name}: {item.quantity} remaining.',
                'url': reverse('inventory'),
                'icon': 'bi-exclamation-octagon' if item.quantity == 0 else 'bi-exclamation-triangle',
                'variant': 'danger' if item.quantity == 0 else 'warning',
            }
            for item in low_stock_items[:max(0, 5 - len(items))]
        )

    return JsonResponse({
        'count': notification_count,
        'message_count': unread_count,
        'items': items,
    })


@login_required
@require_POST
def delete_or_unsend_message(request, message_id):
    message_obj = get_object_or_404(Message, pk=message_id)

    is_sender = (message_obj.sender == request.user)
    is_recipient = (message_obj.recipient == request.user)
    is_admin_or_staff = (
        request.user.role in {UserRole.ADMIN, UserRole.STAFF}
        or request.user.is_staff
        or request.user.is_superuser
    )

    if not (is_sender or is_recipient or is_admin_or_staff):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
            return JsonResponse({'success': False, 'error': 'You do not have permission to modify this message.'}, status=403)
        messages.error(request, 'You do not have permission to delete or unsend this message.')
        return redirect('messages_page')

    action = (request.POST.get('action') or '').strip().lower()
    if not action:
        action = 'unsend' if (is_sender or is_admin_or_staff) else 'delete_for_me'

    target_contact_id = message_obj.recipient_id if is_sender else message_obj.sender_id

    if action == 'unsend':
        if not (is_sender or is_admin_or_staff):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
                return JsonResponse({'success': False, 'error': 'Only the sender or admin can unsend a message for everyone.'}, status=403)
            messages.error(request, 'Only the sender can unsend this message.')
            return redirect(f"/messages/?recipient={target_contact_id}")

        message_obj.is_unsent = True
        message_obj.save(update_fields=['is_unsent'])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
            sender_name = message_obj.sender.get_full_name() or message_obj.sender.username
            return JsonResponse({
                'success': True,
                'action': 'unsend',
                'message_id': message_obj.id,
                'is_sender': is_sender,
                'unsent_label_self': 'You unsent a message',
                'unsent_label_other': f"{sender_name} unsent a message",
            })
        messages.success(request, 'Message unsent.')
        return redirect(f"/messages/?recipient={target_contact_id}")

    elif action in {'delete_for_me', 'delete_me'}:
        if is_sender:
            message_obj.deleted_by_sender = True
            message_obj.save(update_fields=['deleted_by_sender'])
        elif is_recipient:
            message_obj.deleted_by_recipient = True
            message_obj.save(update_fields=['deleted_by_recipient'])
        elif is_admin_or_staff:
            message_obj.deleted_by_sender = True
            message_obj.save(update_fields=['deleted_by_sender'])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
            return JsonResponse({'success': True, 'action': 'delete_for_me', 'message_id': message_obj.id})
        messages.success(request, 'Message removed for you.')
        return redirect(f"/messages/?recipient={target_contact_id}")

    elif action in {'delete_for_everyone', 'delete_everyone'}:
        if not (is_sender or is_admin_or_staff):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
                return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
            messages.error(request, 'You cannot delete this message for everyone.')
            return redirect(f"/messages/?recipient={target_contact_id}")

        message_obj.deleted_by_sender = True
        message_obj.deleted_by_recipient = True
        message_obj.is_unsent = True
        message_obj.save(update_fields=['deleted_by_sender', 'deleted_by_recipient', 'is_unsent'])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
            return JsonResponse({'success': True, 'action': 'delete_for_everyone', 'message_id': message_obj.id})
        messages.success(request, 'Message deleted for everyone.')
        return redirect(f"/messages/?recipient={target_contact_id}")

    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
            return JsonResponse({'success': False, 'error': 'Invalid action specified.'}, status=400)
        return redirect(f"/messages/?recipient={target_contact_id}")


@login_required
def user_profile_detail(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if request.user.role == UserRole.ADMIN and target_user.role == UserRole.PATIENT:
        appointments = Appointment.objects.filter(patient=target_user).select_related('doctor').order_by('-date', '-time')[:5]
        home_url = '/admin-dashboard/'
        fallback_url = '/messages/'
        edit_url = '/admin-dashboard/'
        return render(
            request,
            'profile_view.html',
            {
                'profile_user': target_user,
                'appointments': appointments,
                'home_url': home_url,
                'fallback_url': fallback_url,
                'edit_url': edit_url,
            },
        )

    if request.user.role == UserRole.PATIENT and target_user.role in {UserRole.ADMIN, UserRole.PATIENT}:
        appointments = Appointment.objects.filter(patient=request.user).select_related('doctor').order_by('-date', '-time')[:5]
        home_url = '/dashboard/'
        fallback_url = '/messages/'
        edit_url = '/dashboard/profile/'
        return render(
            request,
            'profile_view.html',
            {
                'profile_user': target_user,
                'appointments': appointments,
                'home_url': home_url,
                'fallback_url': fallback_url,
                'edit_url': edit_url,
            },
        )

    if request.user == target_user:
        appointments = Appointment.objects.filter(patient=request.user).select_related('doctor').order_by('-date', '-time')[:5]
        home_url = '/dashboard/'
        fallback_url = '/dashboard/'
        edit_url = '/dashboard/profile/'
        return render(
            request,
            'profile_view.html',
            {
                'profile_user': target_user,
                'appointments': appointments,
                'home_url': home_url,
                'fallback_url': fallback_url,
                'edit_url': edit_url,
            },
        )

    return redirect('messages_page')
