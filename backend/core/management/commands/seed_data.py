from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from sales_app.models import Offer, OfferDetail, Order, Review
from user_auth_app.models import UserProfile


DEMO_PASSWORD = "Demo1234!"

BUSINESS_USERS = [
    {
        "username": "maxdev",
        "email": "max.weber@demo.de",
        "first_name": "Max",
        "last_name": "Weber",
        "location": "Berlin",
        "tel": "+49 30 12345678",
        "description": "Erfahrener Fullstack-Entwickler mit 8+ Jahren Erfahrung in Python, Django und React. Spezialisiert auf skalierbare Webanwendungen und APIs.",
        "working_hours": "Mo-Fr 9:00 - 18:00",
    },
    {
        "username": "sarah.designs",
        "email": "sarah.mueller@demo.de",
        "first_name": "Sarah",
        "last_name": "Müller",
        "location": "München",
        "tel": "+49 89 98765432",
        "description": "UI/UX Designerin und Frontend-Entwicklerin. Ich gestalte nutzerzentrierte Interfaces mit modernem Design und sauberer Code-Basis. Figma, Adobe XD, HTML/CSS/JS.",
        "working_hours": "Mo-Fr 10:00 - 17:00",
    },
    {
        "username": "devops.felix",
        "email": "felix.schmidt@demo.de",
        "first_name": "Felix",
        "last_name": "Schmidt",
        "location": "Hamburg",
        "tel": "+49 40 55566677",
        "description": "DevOps Engineer & Cloud-Architekt. AWS, Docker, Kubernetes, CI/CD Pipelines. Ich bringe dein Projekt sicher und performant in die Cloud.",
        "working_hours": "Mo-Fr 8:00 - 16:00",
    },
    {
        "username": "anna.backend",
        "email": "anna.koch@demo.de",
        "first_name": "Anna",
        "last_name": "Koch",
        "location": "Köln",
        "tel": "+49 221 4445556",
        "description": "Backend-Entwicklerin mit Schwerpunkt auf Django, Flask und PostgreSQL. Erfahrung in der Entwicklung von REST-APIs, Datenbank-Design und Automatisierung.",
        "working_hours": "Mo-Do 9:00 - 17:30",
    },
    {
        "username": "tom.mobile",
        "email": "tom.richter@demo.de",
        "first_name": "Tom",
        "last_name": "Richter",
        "location": "Frankfurt",
        "tel": "+49 69 7778889",
        "description": "Mobile App-Entwickler für iOS und Android. React Native, Flutter und Swift. Von der Konzeption bis zum App Store Release — alles aus einer Hand.",
        "working_hours": "Mo-Fr 9:00 - 18:00",
    },
    {
        "username": "julia.data",
        "email": "julia.bauer@demo.de",
        "first_name": "Julia",
        "last_name": "Bauer",
        "location": "Stuttgart",
        "tel": "+49 711 3334445",
        "description": "Data Scientist & Machine Learning Ingenieurin. Python, TensorFlow, Pandas. Ich verwandle deine Daten in wertvolle Erkenntnisse und intelligente Modelle.",
        "working_hours": "Mo-Fr 10:00 - 18:00",
    },
]

CUSTOMER_USERS = [
    {
        "username": "petra.startup",
        "email": "petra.wagner@demo.de",
        "first_name": "Petra",
        "last_name": "Wagner",
        "location": "Düsseldorf",
        "description": "Startup-Gründerin im E-Commerce Bereich. Suche regelmäßig Freelancer für Web-Projekte.",
    },
    {
        "username": "markus.agentur",
        "email": "markus.hoffmann@demo.de",
        "first_name": "Markus",
        "last_name": "Hoffmann",
        "location": "Leipzig",
        "description": "Projektmanager bei einer Digitalagentur. Immer auf der Suche nach talentierten Entwicklern.",
    },
    {
        "username": "lena.freelance",
        "email": "lena.frank@demo.de",
        "first_name": "Lena",
        "last_name": "Frank",
        "location": "Nürnberg",
        "description": "Marketing-Beraterin und Freelancerin. Brauche regelmäßig Unterstützung bei technischen Umsetzungen.",
    },
    {
        "username": "david.tech",
        "email": "david.klein@demo.de",
        "first_name": "David",
        "last_name": "Klein",
        "location": "Dortmund",
        "description": "CTO eines mittelständischen Unternehmens. Outsource gezielt Spezialprojekte an erfahrene Freelancer.",
    },
    {
        "username": "nina.design",
        "email": "nina.schaefer@demo.de",
        "first_name": "Nina",
        "last_name": "Schäfer",
        "location": "Bremen",
        "description": "Inhaberin einer kleinen Designagentur. Suche Entwickler für die technische Umsetzung meiner Designs.",
    },
]


