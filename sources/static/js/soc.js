
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

function Test(){alert('test');}

