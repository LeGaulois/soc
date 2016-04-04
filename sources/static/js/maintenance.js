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