OFFERS = [
    # maxdev
    {
        "business": "maxdev",
        "title": "Professionelle Django REST API Entwicklung",
        "description": "Ich entwickle für dich eine maßgeschneiderte REST API mit Django und Django REST Framework. Inklusive Authentifizierung, Datenbankmodellierung, Tests und Dokumentation. Perfekt für Startups und Unternehmen, die eine solide Backend-Lösung brauchen.",
        "details": [
            {"title": "Starter API", "offer_type": "basic", "revisions": 2, "delivery_time_in_days": 7, "price": "299.00", "features": ["Bis zu 5 Endpunkte", "Token-Authentifizierung", "SQLite-Datenbank", "Grundlegende Tests"]},
            {"title": "Business API", "offer_type": "standard", "revisions": 3, "delivery_time_in_days": 14, "price": "799.00", "features": ["Bis zu 15 Endpunkte", "Token-Authentifizierung", "PostgreSQL-Datenbank", "Umfassende Tests", "API-Dokumentation", "Filterung & Paginierung"]},
            {"title": "Enterprise API", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 28, "price": "1999.00", "features": ["Unbegrenzte Endpunkte", "OAuth2 + Token Auth", "PostgreSQL + Redis", "95%+ Test-Coverage", "Swagger-Dokumentation", "CI/CD Pipeline", "Performance-Optimierung"]},
        ],
    },
    {
        "business": "maxdev",
        "title": "React Frontend-Entwicklung",
        "description": "Moderne React-Anwendungen mit TypeScript, State Management und responsivem Design. Von der Landing Page bis zur komplexen Web-App — professionell, performant und wartbar.",
        "details": [
            {"title": "Single Page", "offer_type": "basic", "revisions": 2, "delivery_time_in_days": 5, "price": "449.00", "features": ["1 Seite / Komponente", "Responsives Design", "Basis-Styling"]},
            {"title": "Multi-Page App", "offer_type": "standard", "revisions": 3, "delivery_time_in_days": 10, "price": "1199.00", "features": ["Bis zu 5 Seiten", "React Router", "State Management", "API-Anbindung", "Responsives Design"]},
            {"title": "Komplette Web-App", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 21, "price": "2999.00", "features": ["Unbegrenzte Seiten", "TypeScript", "Redux/Zustand", "API-Integration", "Unit Tests", "CI/CD", "Performance-Audit"]},
        ],
    },
    # sarah.designs
    {
        "business": "sarah.designs",
        "title": "UI/UX Design für Web-Anwendungen",
        "description": "Professionelles UI/UX Design für deine Web-Anwendung. Ich erstelle nutzerzentrierte Designs in Figma, inklusive Wireframes, Prototypen und einem vollständigen Design System.",
        "details": [
            {"title": "Wireframes", "offer_type": "basic", "revisions": 2, "delivery_time_in_days": 3, "price": "199.00", "features": ["Bis zu 5 Screens", "Low-Fidelity Wireframes", "Nutzerfluss-Diagramm"]},
            {"title": "UI Design", "offer_type": "standard", "revisions": 3, "delivery_time_in_days": 7, "price": "599.00", "features": ["Bis zu 10 Screens", "High-Fidelity Mockups", "Interaktiver Prototyp", "Farbpalette & Typografie", "Responsive Varianten"]},
            {"title": "Design System", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 14, "price": "1499.00", "features": ["Unbegrenzte Screens", "Vollständiges Design System", "Interaktiver Prototyp", "Komponentenbibliothek", "Styleguide-Dokumentation", "Handoff-Dateien"]},
        ],
    },
    {
        "business": "sarah.designs",
        "title": "Responsive HTML/CSS Umsetzung aus Figma",
        "description": "Pixelgenaue Umsetzung deines Figma-Designs in sauberes, semantisches HTML und CSS. Mobile-First, Cross-Browser-kompatibel und performant.",
        "details": [
            {"title": "Landing Page", "offer_type": "basic", "revisions": 1, "delivery_time_in_days": 3, "price": "179.00", "features": ["1 Seite", "Responsiv", "Semantisches HTML", "Cross-Browser"]},
            {"title": "Website", "offer_type": "standard", "revisions": 2, "delivery_time_in_days": 7, "price": "499.00", "features": ["Bis zu 5 Seiten", "Responsiv", "CSS Animationen", "Kontaktformular", "SEO-Grundlagen"]},
            {"title": "Komplette Umsetzung", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 14, "price": "999.00", "features": ["Unbegrenzte Seiten", "CSS Grid & Flexbox", "Animationen", "JavaScript-Interaktionen", "Performance-Optimierung", "Barrierefreiheit"]},
        ],
    },
    # devops.felix
    {
        "business": "devops.felix",
        "title": "Cloud-Infrastruktur & DevOps Setup",
        "description": "Professionelles Cloud-Setup für dein Projekt. AWS, Docker, Kubernetes — ich richte deine Infrastruktur ein, automatisiere Deployments und sorge für Skalierbarkeit und Sicherheit.",
        "details": [
            {"title": "Basis Setup", "offer_type": "basic", "revisions": 1, "delivery_time_in_days": 3, "price": "349.00", "features": ["Docker-Containerisierung", "Einfaches Deployment", "Grundlegendes Monitoring"]},
            {"title": "Profi Setup", "offer_type": "standard", "revisions": 2, "delivery_time_in_days": 7, "price": "899.00", "features": ["Docker + Docker Compose", "CI/CD Pipeline (GitHub Actions)", "AWS/Render Deployment", "SSL-Zertifikate", "Logging & Monitoring"]},
            {"title": "Enterprise Infrastructure", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 21, "price": "2499.00", "features": ["Kubernetes-Cluster", "Multi-Stage CI/CD", "Auto-Scaling", "Load Balancing", "Disaster Recovery", "24/7 Monitoring", "Sicherheits-Audit"]},
        ],
    },
    # anna.backend
    {
        "business": "anna.backend",
        "title": "Datenbank-Design & Optimierung",
        "description": "Professionelles Datenbankdesign und Optimierung für PostgreSQL und MySQL. Von der Modellierung bis zur Query-Optimierung — ich sorge dafür, dass deine Daten effizient und sicher gespeichert werden.",
        "details": [
            {"title": "Schema-Review", "offer_type": "basic", "revisions": 1, "delivery_time_in_days": 2, "price": "149.00", "features": ["Analyse bestehender Datenbank", "Optimierungsvorschläge", "Schriftlicher Report"]},
            {"title": "DB-Design", "offer_type": "standard", "revisions": 2, "delivery_time_in_days": 5, "price": "499.00", "features": ["Neues Schema-Design", "Migrations-Skripte", "Index-Optimierung", "Dokumentation"]},
            {"title": "Komplett-Paket", "offer_type": "premium", "revisions": 3, "delivery_time_in_days": 10, "price": "999.00", "features": ["Schema-Design", "Daten-Migration", "Performance-Tuning", "Backup-Strategie", "Monitoring-Setup", "Ongoing Support (1 Monat)"]},
        ],
    },
    {
        "business": "anna.backend",
        "title": "Python-Automatisierung & Scripting",
        "description": "Individuelle Python-Skripte und Automatisierungslösungen. Web Scraping, Datenverarbeitung, API-Integrationen und wiederkehrende Aufgaben automatisieren.",
        "details": [
            {"title": "Einfaches Skript", "offer_type": "basic", "revisions": 1, "delivery_time_in_days": 2, "price": "99.00", "features": ["1 Python-Skript", "Grundlegende Dokumentation", "1 Revision"]},
            {"title": "Automatisierung", "offer_type": "standard", "revisions": 2, "delivery_time_in_days": 5, "price": "349.00", "features": ["Mehrere Skripte", "Error Handling", "Logging", "Scheduling", "Dokumentation"]},
            {"title": "Komplett-Lösung", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 10, "price": "799.00", "features": ["Komplexe Automatisierung", "API-Integrationen", "Dashboard", "Tests", "Docker-Deployment", "Monitoring"]},
        ],
    },
    # tom.mobile
    {
        "business": "tom.mobile",
        "title": "React Native App-Entwicklung",
        "description": "Cross-Platform Mobile Apps mit React Native. Eine Codebasis für iOS und Android. Modern, performant und sofort einsatzbereit im App Store.",
        "details": [
            {"title": "MVP App", "offer_type": "basic", "revisions": 2, "delivery_time_in_days": 14, "price": "1499.00", "features": ["Bis zu 5 Screens", "Navigation", "Basis-UI", "1 API-Anbindung"]},
            {"title": "Standard App", "offer_type": "standard", "revisions": 3, "delivery_time_in_days": 28, "price": "3499.00", "features": ["Bis zu 12 Screens", "Push-Benachrichtigungen", "Authentifizierung", "Offline-Modus", "API-Integration"]},
            {"title": "Premium App", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 42, "price": "6999.00", "features": ["Unbegrenzte Screens", "In-App Käufe", "Analytics", "App Store Submission", "6 Monate Support", "Performance-Optimierung"]},
        ],
    },
    # julia.data
    {
        "business": "julia.data",
        "title": "Datenanalyse & Visualisierung",
        "description": "Professionelle Datenanalyse mit Python, Pandas und modernen Visualisierungstools. Ich mache aus deinen Rohdaten verständliche Dashboards und aussagekräftige Reports.",
        "details": [
            {"title": "Quick Analysis", "offer_type": "basic", "revisions": 1, "delivery_time_in_days": 3, "price": "249.00", "features": ["Datenbereinigung", "Grundlegende Analyse", "PDF-Report", "Bis zu 3 Visualisierungen"]},
            {"title": "Deep Dive", "offer_type": "standard", "revisions": 2, "delivery_time_in_days": 7, "price": "699.00", "features": ["Umfassende Analyse", "Interaktives Dashboard", "Statistische Auswertung", "Handlungsempfehlungen", "Jupyter Notebook"]},
            {"title": "Enterprise Analytics", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 14, "price": "1799.00", "features": ["Prädiktive Modelle", "Machine Learning", "Automatisierte Pipelines", "Custom Dashboard", "Ongoing Monitoring", "Technische Dokumentation"]},
        ],
    },
    {
        "business": "julia.data",
        "title": "Machine Learning Modell-Entwicklung",
        "description": "Maßgeschneiderte ML-Modelle für dein Unternehmen. Von der Datenaufbereitung über das Training bis zur Deployment-fertigen Lösung.",
        "details": [
            {"title": "POC Modell", "offer_type": "basic", "revisions": 1, "delivery_time_in_days": 7, "price": "599.00", "features": ["Proof of Concept", "1 ML-Modell", "Evaluation Report", "Jupyter Notebook"]},
            {"title": "Production Modell", "offer_type": "standard", "revisions": 2, "delivery_time_in_days": 14, "price": "1499.00", "features": ["Optimiertes Modell", "API-Endpoint", "Modell-Monitoring", "Dokumentation", "A/B Testing"]},
            {"title": "ML Pipeline", "offer_type": "premium", "revisions": -1, "delivery_time_in_days": 28, "price": "3499.00", "features": ["End-to-End Pipeline", "Automatisiertes Training", "Model Registry", "Feature Store", "Monitoring Dashboard", "MLOps Setup"]},
        ],
    },
]


