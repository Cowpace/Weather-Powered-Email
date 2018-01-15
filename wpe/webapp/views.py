from django.shortcuts import render

# Create your views here.
from .forms import MainForm
from .models import EmailSignupModel


def index(request):
    if request.method == 'POST':
        form = MainForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            location_index = int(form.cleaned_data['location'])
            location = dict(form.fields['location'].choices)[location_index]

            city, state = location.split(',')
            city = city.strip().title()
            state = state.strip().upper()

            model = EmailSignupModel(email=email, city=city, state=state)
            if not EmailSignupModel.objects.filter(email=email):
                model.save()
    else:
        form = MainForm()
    print(EmailSignupModel.objects.all())
    return render(request, 'base.html', {'form': form})
