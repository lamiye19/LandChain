from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_label = "main"   

urlpatterns = [
    path('pdf/<int:number>/', views.req_file, name="pdf"),
    path('pdf/', views.invoice, name="pdf2"),

    path("acces-non-autorise", views.error403, name="error403"),
    path("ressource-introuvable/<message>", views.error404, name="error404"),

    path("tableau-de-bord", views.dashbord, name="dashbord"),
    path("profil", views.profile, name="profile"),
    path("clients", views.all_user, name="client"),
    path("agents-division-cadastre", views.all_guichet_user, name="guichet"),
    path("agents-bureau-de-bornage", views.all_bornage_user, name="b_bornage"),
    path("ordre-des-geometre", views.all_geometre_user, name="geometre"),
    path("agents-bureau-de-dessin", views.all_dessin_user, name="dessin"),
    path("agents-bureau-de-conservation", views.all_conservation_user, name="conservation"),
    path("changer-le-role", views.all_user, name="change_role"),

    path("register/", views.choose_register, name="register"),
    path("register/compte-particulier", views.person_register, name="person_register"),
    path("register/compte-entreprise", views.enterprise_register, name="enterprise_register"),
    path("login/", views.login_req, name="login"),
    path("logout/", views.logout_req, name="logout"),

    path("icons", views.icons, name="icons"),
    path("tables", views.tables, name="tables"),

    # Public
    path("", views.home, name="home"),
    path("journal-officiel", views.journal, name="journal"),
    path("travaux-de-bornage/", views.public_demarcations, name="bornage"),
    path("carte", views.carte, name="carte"),
    path("a-ventre", views.en_vente, name="en_vente"),

    # requisitions
    path("requisitions", views.requisitions, name="requisitions"),
    path("mes-requisitions", views.my_requisitions, name="my_requisitions"),
    path("requisitions/<int:number>/", views.single_requisition, name="single_requisition"),
    path("requisitions/<int:number>/facturation", views.payment, name="payment"),
    path("requisitions-response", views.state_requisition, name="state_requisition"),
    path("demander-une-requisition", views.add_requisition, name="add_requisition"),

    # plaintes
    path("plaintes", views.complaints, name="complaints"),
    path("mes-plaintes", views.my_complaints, name="my_complaints"),
    path("plaintes-response", views.state_complaint, name="state_complaint"),
    path("plaintes/<int:number>", views.add_complaint, name="add_complaint"),

    # Travaux de bornage
    path("travaux-de-bornage", views.demarcations, name="demarcations"),
    path("programmer-travaux-de-bornage", views.add_demarcation, name="add_demarcation"),

    # Rapport des ravaux de bornage
    path("rapports-travaux-de-bornage", views.reports, name="reports"),
    path("redaction-de-pv/<int:id>", views.add_report, name="add_report"),
    path("redaction-de-pv/<int:id>", views.reports, name="single_report"),
    path("redaction-de-pv/<int:number>/", views.single_requisition, name="add_plan"),


    # Titre foncier
    path("registre-foncier", views.deeds, name="deeds"),
    path("actifs-foncier", views.my_deeds, name="my_deeds"),
    path("registre-foncier/<int:number>", views.add_deed, name="add_deed"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'main.views.error404'