REVIEWS = [
    # Reviews for maxdev
    {"business": "maxdev", "reviewer": "petra.startup", "rating": 5, "description": "Max hat unsere REST API in Rekordzeit entwickelt. Sauberer Code, gute Dokumentation und sehr gute Kommunikation. Absolut zu empfehlen!"},
    {"business": "maxdev", "reviewer": "markus.agentur", "rating": 5, "description": "Hervorragende Arbeit! Die API läuft stabil und performant. Max hat proaktiv Optimierungsvorschläge gemacht, die uns viel Zeit gespart haben."},
    {"business": "maxdev", "reviewer": "david.tech", "rating": 4, "description": "Sehr gute technische Umsetzung. Die Lieferzeit war etwas länger als erwartet, aber das Endergebnis hat die Erwartungen übertroffen."},
    {"business": "maxdev", "reviewer": "lena.freelance", "rating": 5, "description": "Professionell von Anfang bis Ende. Max hat meine Anforderungen sofort verstanden und eine perfekte Lösung geliefert. Werde definitiv wieder buchen!"},
    # Reviews for sarah.designs
    {"business": "sarah.designs", "reviewer": "petra.startup", "rating": 5, "description": "Sarahs Designs sind einfach wunderschön! Sie hat unsere vagen Vorstellungen in ein perfektes UI verwandelt. Die Nutzerführung ist durchdacht und intuitiv."},
    {"business": "sarah.designs", "reviewer": "nina.design", "rating": 5, "description": "Als Designerin weiß ich, worauf es ankommt — und Sarah liefert erstklassige Qualität. Das Design System ist sauber strukturiert und gut dokumentiert."},
    {"business": "sarah.designs", "reviewer": "markus.agentur", "rating": 4, "description": "Tolles Design mit Liebe zum Detail. Die responsive Umsetzung war pixelgenau. Einzig die Abstimmungsphase hätte etwas schneller gehen können."},
    {"business": "sarah.designs", "reviewer": "david.tech", "rating": 5, "description": "Sarah versteht es, technische Anforderungen mit ästhetischem Design zu verbinden. Unsere Nutzer lieben das neue Interface!"},
    # Reviews for devops.felix
    {"business": "devops.felix", "reviewer": "david.tech", "rating": 5, "description": "Felix hat unsere gesamte Infrastruktur auf AWS migriert. CI/CD Pipeline läuft perfekt, Deployments sind jetzt vollautomatisch. Erstklassige Arbeit!"},
    {"business": "devops.felix", "reviewer": "markus.agentur", "rating": 4, "description": "Sehr kompetent im Bereich DevOps. Das Docker-Setup funktioniert einwandfrei und die Dokumentation ist gut verständlich."},
    {"business": "devops.felix", "reviewer": "petra.startup", "rating": 5, "description": "Als Startup waren wir mit dem Cloud-Setup überfordert. Felix hat alles professionell eingerichtet und uns die Grundlagen erklärt. Top!"},
    # Reviews for anna.backend
    {"business": "anna.backend", "reviewer": "lena.freelance", "rating": 5, "description": "Anna hat meine Datenbank komplett überarbeitet und optimiert. Die Queries sind jetzt 10x schneller. Sehr beeindruckend!"},
    {"business": "anna.backend", "reviewer": "petra.startup", "rating": 4, "description": "Gute Arbeit bei der API-Entwicklung. Anna ist sehr gewissenhaft und liefert sauberen, gut getesteten Code."},
    {"business": "anna.backend", "reviewer": "david.tech", "rating": 5, "description": "Hervorragende Python-Automatisierung. Anna hat unsere manuellen Prozesse komplett automatisiert und uns damit viele Arbeitsstunden gespart."},
    # Reviews for tom.mobile
    {"business": "tom.mobile", "reviewer": "markus.agentur", "rating": 5, "description": "Tom hat eine fantastische React Native App für unseren Kunden entwickelt. Läuft perfekt auf iOS und Android. Sehr empfehlenswert!"},
    {"business": "tom.mobile", "reviewer": "nina.design", "rating": 4, "description": "Die App-Umsetzung meines Designs war sehr gut. Tom hat die Animationen und Übergänge sauber implementiert. Kleine Anpassungen waren schnell erledigt."},
    {"business": "tom.mobile", "reviewer": "petra.startup", "rating": 5, "description": "Unsere erste App und Tom hat den gesamten Prozess bis zum App Store begleitet. Professionell, zuverlässig und technisch top."},
    # Reviews for julia.data
    {"business": "julia.data", "reviewer": "david.tech", "rating": 5, "description": "Julia hat unsere Verkaufsdaten analysiert und ein prädiktives Modell erstellt. Die Genauigkeit ist beeindruckend und das Dashboard sehr nützlich."},
    {"business": "julia.data", "reviewer": "markus.agentur", "rating": 5, "description": "Die Datenanalyse von Julia war extrem aufschlussreich. Sie hat Muster entdeckt, die uns vorher völlig entgangen waren. Absolute Spezialistin!"},
    {"business": "julia.data", "reviewer": "lena.freelance", "rating": 4, "description": "Sehr kompetent in Sachen Datenanalyse. Julia hat mir geholfen, meine Marketing-Daten besser zu verstehen und datenbasierte Entscheidungen zu treffen."},
]


