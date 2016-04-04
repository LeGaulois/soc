
function toggleMe(a){
	var e=document.getElementById(a);
	if(!e)return true;
	if(e.style.display=="none"){
		e.style.display="block"
	}
	else{
		e.style.display="none"
	}
	return true;
}



function Selection() {

	var e=document.getElementById('id_type_selection');
	var tableau=[];
	var x = document.getElementsByTagName("label");
	var i;
	var j;
	var k;

	var valeur=e.options[ e.selectedIndex ].value;
	
	if(valeur!=''){
		document.getElementById(valeur).style.display="block";
	}
	

	for (i = 0; i < e.options.length; i++) {
		option=e.options[i].value;

		if ((option!=valeur)&&(option!='')) {
			tableau.push(option);
			document.getElementById(option).style.display='none';
		}
	}


	for (j = 0; j < x.length; j++) {
		var f=x[j].htmlFor;

		if (f==valeur){
			x[j].style.display="block";
		}
		
		else {
			for (k = 0; k < tableau.length; k++) {
				if (f==tableau[k]) {
					x[j].style.display="none";
				}
				
			}
		}
	}
}



function updateScans() {
    ajaxGet('/scans/getStatusScans/',function(content){

        try {   
            var tableau=document.getElementById('tableau_scans');
            var lignes=tableau.rows;
            var cells_restantes=[];

            for (var k= 0; k < lignes.length; k++) {
                cells_restantes.push(k);
            }
        }
        catch(e){}

        for (var i = 0; i < content.length; i++) {
            var id=content[i]['id_scan'];
            var nmap_status=content[i]['nmap']['status'];
            var nmap_progress=content[i]['nmap']['progress'];
            var nmap_import=content[i]['nmap']['import'];
            var nessus_status=content[i]['nessus']['status'];
            var nessus_progress=content[i]['nessus']['progress'];
            var nessus_import=content[i]['nessus']['import'];


            var tableau=document.getElementById('tableau_scans');

            if (tableau==null){
                var div=document.getElementById('scans_en_cours');
                div.innerHTML="";
                var table='<table class="table table-striped table-bordered">\
                    <thead>\
                        <tr>\
	                        <th><center>Nmap Status</center></th>\
	                        <th><center>Nmap Progress</center></th>\
	                        <th><center>Nmap Import</center></th>\
	                        <th><center>Nessus Status</center></th>\
	                        <th><center>Nessus Progress</center></th>\
	                        <th><center>Nessus Import</center></th>\
                        </tr>\
                    </thead>\
                    <tbody id=tableau_scans>\
                    </tbody>\
                </table>';
                div.innerHTML=table;
                
                tableau=document.getElementById('tableau_scans');
                var nouvelleLigne=tableau.insertRow(0);
                nouvelleLigne.id='scan_'+id;
                nouvelleLigne.insertCell(0);
                var graph=nouvelleLigne.insertCell(1);
                graph.class='graph';
                nouvelleLigne.insertCell(2);
                nouvelleLigne.insertCell(3);
                graph=nouvelleLigne.insertCell(4);
                graph.class='graph';
                nouvelleLigne.insertCell(5);
            }

            var lignes=tableau.rows;

            for (var j= 0; j < lignes.length; j++) {
                if ((j==lignes.length-1)&&(lignes[j].id!='scan_'+id)) {
                    var nouvelleLigne=tableau.insertRow(0);
                    nouvelleLigne.id='scan_'+id;
                    nouvelleLigne.insertCell(0);
                    var graph=nouvelleLigne.insertCell(1);
                    graph.class='graph';
                    nouvelleLigne.insertCell(2);
                    nouvelleLigne.insertCell(3);
                    graph=nouvelleLigne.insertCell(4);
                    graph.class='graph';
                    nouvelleLigne.insertCell(5);
                }

                if (lignes[j].id=='scan_'+id) {
                    colonnes=lignes[j].cells;

                    colonnes[0].innerHTML='<center>'+nmap_status+'</center>';
                    colonnes[1].innerHTML='<div id="'+id+'-nmap"></div>';
                    $("#"+id+'-nmap').circliful({
                    animationStep: 500,
                    percentageTextSize:30,
                    percent: nmap_progress,
                    backgroundBorderWidth: 15,
                    foregroundBorderWidth: 15
                    });

                    colonnes[2].innerHTML='<center>'+nmap_import+'</center>';

                    colonnes[3].innerHTML='<center>'+nessus_status+'</center>';
                    colonnes[4].innerHTML='<div id="'+id+'-nessus"></div>';
                    $("#"+id+'-nessus').circliful({
                    animationStep: 500,
                    percentageTextSize:30,
                    percent: nessus_progress,
                    backgroundBorderWidth: 15,
                    foregroundBorderWidth: 15
                    });
                    colonnes[5].innerHTML='<center>'+nessus_import+'</center>';
                    break
                }
            }
        }

        if(content.length==0) {
            $("table").remove();
        }

        try {   
            for (var k= 0; k < cells_restantes.length; k++) {
                cells_restantes.splice(k,1);
            }
        }
        catch (e){}
    })


    setTimeout(updateScans, 10000);
}


function supprimerEntreeHistorique(id_scan) {
    
    ajaxGet('/scans/supprimerEntreeHistorique/'+id_scan,function(content){
        var tableau=document.getElementById('tableau_scans');
        var lignes=tableau.rows;

        for (var j= 0; j < lignes.length; j++) {
            if (lignes[j].id==id_scan) {
                tableau.deleteRow(j);
            }
        }
    })        

}

