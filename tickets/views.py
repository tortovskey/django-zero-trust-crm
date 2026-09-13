from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.rbac import ADMIN, AUDITOR, MANAGER, SECURITY, USER, get_role, log_denied, require_roles
from security.services import log_security_event

from .forms import TicketForm
from .models import Ticket


def _visible_tickets(user):
    role = get_role(user)
    if role == USER:
        return Ticket.objects.filter(requester=user)
    return Ticket.objects.all()


@require_roles(ADMIN, MANAGER, AUDITOR, SECURITY, USER)
def ticket_list(request):
    tickets = _visible_tickets(request.user).select_related('client', 'responsible_manager', 'requester')
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    query = request.GET.get('q')
    if status:
        tickets = tickets.filter(status=status)
    if priority:
        tickets = tickets.filter(priority=priority)
    if query:
        tickets = tickets.filter(Q(subject__icontains=query) | Q(client__full_name__icontains=query))
    return render(
        request,
        'tickets/ticket_list.html',
        {
            'tickets': tickets,
            'status': status or '',
            'priority': priority or '',
            'query': query or '',
            'statuses': Ticket.Status.choices,
            'priorities': Ticket.Priority.choices,
        },
    )


@require_roles(ADMIN, MANAGER, AUDITOR, SECURITY, USER)
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket.objects.select_related('client', 'responsible_manager', 'requester'), pk=pk)
    if get_role(request.user) == USER and ticket.requester_id != request.user.id:
        log_denied(request, f'Попытка просмотра чужой заявки {ticket.number}')
        raise PermissionDenied
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@require_roles(ADMIN, MANAGER, USER)
def ticket_create(request):
    form = TicketForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.requester = request.user
        if get_role(request.user) == USER:
            ticket.status = Ticket.Status.NEW
            ticket.responsible_manager = None
        ticket.save()
        log_security_event(
            request=request,
            event_type='ticket_created',
            description=f'Создана заявка {ticket.number}',
            risk_level='low',
        )
        messages.success(request, 'Заявка создана.')
        return redirect('tickets:detail', pk=ticket.pk)
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Новая заявка'})


@require_roles(ADMIN, MANAGER)
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketForm(request.POST or None, instance=ticket, user=request.user)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save()
        log_security_event(
            request=request,
            event_type='ticket_updated',
            description=f'Обновлена заявка {ticket.number}',
            risk_level='low',
        )
        messages.success(request, 'Заявка обновлена.')
        return redirect('tickets:detail', pk=ticket.pk)
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Редактирование заявки'})


@require_roles(ADMIN, MANAGER)
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        number = ticket.number
        ticket.delete()
        log_security_event(
            request=request,
            event_type='ticket_updated',
            description=f'Удалена заявка {number}',
            risk_level='medium',
        )
        messages.success(request, 'Заявка удалена.')
        return redirect('tickets:list')
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})