ORDERS = [
    # Orders from petra.startup
    {"customer": "petra.startup", "business": "maxdev", "offer_title": "Professionelle Django REST API Entwicklung", "offer_type": "standard", "status": "completed"},
    {"customer": "petra.startup", "business": "sarah.designs", "offer_title": "UI/UX Design für Web-Anwendungen", "offer_type": "standard", "status": "completed"},
    {"customer": "petra.startup", "business": "devops.felix", "offer_title": "Cloud-Infrastruktur & DevOps Setup", "offer_type": "basic", "status": "completed"},
    {"customer": "petra.startup", "business": "tom.mobile", "offer_title": "React Native App-Entwicklung", "offer_type": "basic", "status": "in_progress"},
    # Orders from markus.agentur
    {"customer": "markus.agentur", "business": "maxdev", "offer_title": "React Frontend-Entwicklung", "offer_type": "premium", "status": "completed"},
    {"customer": "markus.agentur", "business": "sarah.designs", "offer_title": "Responsive HTML/CSS Umsetzung aus Figma", "offer_type": "standard", "status": "completed"},
    {"customer": "markus.agentur", "business": "tom.mobile", "offer_title": "React Native App-Entwicklung", "offer_type": "standard", "status": "in_progress"},
    {"customer": "markus.agentur", "business": "julia.data", "offer_title": "Datenanalyse & Visualisierung", "offer_type": "standard", "status": "completed"},
    # Orders from david.tech
    {"customer": "david.tech", "business": "maxdev", "offer_title": "Professionelle Django REST API Entwicklung", "offer_type": "premium", "status": "completed"},
    {"customer": "david.tech", "business": "devops.felix", "offer_title": "Cloud-Infrastruktur & DevOps Setup", "offer_type": "premium", "status": "in_progress"},
    {"customer": "david.tech", "business": "anna.backend", "offer_title": "Python-Automatisierung & Scripting", "offer_type": "premium", "status": "completed"},
    {"customer": "david.tech", "business": "julia.data", "offer_title": "Machine Learning Modell-Entwicklung", "offer_type": "standard", "status": "in_progress"},
    # Orders from lena.freelance
    {"customer": "lena.freelance", "business": "anna.backend", "offer_title": "Datenbank-Design & Optimierung", "offer_type": "standard", "status": "completed"},
    {"customer": "lena.freelance", "business": "maxdev", "offer_title": "React Frontend-Entwicklung", "offer_type": "basic", "status": "completed"},
    {"customer": "lena.freelance", "business": "julia.data", "offer_title": "Datenanalyse & Visualisierung", "offer_type": "basic", "status": "completed"},
    # Orders from nina.design
    {"customer": "nina.design", "business": "sarah.designs", "offer_title": "UI/UX Design für Web-Anwendungen", "offer_type": "premium", "status": "completed"},
    {"customer": "nina.design", "business": "tom.mobile", "offer_title": "React Native App-Entwicklung", "offer_type": "standard", "status": "completed"},
    {"customer": "nina.design", "business": "anna.backend", "offer_title": "Python-Automatisierung & Scripting", "offer_type": "basic", "status": "in_progress"},
]


