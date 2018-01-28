from django.shortcuts import render

# Create your views here.
from .forms import MainForm
from .models import EmailSignupModel


def index(request):
    exists = False
    success = False
    if request.method == 'POST':
        form = MainForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            location_index = int(form.cleaned_data['location'])
            # get the city and state from what index the user chose in the dropdown
            location = dict(form.fields['location'].choices)[location_index]

            city, state = location.split(',')
            city = city.strip().title()
            state = state.strip().upper()

            model = EmailSignupModel(email=email, city=city, state=state)
            if not EmailSignupModel.objects.filter(email=email):
                model.save()
                success = True
                form = MainForm()
            else:
                exists = True
    else:
        form = MainForm()

    return render(
        request,
        'base.html',
        {
            'form': form,
            'exists': exists,
            'success': success
        }
    )
