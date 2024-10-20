from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.http import JsonResponse

from .forms import PropertyForm, RentPropertyForm
from .models import *
from .utils import *


def landing(request):
    """
    Render the landing page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered landing page.
    """
    if request.user.is_authenticated:
        return redirect("home")
    
    return render(request, "core/landing.html")


@login_required
def home(request):
    """
    This view renders the home page template with the user's available properties,
    rented properties, and recent activities and notifications.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered home page.
    """
    available_properties = Property.objects.filter(
        user=request.user, is_rented=False
    ).order_by("created_at")

    rented_properties = Property.objects.filter(
        user=request.user, is_rented=True
    ).order_by("property_rentals__end_date")

    recent_activities = (
        RecentActivity.objects.filter(user=request.user)
        .exclude(activity_type="overdue")
        .order_by("-timestamp")[:10]
    )

    notifications = Notifications.objects.filter(user=request.user, is_read=False)

    expiring_contracts = get_expiring_contracts(rented_properties)
    upcoming_payments = get_upcoming_payments(rented_properties)
    monthly_revenue = get_monthly_revenue(rented_properties)

    payment_status_counts = get_payment_status_chart(request.user)

    context = {
        "available_properties": available_properties,
        "rented_properties": rented_properties,
        "expiring_contracts": expiring_contracts,
        "upcoming_payments": upcoming_payments,
        "recent_activities": recent_activities,
        "notifications": notifications,
        "monthly_revenue": monthly_revenue,
        "payment_status_counts": payment_status_counts,
    }

    return render(request, "core/home.html", context)


@login_required
def add_property(request):
    """
    This view add a new property to the user's list of properties.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        if request.method == "POST":
            HttpResponse: Redirects to the all_properties view.
        else:
            HttpResponse: The adding property form.
    """
    if request.method == "POST":
        try:
            form = PropertyForm(request.POST, action="add")
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                instance.save()
                return redirect("all_properties")
        except Exception as e:
            form.add_error(None, str(e))
    else:
        form = PropertyForm(action="add")

    return render(request, "forms/add_property_form.html", {"form": form})


@login_required
def edit_property(request, pk):
    instance = get_object_or_404(Property, id=pk)

    if request.method == "POST":
        form = PropertyForm(request.POST, instance=instance, action="edit")
        if form.is_valid():
            try:
                form.save()
                return redirect("all_properties")
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = PropertyForm(instance=instance, action="edit")

    return render(
        request, "forms/edit_property_form.html", {"form": form, "property": instance}
    )


@login_required
def view_property(request, pk):
    """
    This view display the details of a property.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the property to view.

    Returns:
        HttpResponse: The details of the property.
    """
    property = get_object_or_404(Property, id=pk)
    rental_histories = RentHistory.objects.filter(property_id=pk)

    context = {}
    if property.is_rented:
        instance = get_object_or_404(RentProperty, property=property)
        context["rent_property"] = instance
    context["property"] = property
    context["rental_histories"] = rental_histories

    return render(request, "includes/view_property.html", context)


@login_required
def delete_property(request, pk):
    """
    This view delete a property owned by the user.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the property to delete.

    Returns:
        HttpResponse: The list of all properties owned by the user.
    """
    instance = get_object_or_404(Property, id=pk)
    instance.delete()

    all_properties = Property.objects.filter(user=request.user)
    return render(
        request, "includes/all_properties.html", {"all_properties": all_properties}
    )


@login_required
def rent_property(request, pk):
    """
    This view rent a property to a tenant.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the property to rent.

    Returns:
        if request.method == "POST":
            HttpResponse: Redirects to the all_properties view.
        else:
            HttpResponse: The rent property form.
    """
    instance = get_object_or_404(Property, id=pk)

    if request.method == "POST":
        form = RentPropertyForm(request.POST, request.FILES, property=instance)
        if form.is_valid():
            name = form.cleaned_data.get("tenant_name")
            phone_number = form.cleaned_data.get("tenant_phone_number")
            try:
                if phone_number.startswith("+"):
                    tenant, created = Tenant.objects.get_or_create(
                        name=name.title(),
                        phone_number=phone_number,
                        defaults={"id_image": form.cleaned_data.get("tenant_image")},
                    )
                    rent_property = form.save(commit=False)
                    rent_property.property = instance
                    rent_property.tenant = tenant
                    instance.is_rented = True
                    instance.save()
                    rent_property.save()
                    return redirect("all_properties")
                else:
                    raise ValueError(
                        "Phone number must start with '+', Format: +249912345678"
                    )
            except Exception as e:
                form.add_error(None, str(e))
                return render(
                    request,
                    "forms/rent_property_form.html",
                    {"form": form, "property": instance},
                )
    else:
        form = RentPropertyForm(property=instance)

    return render(
        request, "forms/rent_property_form.html", {"form": form, "property": instance}
    )


