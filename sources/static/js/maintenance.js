function testPostgreSQL() {
    $( "#popup" ).dialog({
        title: "test PostgreSQL",
    });
    $( "#popup" ).dialog("open");

    var div=document.getElementById('popup');    

    div.innerHTML="Test de connection en cours...";

    ajaxPost('/maintenance/testConnectionSQL/',{
            'address': document.getElementById('postgresql_addr').value,
            'port': document.getElementById('postgresql_port').value,
            'database': document.getElementById('postgresql_database').value,
            'login': document.getElementById('postgresql_login').value,
            'password': document.getElementById('postgresql_password').value
            },function(content){
                if (content=='OK'){div.innerHTML="<br><span style ='float'><img src='/static/img/ok.png' %}' alt='completed' style='width:30px;height:30px;'></span>Connection reussi";
                document.getElementById('suivant').disabled=false;}
                else {div.innerHTML="<br><span style ='float'><img src='/static/img/error.png' %}' alt='completed' style='width:30px;height:30px;'></span>  "+content; }
    })
}


function testNessus() {
    $( "#popup" ).dialog({
        title: "test Nessus",
        buttons:{},
    });
    $( "#popup" ).dialog("open");

    var div=document.getElementById('popup');    

    div.innerHTML="<br>Test de connection en cours...";

    try {	
    	var verify = document.getElementById('nessus_verify').value;
    }

    catch (err) {
    	var verify = 'off';
    }	

    ajaxPost('/maintenance/testConnectionNessus/',{
            'address': document.getElementById('nessus_addr').value,
            'port': document.getElementById('nessus_port').value,
            'login': document.getElementById('nessus_login').value,
            'password': document.getElementById('nessus_password').value,
	    'verify': verify	    
            },function(content){
                if (content=='OK'){div.innerHTML="<br><span style ='float'><img src='/static/img/ok.png' %}' alt='completed' style='width:30px;height:30px;'></span>  Connection reussi";
                document.getElementById('suivant').disabled=false;
                }
                else {div.innerHTML="<br><span style ='float'><img src='/static/img/error.png' %}' alt='completed' style='width:30px;height:30px;'></span>  "+content; }
    })
}


function testMail() {
    $( "#popup" ).dialog({
        title: "test Mail",
        buttons:{},
    });
    $( "#popup" ).dialog("open");

    var div=document.getElementById('popup');    

    div.innerHTML="<br>Test de connection en cours...";	

    ajaxPost('/maintenance/testConnectionMail/',{
            'address': document.getElementById('mail_addr').value,
            'port': document.getElementById('mail_port').value,
            'login': document.getElementById('mail_login').value,
            'password': document.getElementById('mail_password').value,
	    'tls': document.getElementById('mail_tls').value 	    
            },function(content){
                if (content=='OK'){div.innerHTML="<br><span style ='float'><img src='/static/img/ok.png' %}' alt='completed' style='width:30px;height:30px;'></span>  Connection reussi";
                document.getElementById('suivant').disabled=false;
                }
                else {div.innerHTML="<br><span style ='float'><img src='/static/img/error.png' %}' alt='completed' style='width:30px;height:30px;'></span>  "+content; }
    })
}



function alertAlreadyInit() {
    $( "#popup" ).dialog({
        title: "ATTENTION !!",
        resizable: false,
        modal: true,
        buttons: {
        "continuer": function() {
          $( this ).dialog( "destroy");
          $( this ).dialog( "close" );
        },
        "Annuler": function() {
            location.replace("/serveurs/liste")
        }
      }
    });

    var div=document.getElementById('popup');
    div.innerHTML="<FONT color='red'>Le projet est déjà initialisé !!<br> Si vous continuez, toutes les données seront perdues</FONT>";   
}



function validerNessus() {
    ajaxPost('/maintenance/validerNessus/',{
                'address': document.getElementById('nessus_addr').value,
                'port': document.getElementById('nessus_port').value,
                'login': document.getElementById('nessus_login').value,
                'password': document.getElementById('nessus_password').value,
                'directory-id': document.getElementById('nessus_directory-id').value,
                'verify': document.getElementById('nessus_verify').value
    })
}

function validerMail() {
    ajaxPost('/maintenance/validerMail/',{
                'address': document.getElementById('mail_addr').value,
                'port': document.getElementById('mail_port').value,
                'login': document.getElementById('mail_login').value,
                'password': document.getElementById('mail_password').value,
		'tls': document.getElementById('mail_tls').value	
    })
}

function validerVariables() {
    ajaxPost('/maintenance/validerVariables/',{
                'localisation': document.getElementById('var_localisation').value,
                'type': document.getElementById('var_type').value,
                'environnement': document.getElementById('var_environnement').value
    })
}


function validerInfosRapports() {
var temp=document.getElementById('infos-rapports_logo');
var image=temp.files[0];

    ajaxPost('/maintenance/validerInfosRapports/',{
                'societe': document.getElementById('infos-rapports_societe').value,
                'auteur': document.getElementById('infos-rapports_auteur').value,
		'logo':
    })
}
