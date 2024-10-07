from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Property, Tenant, RentProperty, RentHistory
from django.shortcuts import get_object_or_404
from .forms import PropertyForm, RentPropertyForm
from django.http import HttpResponse
from django.utils.translation import gettext as _
from .utils import *
from datetime import datetime


def landing(request):
    """ """
    return render(request, "core/landing.html")


@login_required
def home(request):
    """ """
    available_properties = Property.objects.filter(
        user=request.user, is_rented=False
    ).order_by("created_at")

    rented_properties = Property.objects.filter(
        user=request.user, is_rented=True
    ).order_by("property_rentals__end_date")

    expiring_contracts = get_expiring_contracts(rented_properties)
    upcoming_payments = get_upcoming_payments(rented_properties)

    context = {
        "available_properties": available_properties,
        "rented_properties": rented_properties,
        "expiring_contracts": expiring_contracts,
        "upcoming_payments": upcoming_payments,
    }

    return render(request, "core/home.html", context)


@login_required
def add_property(request):
    """ """
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


def rent_property(request, pk):
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


def edit_rental(request, pk):
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


def all_properties(request):
    """ """
    my_properties = Property.objects.filter(user=request.user)
    context = {"all_properties": my_properties}
    return render(request, "includes/all_properties.html", context)


def delete_property(request, pk):
    """ """
    instance = get_object_or_404(Property, id=pk)
    instance.delete()

    all_properties = Property.objects.filter(user=request.user)
    return render(
        request, "includes/all_properties.html", {"all_properties": all_properties}
    )


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


def view_property(request, pk):
    property = get_object_or_404(Property, id=pk)
    rental_histories = RentHistory.objects.filter(property_id=pk)

    context = {}
    if property.is_rented:
        instance = get_object_or_404(RentProperty, property=property)
        context["rent_property"] = instance
    context["property"] = property
    context["rental_histories"] = rental_histories

    return render(request, "includes/view_property.html", context)


def mark_as_paid(request, pk):
    instance = get_object_or_404(RentProperty, id=pk)

    if instance.paid:
        instance.paid = False
        instance.save()
        return HttpResponse(
            f'<a class="btn btn-danger btn-sm rounded-4 px-2 m-0 py-0" data-bs-toggle="modal" data-bs-target="#confirmPaymentModal{instance.property.id }">Unpaid</a>'
        )
    else:
        instance.paid = True
        instance.save()
        return HttpResponse(
            f'<a class="property-button btn btn-sm rounded-4 px-2 m-0 py-0" data-bs-toggle="modal" data-bs-target="#confirmPaymentModal{instance.property.id }">Paid</a>'
        )


def empty_property(request, pk):
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
