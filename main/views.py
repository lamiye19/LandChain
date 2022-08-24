import contextlib
from urllib import response
from urllib.request import HTTPRedirectHandler, Request
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from email import message
from http.client import HTTPResponse
from pathlib import Path
from time import time
from django.conf import settings
from django.urls import reverse
from django.template import engines
from django.shortcuts import redirect, render
import requests
from dadc.settings import BASE_DIR
from main.pays import PAYS
from .choices import *
from main.models import Coordinate, Demarcation, Report, State, User, Complaint, Person, Requisition, landDeed
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from wkhtmltopdf.views import PDFTemplateResponse
from django.template.loader import render_to_string
from django.core.files import File
from django.db.models import Q


def error500(request):
    return render(request, 'home/page-500.html')

def error403(request):
    return render(request, 'home/page-403.html')

def error404(request, message):
    return render(request, 'home/page-404.html', status=404, context={"message": message})


def home(request):

    return render(request, "main/index.html", {"segment":'home'})

def icons(request):
    return render(request, "home/icons.html", {"segment": "icons"})

def tables(request):
    return render(request, "home/tables.html", {"segment": "tables"})



def register(data):
    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        last_name=data['last_name'],
        first_name=data['first_name'],
        id_document=data['id_document']
    )

    user.save()

    return user


def journal(request):
    context = {
        "requisitions": Requisition.objects.all()
    }
    return render(request, "public/journal.html", context)


def bornage(request):
    return render(request, "public/bornage.html")


def carte(request):
    return render(request, "public/carte.html")


def en_vente(request):
    return render(request, "public/en_vente.html")



