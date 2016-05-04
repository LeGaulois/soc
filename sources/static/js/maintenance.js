function testPostgreSQL() {
    $( "#popup" ).dialog({
        title: "test PostgreSQL",
    });
    $( "#popup" ).dialog("open");

    var div=document.getElementById('popup');    

    div.innerHTML="Test de connection en cours...";

    ajaxPost('/maintenance/testConnectionSQL/',{
            'host': document.getElementById('id_0-pg_ip').value,
            'port': document.getElementById('id_0-pg_port').value,
            'database': document.getElementById('id_0-pg_base').value,
            'user': document.getElementById('id_0-pg_user').value,
            'password': document.getElementById('id_0-pg_password').value
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

    ajaxPost('/maintenance/testConnectionNessus/',{
            'host': document.getElementById('id_1-nessus_ip').value,
            'port': document.getElementById('id_1-nessus_port').value,
            'user': document.getElementById('id_1-nessus_user').value,
            'password': document.getElementById('id_1-nessus_password').value
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
                'password': document.getElementById('mail_password').value
    })
}

function validerVariables() {
    ajaxPost('/maintenance/validerVariables/',{
                'localisation': document.getElementById('var_localisation').value,
                'type': document.getElementById('var_type').value,
                'environnement': document.getElementById('var_environnement').value
    })
}