@login_required
def edit_rental(request, pk):
    """
    This view edit a rented property.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the rented property to edit.

    Returns:
        if request.method == "POST":
            HttpResponse: Redirects to the view_property view.
        else:
            HttpResponse: The edit rental form.
    """
    rental = get_object_or_404(RentProperty, id=pk)
    tenant = rental.tenant

    if request.method == "POST":
        form = RentPropertyForm(
            request.POST, request.FILES, instance=rental, tenant=tenant, action="edit"
        )
        if form.is_valid():
            name = form.cleaned_data.get("tenant_name")
            phone_number = form.cleaned_data.get("tenant_phone_number")

            try:
                if phone_number.startswith("+"):
                    tenant.name = name
                    tenant.phone_number = phone_number
                    tenant.id_image = form.cleaned_data.get("tenant_image")
                    tenant.save()
                    form.save()
                    return redirect("view_property", pk=rental.property.id)
                else:
                    raise ValueError(
                        "Phone number must start with '+', Format: +249912345678"
                    )
            except Exception as e:
                form.add_error(None, str(e))
                return render(
                    request,
                    "forms/edit_rental_form.html",
                    {"form": form, "rental": rental},
                )
    else:
        form = RentPropertyForm(instance=rental, tenant=tenant, action="edit")

    return render(
        request, "forms/edit_rental_form.html", {"form": form, "rental": rental}
    )


@login_required
def all_properties(request):
    """
    This view all properties owned by the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The list of all properties owned by the user.
    """
    my_properties = Property.objects.filter(user=request.user)
    context = {"all_properties": my_properties}
    return render(request, "includes/all_properties.html", context)


@login_required
def search_all_properties(request):
    """
    This view search all properties owned by the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The list of all properties owned by the user that match the search query.
    """
    q = request.GET.get("q", None)

    if q:
        Properties = Property.objects.filter(
            Q(name__icontains=q) | Q(country__icontains=q)
        ).distinct()
    else:
        Properties = Property.objects.all()
        return render(
            request,
            "includes/all_properties.html",
            {"all_properties": Properties},
        )

    return render(
        request, "includes/all_properties.html", {"all_properties": Properties}
    )


@login_required
def mark_as_paid(request, pk):
    """
    This view mark a rental payment as paid.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the rented property to mark as paid.

    Returns:
        HttpResponse: The list of upcoming payments.
    """
    instance = get_object_or_404(RentProperty, id=pk)

    if instance:
        instance.status = "paid"
        instance.save()

        rented_properties = Property.objects.filter(
            user=request.user, is_rented=True
        ).order_by("property_rentals__end_date")
        upcoming_payments = get_upcoming_payments(rented_properties)
        return render(
            request,
            "includes/upcoming_payments.html",
            {"upcoming_payments": upcoming_payments},
        )


@login_required
def empty_property(request, pk):
    """
    This view empty a rented property.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the rented property to empty.

    Returns:
        HttpResponse: The list of all properties owned by the user.
    """
    rental = get_object_or_404(RentProperty, id=pk)
    property = rental.property
    tenant = rental.tenant
    contract_url = rental.contract.url if rental.contract else None

    property.is_rented = False
    property.save()

    RentHistory.objects.create(
        property=property,
        tenant=tenant,
        price=rental.price,
        damage_deposit=rental.damage_deposit,
        start_date=rental.start_date,
        payment_type=rental.get_payment_period(),
        end_date=(
            rental.end_date
            if rental.end_date == datetime.today().date()
            else datetime.today().date()
        ),
        contract=contract_url,
    )

    rental.delete()

    return redirect("view_property", pk=property.id)