"""
 USER ACCOUNT
"""
def f_login(request, username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return True
    else:
        return False

def login_req(request):
    context = {'question': True, 'segment': "home"}
    if request.method == "POST":
        if form := request.POST:
            username = form.get('username')
            password = form.get('password')
            if f_login(request, username, password):
                user = User.objects.get(username=username)
                with contextlib.suppress(ObjectDoesNotExist):
                    u = user.person
                    if u.type != 'CLIENT':
                        context['segment'] = "dashbord"
                        return redirect("dashbord")
                return redirect("home")
            else:
                context["error"] = "Nom d'utilisateur ou mot de passe invalide."

    return render(request, "auth/login.html", context)

def logout_req(request):
    logout(request)
    return redirect("home")

def dashbord(request):
    context= {
        "requisitions": Requisition.objects.all(),
        "complaints": Complaint.objects.all(),
        "users": User.objects.filter(Q(last_name= '') | Q(person__type = 'CLIENT')),
        "agents": Person.objects.filter(~Q(type = 'CLIENT')),
        "deeds": landDeed.objects.all(),
    }
    return render(request, "home/index.html", context)

def profile(request):
    context = {
        'segment': "profile"
    }

    return render(request, "auth/profile.html", context)

def choose_register(request):
    context = {'question': True}

    return render(request, "auth/register.html", context)


def person_register(request):
    context = {
        'person': True, 
        'segment': "home",
        'states': PAYS
        }
    if request.method == "POST":
        form = request.POST
        id_document = request.FILES['id_document']

        if id_document.name.split('.')[-1] != 'pdf':
            context['file'] = "Le fichier doit être en PDF."
            return render(request, "auth/register.html", context)

        data = {
            "username": form.get('username'),
            'email': form.get('email'),
            'password': form.get('password'),
            'first_name': form.get('first_name'),
            'last_name': form.get('last_name'),
            'id_document': id_document
        }

        find = User()
        try:
            find = User.objects.get(username=data['username'])
            context['username'] = "Cet nom d'utilisateur existe déjà."
        except find.DoesNotExist:
            if data['username'] == data['password']:
                context['password'] = "Le mot de passe ne doit pas être similaire au nom d'utilisateur."
            else:
                user = register(data)

                person = Person(
                    user=user,
                    gender=form.get('gender'),
                    partner_name=form.get('partner_name'),
                    profession=form.get('profession'),
                    birthday=form.get('birthday'),
                    bornAt=form.get('bornAt'),
                    address=form.get('address'),
                    residence=form.get('residence'),
                    nationality=form.get('nationality'),
                    marital_status=form.get('marital_status'),
                    phone=form.get('phone'),
                )
                person.save()

                if f_login(request, data['username'], data['password']):
                    return redirect("home")
                else:
                    context["error"] = "Nom d'utilisateur ou mot de passe invalide."

    return render(request, "auth/register.html", context)

def enterprise_register(request):
    context = {'enterprise': True, 'segment': "home"}
    if request.method == "POST":
        form = request.POST
        id_document = request.FILES['id_document']

        if id_document.name.split('.')[-1] != 'pdf':
            context['file'] = "Le fichier doit être en PDF."
            return render(request, "auth/register.html", context)

        data = {
            "username": form.get('username'),
            'email': form.get('email'),
            'password': form.get('password'),
            'first_name': form.get('first_name'),
            'last_name': "",
            'id_document': id_document
        }

        find = User()
        try:
            find = User.objects.get(username=data['username'])
            context['username'] = "Cet nom d'utilisateur existe déjà."
        except find.DoesNotExist:
            if data['username'] == data['password']:
                context['password'] = "Le mot de passe ne doit pas être similaire au nom d'utilisateur."
            else:
                user = register(data)

                if f_login(request, data['username'], data['password']):
                    return redirect("home")
                else:
                    context["error"] = "Nom d'utilisateur ou mot de passe invalide."

    return render(request, "auth/register.html", context)

def all_user(request):
    users = User.objects.filter(Q(last_name= '') | Q(person__type = 'CLIENT'))
    context = {
        'users': users,
        'segment': 'CLIENT',
        'types': ROLE
    }
    if request.method == "POST":
        user = User.objects.get(username = request.POST.get('username'))
        user.person.type = request.POST.get('type')
        user.person.save()
        print(request.POST.get('type'))
        print(user.person.type)
        context['message'] = "L'utilisateur a été modifié."
        return redirect('client')
    return render(request, 'accounts/all_user.html', context)

def all_guichet_user(request):
    users = User.objects.filter(person__type='GUICHET')
    context = {
        'users': users,
        'segment': 'GUICHET',
        'types': ROLE
    }
    
    return render(request, 'accounts/all_user.html', context)
     
def all_bornage_user(request):
    users = User.objects.filter(person__type='BORNAGE')
    context = {
        'users': users,
        'segment': 'BORNAGE',
        'types': ROLE
    }
    
    return render(request, 'accounts/all_user.html', context)
     
def all_geometre_user(request):
    users = User.objects.filter(person__type='GEOMETRE')
    context = {
        'users': users,
        'segment': 'GEOMETRE',
        'types': ROLE
    }
    
    return render(request, 'accounts/all_user.html', context)
     

def all_dessin_user(request):
    users = User.objects.filter(person__type='DESSIN')
    context = {
        'users': users,
        'segment': 'DESSIN',
        'types': ROLE
    }
    
    return render(request, 'accounts/all_user.html', context)

def all_conservation_user(request):
    users = User.objects.filter(person__type='CONSERVATION')
    context = {
        'users': users,
        'segment': 'CONSERVATION',
        'types': ROLE
    }
    
    return render(request, 'accounts/all_user.html', context)
     



"""
 REQUISITION
"""
@login_required()
def requisitions(request):
    user = User.objects.get(username=request.user)
    requisitions = []
    try:
        u = user.person
        requisitions = Requisition.objects.all()
        if u.type == 'CLIENT':
            return redirect('error403')
        if u.type == 'GEOMETRE':
            requisitions = Requisition.objects.filter(demarcation__surveyor = user)
        if u.type == 'DESSIN':
            requisitions = Requisition.objects.filter(demarcation__drawer = user)
        if u.type == 'CONSERVATION':
            requisitions = Requisition.objects.filter(landdeed__author = user)
    except ObjectDoesNotExist:
        return redirect('error403')

    context = {
        "requisitions": requisitions,
        "segment": "requisitions",
        "template": 'layouts/base.html'
    }
    return render(request, "requisition/read.html", context)

@login_required()
def my_requisitions(request):
    requisitions = Requisition.objects.filter(author__username = request.user)
    context = {
        "requisitions": requisitions,
        "segment": "my_requisitions",
        "template": 'main/base.html'
    }
    return render(request, "requisition/read.html", context)

@login_required()
def add_requisition(request):
    context = {}

    if request.method == "POST":
        form = request.POST
        files = request.FILES

        land_receipt=request.FILES['land_receipt'],
        floor_plan=request.FILES['floor_plan'],
        notarial_instrument=request.FILES['notarial_instrument']

        if request.FILES['land_receipt'].name.split('.')[-1] != 'pdf' or request.FILES['floor_plan'].name.split('.')[-1] != 'pdf' or request.FILES['notarial_instrument'].name.split('.')[-1] != 'pdf':
            context['file'] = "Les fichiers doivent être en PDF."
            return render(request, "requisition/add.html", context)

        requisition = Requisition.objects.create(
            number=time(),
            # Property info
            area_a=form.get('area_a'),
            area_ca=form.get('area_ca'),
            quality=form.get('quality'),
            type=form.get('type'),
            info=form.get('info'),
            quarter=form.get('quarter'),
            real_name=form.get('real_name'),
            prefecture=form.get('prefecture'),

            east=form.get('east'),
            western=form.get('western'),
            north=form.get('north'),
            south=form.get('south'),
            author=User.objects.get(username=request.user),
            # Files and payment
            land_receipt=files['land_receipt'],
            floor_plan=files['floor_plan'],
            notarial_instrument=files['notarial_instrument'],
        )
        requisition.save()

        

        req_file(request, requisition.number)
    

        context['message'] = 'Réquisition bien envoyée. Vous aurez une réponse dans les 48 heures.'

        return redirect('single_requisition', number=int(requisition.number))


    return render(request=request, template_name="requisition/add.html", context=context)

@login_required()
def payment(request, number):
    # sourcery skip: inline-immediately-returned-variable, remove-unreachable-code
    context = {}
    try:
        requisition = Requisition.objects.get(number=number)
        context["requisition"] = requisition
        url = "https://mysterious-forest-88850.herokuapp.com//api/v1/predict/"
        area = (requisition.area_a *100) + requisition.area_ca,
        PARAMS = {
            "type_property": "terrain",
            "type_zone": "rural",
            "quartier": "adidogome",
            "have_closure": 0,
            "dist_road": 720,
            "area": area
        }
        vv = requests.get(url, PARAMS)
        if vv.status_code == 200:
            context["vv"] = vv.json()['Valeur vénale']
            context["register"] = context["vv"] * 0.05
            context["taxe"] = context["vv"] * 0.01
            context["safe"] = context["vv"] * 0.02
            context["fixed"] = 1000
            context["jort"] = 10000
            context["deposit"] = 2000
            if request.method == "POST":
                form = request.POST
                requisition.pay = int(time())
                requisition.pay_date = datetime.now()
                requisition.save()

                invoice(request, requisition, context)

                return redirect('single_requisition', number=int(requisition.number))
        else:
            return redirect('error500')

    except ObjectDoesNotExist:
        context["error"] = "Cette réquisition n'existe pas."

    return render(request, "requisition/payment2.html", context)


@login_required()
def state_requisition(request):
    if request.method == "POST":
        form = request.POST
        requisition = Requisition.objects.get(number=form.get('number'))
        state = State.objects.create(requisition=requisition, state=form.get('state'))
    return redirect('requisitions')

def single_requisition(request, number):
    context = {
        'template': 'layouts/base.html' , 
        "Auth": True
    }
    try:
        requisition = Requisition.objects.get(number=number)
        if request.user.is_authenticated:
            try:
                u = request.user.person
                requisitions = Requisition.objects.all()
                
                if u.type == 'CLIENT':
                    context['template'] = 'main/base.html'
                    if requisition.author != request.user:
                        context['Auth'] = False
                elif u.type == 'BORNAGE':
                    if not requisition.demarcation_set.all():
                        surveyors = Person.objects.filter(type='GEOMETRE')
                        drawers = Person.objects.filter(type='DESSIN')
                        context["surveyors"] = surveyors
                        context["drawers"] = drawers
                
                context["requisition"] = requisition
                if request.method == "POST":
                    if request.FILES['floor_plan'].name.split('.')[-1] != 'pdf':
                        context['file'] = "Le fichier doit être en PDF."
                    else:
                        add_plan(request, request.POST.get('id'), request.FILES['floor_plan'])

            except ObjectDoesNotExist:
                context['template'] = 'main/base.html'
                if requisition.author != request.user:
                    context['Auth'] = False
        else:
            context['template'] = 'main/base.html'
            if requisition.author.username != request.user:
                context['Auth'] = False

        
    except ObjectDoesNotExist:
        message = "Cette réquisition n'existe pas."
        return redirect(reverse('error404', 
                            kwargs={'message': message}))
    

    return render(request, "requisition/single.html", context)

""" 
 COMPLANT
"""

@login_required()
def complaints(request):
    user = User.objects.get(username=request.user)
    complaints = Complaint.objects.all()
    try:
        u = user.person
        if u.type == 'CLIENT':
            return redirect('error403')
        if u.type == 'GEOMETRE':
            complaints = Complaint.objects.filter(requisition__demarcation__surveyor = user)
        if u.type == 'DESSIN':
            complaints = Complaint.objects.filter(requisition__demarcation__drawer = user)
        if u.type == 'CONSERVATION':
            complaints = Complaint.objects.filter(requisition__landDeed__generated_by = user)
    except ObjectDoesNotExist:
        return redirect('error403')
    context = {
        "complaints": complaints,
        "segment": "complaints",
        "template": 'layouts/base.html'
    }
    return render(request, "complaint/read.html", context)

@login_required()
def my_complaints(request):
    complaints = Complaint.objects.filter(author__username = request.user)
    context = {
        "complaints": complaints,
        "segment": "my_complaints",
        "template": 'main/base.html'
    }
    return render(request, "complaint/read.html", context)


@login_required()
def add_complaint(request, number):
    context = {
        "number": number
    }
    try:
        requisition = Requisition.objects.get(number=number)
        if requisition.author.username == request.user:
            return redirect('error403')

        elif request.method == "POST":
            form = request.POST
            proof_file = request.FILES['proof_file']

            if request.FILES['proof_file'].name.split('.')[-1] != 'pdf':
                context['file'] = "Le fichier doit être en PDF."
            else:
                author = User.objects.get(username=request.user)
                complaint = Complaint.objects.create(
                    id = int(time()),
                    object=form.get('object'),
                    message=form.get('message'),
                    proof_file=proof_file,
                    author = author,
                    requisition = requisition
                )
                complaint.save()

                texte = f'Plainte {complaint.id}'

                state = State.objects.create(requisition=requisition, state='P', raison = texte, author=author)

                context["requisition"] = requisition
                context['message'] = 'Plainte bien envoyé. Vous aurez une réponse dans les 48 heures.'

                return redirect('my_complaints')
    except ObjectDoesNotExist:
        context["error"] = "Cette réquisition n'existe pas."

    return render(request=request, template_name="complaint/add.html", context=context)


@login_required()
def state_complaint(request):
    try: 
        complaint = Complaint.objects.get(pk=form.get('id'))
        if complaint.author.username == request.user:
            return redirect('error403')

        elif request.method == "POST":
                form = request.POST
                author = User.objects.get(username=request.user)

                complaint.state = int(form.get('state'))
                complaint.state_date = datetime.now()
                complaint.state_author = author
                complaint.save()

                requisition = Requisition.objects.get(number=complaint.requisition.number)

                c = requisition.complaint_set.all()
                print(complaint)

                if complaint.state:
                    texte = f'Prise en compte de la plainte {complaint.id}'
                    print(texte)
                    state = State.objects.create(requisition=requisition, state='C', raison = texte, author=author)
                elif not c.filter(state=None):
                    texte = f'Rejet de la plainte {complaint.id}'
                    state = State.objects.create(requisition=requisition, state='A', raison = texte, author=author)
    except ObjectDoesNotExist:
        message = "Cette plainte n'existe pas"
        return redirect((reverse('error404', 
                            kwargs={'message': message})))
        #return redirect(request.META['HTTP_REFERER'])
        
    return redirect(request.META['HTTP_REFERER'])

""" 
 DEMARCATION
"""""
@login_required()
def demarcations(request):
    user = User.objects.get(username=request.user)
    try:
        u = user.person
        if u.type == 'GEOMETRE':
            demarcations = Demarcation.objects.filter(surveyor = user)
        elif u.type == 'DESSIN':
            demarcations = Demarcation.objects.filter(drawer = user)
        elif u.type == 'CONSERVATION':
            demarcations = Demarcation.objects.filter(author = user)
        elif u.type == 'GUICHET':
            demarcations = Complaint.objects.all()
        else:
            return redirect('error403')
    except ObjectDoesNotExist:
        return redirect('error403')
    context = {
        "demarcations": demarcations,
        "segment": "demarcations",
        "template": 'layouts/base.html'
    }
    return render(request, "demarcation/read.html", context)

def public_demarcations(request):
    context = {
        "demarcations": Demarcation.objects.all(),
        "segment": "bornage",
        "template": 'main/base.html'
    }
    return render(request, "demarcation/read.html", context)


@login_required()
def add_demarcation(request):
    if request.method == "POST":
        form = request.POST
        context = {}

        try:
            requisition = Requisition.objects.get(number=form.get('number'))
            author = User.objects.get(username=request.user)
            surveyor = User.objects.get(username=form.get('surveyor'))
            drawer = User.objects.get(username=form.get('drawer'))

            choosed_date = form.get('date')+ ' '+ form.get('heure')
            demarcation = Demarcation.objects.create(
                choosed_date = choosed_date,
                author = author,
                drawer = drawer,
                surveyor = surveyor,
                requisition = requisition
            )
            demarcation.save()

            texte = 'Travaux de bornage programmés'

            state = State.objects.create(requisition=requisition, state='A', raison = texte, author=author)

            context["requisition"] = requisition

            return redirect('single_requisition', number=int(requisition.number))

        except ObjectDoesNotExist:
            message = "Cette réquisition n'existe pas."
            return redirect((reverse('error404', 
                            kwargs={'message': message})))


""" 
 REPORT
"""""
@login_required()
def reports(request):
    context = {
        "reports": Report.objects.all(),
        "segment": "reports"
    }
    return render(request, "report/read.html", context)

@login_required()
def add_report(request, id):
    try:
        demarcation = Demarcation.objects.get(pk=id)
        if demarcation.surveyor != request.user:
            return redirect('error403')   
        context = {
            "id": id,
            "segment": "reports"
        }
        if request.method == "POST":
            form = request.POST
            report = Report.objects.create(
                pv = form.get('pv'),
                demarcation = demarcation
            )
            report.save() 

            for i in range(1,7):
                x,y = form.get(f'x{i}') , form.get(f'x{i}')
                if x != '' and y != '' :
                    #x,y = float(x), float(y)
                    coordinate = Coordinate.objects.create(
                        x = x,
                        y = y,
                        report = report
                    )
            return redirect('reports')

    except ObjectDoesNotExist:
        message = "La programmation des travaux de bornage demandée n'existe pas"
        return redirect((reverse('error404', 
                            kwargs={'message': message})))
    return render(request, "report/add.html", context)

@login_required()
def add_plan(username, report_id, file):
    report = Report.objects.get(pk=report_id)
    report.floor_plan = file
    report.save()

    requisition = report.demarcation.requisition
    author = User.objects.get(username=username)

    texte = 'Rapport de bornage soummis'
    State.objects.create(requisition=requisition, state='A', raison = texte, author=author)
    
 
""" 
 LAND DEEDS
"""

@login_required()
def deeds(request):
    context = {
        "deeds": landDeed.objects.all(),
        "segment": "deeds"
    }
    return render(request, "deed/read.html", context)

@login_required()
def my_deeds(request):
    deeds = landDeed.objects.filter(requisition__author__username = request.user)
    context = {
        "deeds": deeds,
        "segment": "my_deeds"
    }
    return render(request, "deed/read.html", context)


@login_required()
def add_deed(request, number):
    if request.method == "POST":
        context = {}
        try:
            requisition = Requisition.objects.get(number=number)
            author = User.objects.get(username=request.user)
            landDeed.objects.create(
                number = int(time()),
                author = author,
                requisition = requisition
            )

            texte = 'Titre foncier disponible'

            State.objects.create(requisition=requisition, state='T', raison = texte, author=author)

        except ObjectDoesNotExist:
            context["error"] = "Cette réquisition n'existe pas."


        return redirect('single_requisition', number=number)

   

""" 
 PDF
"""
def invoice(request, requisition, context):
    str_template= render_to_string("requisition/payment.html", context)
    response = PDFTemplateResponse(
        request,
        engines['django'].from_string(str_template),
        context=context,
        show_content_in_browser=True
    )
    fPath = f"{BASE_DIR}/media/invoices/facture-req{requisition.number}.pdf"    
    with open(fPath, "wb") as f:
        f.write(response.rendered_content)

    path = Path(fPath)
    with path.open(mode='rb') as f:
        requisition.liquidation_receipt = File(f, name=path.name)
        requisition.save()

def req_file(request, number):
    requisition = Requisition.objects.get(number=number)
    str_template= render_to_string("requisition/fiche.html", {"requisition":requisition})
    response = PDFTemplateResponse(
        request,
        engines['django'].from_string(str_template),
        show_content_in_browser=True
    )
    fPath = f"{BASE_DIR}/media/files/fiche-req{requisition.number}.pdf"    
    with open(fPath, "wb") as f:
        f.write(response.rendered_content)

    path = Path(fPath)
    with path.open(mode='rb') as f:
        requisition.file = File(f, name=path.name)
        requisition.save()
    return response


def fb_page(request, number):
    page_id = 104081802431797
    access_token = "EAANtdsp8wU0BAMKntZArnktxlp9rUPKUtZAKMwZAqM51c23fC9DgfLkeLUJOZAvfW65RPqMuno12ZBt0pq1UsDzSQVfIT9VpZCJcs3sC00BahWneNSZBLLZC1hJ6whLa1eppbvwXKL4ZBvsCsrpfVla60oMXR4dDV5qcvG0ZBZCBbQaUZB5iTEYNyXaZC"
    link = f"localhost:8000/requisitions/{number}"
    message = "Une nouvelle demande d'immatriculation est en cours d'étude. Cliquez que le lien pour en savoir plus"

    url = f"https://graph.facebook.com/{page_id}/feed"

    PARAMS = {
        "message": message,
        "link": link,
        "access_token": access_token
    }

    response = requests.get(url, PARAMS)

    if response.status_code != 200:
        print(response.json())
        return redirect("journal")
    return redirect("home")
