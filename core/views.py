from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Property
from django.shortcuts import get_object_or_404
from .forms import PropertyForm, RentPropertyForm
# from django.utils.translation import gettext as _


def landing(request):
    """
    """
    return render(request, "core/landing.html")


@login_required
def home(request):
    """
    """
    available_properties = Property.objects.filter(user=request.user ,is_rented=False)
    rented_properties = Property.objects.filter(user=request.user ,is_rented=True)
    context = {"available_properties": available_properties, "rented_properties": rented_properties}

    return render(request, "core/home.html", context)


@login_required
def add_property(request):
    """
    """
    if request.method == "POST":
        try:
            form = PropertyForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                instance.save()
                return redirect("all_properties")
        except Exception as e:
            form.add_error(None, str(e))
    else:
        form = PropertyForm()

    return render(request, "forms/add_property_form.html", {"form": form})


@login_required
def rent_property(request, pk):
    """
    """
    property_instance = get_object_or_404(Property, id=pk)

    if request.method == "POST":
        form = RentPropertyForm(request.POST)
        try:
            if form.is_valid():
                phone_number = form.cleaned_data.get("t_phone_number")
                if phone_number and phone_number.startswith("+"):
                    instance = form.save(commit=False)
                    instance.property = property_instance
                    property_instance.is_rented = True
                    property_instance.owner = request.user
                    property_instance.save()
                    instance.save()
                    return redirect("home")
                else:
                    form.add_error(
                        "t_phone_number", "Phone number must start with '+'."
                    )
        except Exception as e:
            form.add_error(None, str(e))
    else:
        form = RentPropertyForm()

    return render(request, "core/add_tenant.html", {"form": form})


def all_properties(request):
    """
    """
    my_properties = Property.objects.filter(user=request.user)
    context = {"all_properties": my_properties}
    return render(request, 'includes/all_properties.html', context)

def delete_property(request, pk):
    """
    """
    instance = get_object_or_404(Property, id=pk)
    instance.delete()

    all_properties = Property.objects.filter(user=request.user)
    return render(request, "includes/all_properties.html", {"all_properties": all_properties})

def edit_property(request, pk):
    instance = get_object_or_404(Property, id=pk)
    if request.method == "POST":
        form = PropertyForm(request.POST ,instance=instance)
        if form.is_valid():
            try:
                form.save()
                return redirect("all_properties")
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = PropertyForm(instance=instance)

    return render(request, "forms/edit_property_form.html", {"form": form, "property": instance})