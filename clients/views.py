from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.rbac import ADMIN, AUDITOR, MANAGER, can_edit_business_data, require_roles
from security.services import log_security_event

from .forms import ClientForm
from .models import Client


@require_roles(ADMIN, MANAGER, AUDITOR)
def client_list(request):
    clients = Client.objects.all()
    query = request.GET.get('q')
    if query:
        clients = clients.filter(full_name__icontains=query)
    return render(request, 'clients/client_list.html', {'clients': clients, 'query': query or ''})


@require_roles(ADMIN, MANAGER, AUDITOR)
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/client_detail.html', {'client': client})


@require_roles(ADMIN, MANAGER)
def client_create(request):
    form = ClientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        client = form.save(commit=False)
        client.created_by = request.user
        client.save()
        log_security_event(
            request=request,
            event_type='client_created',
            description=f'Создан клиент {client.full_name}',
            risk_level='low',
        )
        messages.success(request, 'Клиент создан.')
        return redirect('clients:detail', pk=client.pk)
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Новый клиент'})


@require_roles(ADMIN, MANAGER)
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if request.method == 'POST' and form.is_valid():
        client = form.save()
        log_security_event(
            request=request,
            event_type='client_updated',
            description=f'Обновлен клиент {client.full_name}',
            risk_level='low',
        )
        messages.success(request, 'Клиент обновлен.')
        return redirect('clients:detail', pk=client.pk)
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Редактирование клиента'})


@require_roles(ADMIN, MANAGER)
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not can_edit_business_data(request.user):
        raise PermissionDenied
    if request.method == 'POST':
        name = client.full_name
        client.delete()
        log_security_event(
            request=request,
            event_type='client_deleted',
            description=f'Удален клиент {name}',
            risk_level='medium',
        )
        messages.success(request, 'Клиент удален.')
        return redirect('clients:list')
    return render(request, 'clients/client_confirm_delete.html', {'client': client})
