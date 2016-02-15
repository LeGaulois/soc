from menu import Menu, MenuItem
from django.core.urlresolvers import reverse


Menu.add_item("main", MenuItem("Liste Machines",
                               reverse("liste_machines",args=None,kwargs=None,current_app='serveurs')))


Menu.add_item("main", MenuItem("Applis",
                               reverse("liste_applis",None,None,current_app="serveurs")))


scans_children = (
    MenuItem("Manuel",
             reverse("listeScan",None,None,current_app="serveurs"),
             weight=10),
    MenuItem("Auto",
             reverse("listeScan",None,None,current_app="serveurs"),
             weight=80,
             separator=True),
)


Menu.add_item("main", MenuItem("Scans",
                               reverse("listeScan",None,None,current_app="serveurs"),
			       children=scans_children))