class Command(BaseCommand):
    help = "Seed the database with professional demo data (users, offers, orders, reviews)"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing non-staff data before seeding")

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Order.objects.all().delete()
            Review.objects.all().delete()
            OfferDetail.objects.all().delete()
            Offer.objects.all().delete()
            UserProfile.objects.filter(user__is_staff=False, user__is_superuser=False).delete()
            User.objects.filter(is_staff=False, is_superuser=False).delete()
            Token.objects.filter(user__is_staff=False, user__is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("  Cleared."))

        profiles = {}

        # Create guest users
        self._create_user_with_profile(profiles, "guest.customer", "guest_customer@guest.de", "Guest", "Customer", "customer", {
            "location": "Demo Stadt",
            "description": "Demo-Account für Kunden. Einfach einloggen und die Plattform testen!",
        }, password="o6B6<c1x|`N2")
        self._create_user_with_profile(profiles, "guest.business", "guest_business@guest.de", "Guest", "Business", "business", {
            "location": "Demo Stadt",
            "description": "Demo-Account für Anbieter. Einfach einloggen und Angebote erstellen!",
            "working_hours": "Mo-Fr 9:00 - 17:00",
        }, password="o6B6<c1x|`N2")

        # Create business users
        for data in BUSINESS_USERS:
            extra = {k: data[k] for k in ("location", "tel", "description", "working_hours") if k in data}
            self._create_user_with_profile(profiles, data["username"], data["email"], data["first_name"], data["last_name"], "business", extra)

        # Create customer users
        for data in CUSTOMER_USERS:
            extra = {k: data[k] for k in ("location", "description") if k in data}
            self._create_user_with_profile(profiles, data["username"], data["email"], data["first_name"], data["last_name"], "customer", extra)

        self.stdout.write(self.style.SUCCESS(f"  Created {len(profiles)} user profiles."))

        # Create offers
        offer_count = 0
        for offer_data in OFFERS:
            profile = profiles.get(offer_data["business"])
            if not profile:
                continue
            offer, created = Offer.objects.get_or_create(
                user_profile=profile,
                title=offer_data["title"],
                defaults={"description": offer_data["description"]},
            )
            if created:
                offer_count += 1
                for detail in offer_data["details"]:
                    OfferDetail.objects.get_or_create(
                        offer=offer,
                        offer_type=detail["offer_type"],
                        defaults={
                            "title": detail["title"],
                            "revisions": detail["revisions"],
                            "delivery_time_in_days": detail["delivery_time_in_days"],
                            "price": Decimal(detail["price"]),
                            "features": detail["features"],
                        },
                    )
        self.stdout.write(self.style.SUCCESS(f"  Created {offer_count} offers with details."))

        # Create orders
        order_count = 0
        for order_data in ORDERS:
            customer = profiles.get(order_data["customer"])
            if not customer:
                continue
            try:
                detail = OfferDetail.objects.get(
                    offer__user_profile=profiles[order_data["business"]],
                    offer__title=order_data["offer_title"],
                    offer_type=order_data["offer_type"],
                )
            except OfferDetail.DoesNotExist:
                self.stderr.write(f"  Skipping order: detail not found for {order_data['offer_title']} ({order_data['offer_type']})")
                continue
            if not Order.objects.filter(customer_user=customer, offer_detail=detail).exists():
                Order.objects.create(customer_user=customer, offer_detail=detail, status=order_data["status"])
                order_count += 1
        self.stdout.write(self.style.SUCCESS(f"  Created {order_count} orders."))

        # Create reviews
        review_count = 0
        for review_data in REVIEWS:
            business = profiles.get(review_data["business"])
            reviewer = profiles.get(review_data["reviewer"])
            if not business or not reviewer:
                continue
            if not Review.objects.filter(business_user=business, reviewer=reviewer).exists():
                Review.objects.create(
                    business_user=business,
                    reviewer=reviewer,
                    rating=review_data["rating"],
                    description=review_data["description"],
                )
                review_count += 1
        self.stdout.write(self.style.SUCCESS(f"  Created {review_count} reviews."))

        self.stdout.write(self.style.SUCCESS("\nSeeding complete!"))
        self.stdout.write(f"  Demo login password: {DEMO_PASSWORD}")
        self.stdout.write(f"  Guest customer: guest.customer / o6B6<c1x|`N2")
        self.stdout.write(f"  Guest business: guest.business / o6B6<c1x|`N2")

    def _create_user_with_profile(self, profiles, username, email, first_name, last_name, user_type, extra=None, password=None):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        if created:
            user.set_password(password or DEMO_PASSWORD)
            user.save()
            Token.objects.get_or_create(user=user)

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={"type": user_type},
        )
        if extra:
            for key, value in extra.items():
                setattr(profile, key, value)
            profile.save()

        profiles[username] = profile
