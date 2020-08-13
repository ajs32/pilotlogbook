
function lookup()
{
	if(document.querySelector("#iata").value == ''  && document.querySelector("#icao").value == ''  && document.querySelector("#name").value == ''  && document.querySelector("#city").value == ''  && document.querySelector("#country").value == '')
	{
		document.querySelector("#msg_lookup").style.color = 'red';
		document.querySelector("#msg_lookup").innerHTML = "Enter either IATA, ICAO codes or Airport name, City or Country";
	}
	else
	{
		let query = "";
		if (document.querySelector("#iata").value != '') { query += "&iata="+document.querySelector("#iata").value; }
		if (document.querySelector("#icao").value != '') { query += "&icao="+document.querySelector("#icao").value; }
		if (document.querySelector("#name").value != '') { query += "&name="+document.querySelector("#name").value; }
		if (document.querySelector("#city").value != '') { query += "&city="+document.querySelector("#city").value; }
		if (document.querySelector("#country").value != '') { query += "&country="+document.querySelector("#country").value; }

		var xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				// if ERROE is returned
				if (xhttp.responseText[0] == "E"){
					document.querySelector("#msg_lookup").style.color = 'red';
					document.getElementById("msg_lookup").innerHTML = xhttp.responseText.slice(1,); }
				else{

						let new_tbl = '<table class="main_table"><thead><caption style="text-align: left; font-size:large;"><label>Airport information</label></caption></thead><tbody>';
						let cnt = 0;

						let x = (xhttp.responseText).split('[')

						// devide response into separate lists
						var lists = (x[1]).slice(1,-2).split('), (')

						// split each list into info items and add them to info list
						let ap_inf = [];
						for (cnt=0; cnt < lists.length; cnt++)
						{
							ap_inf.push((lists[cnt]).split(','))					
						}	

						for (let cnt = 0; cnt < x[0]; cnt++)
						{ 
							if (cnt > 0) {new_tbl+='<tr><th style="height:12px;"></th></tr>';}
							new_tbl += '<tr><th style="width: 150px;">Airport name</th><td>'+ap_inf[cnt][0].slice(1,-1)+'</td></tr><tr><th style="width: 150px;">Airport IATA code</th><td>'+ap_inf[cnt][1].slice(2,-1)+'</td></tr><tr><th style="width: 150px;">Airport ICAO code</th><td>'+ap_inf[cnt][2].slice(2,-1)+'</td></tr><tr><th style="width: 150px;">City</th><td>'+ap_inf[cnt][3].slice(2,-1)+'</td></tr><tr><th style="width: 150px;">Country</th><td>'+ap_inf[cnt][4].slice(2,-1)+'</td></tr><tr></tr></tbody>'; }

						new_tbl += "</table>";

						document.querySelector("#msg_lookup").style.color = 'green';
						document.querySelector("#msg_lookup").innerHTML = "Airport information retrieved"; 

						document.querySelector("#ap_info").innerHTML = new_tbl;
					}
			}
		};
	
		xhttp.open("POST", "/airports", true);
		xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
		xhttp.send("todo=lookup"+query);
	}
}


// Check required inputs are present and submit
function submit_airport()
{
	if (document.querySelector("#upd_iata").value == ''){
		document.querySelector("#msg_update").innerHTML = "Airport IATA code is missing"; }
	else if (document.querySelector("#upd_icao").value == ''){
		document.querySelector("#msg_update").innerHTML = "Airport ICAO code is missing"; }
	else if (document.querySelector("#upd_name").value == ''){
		document.querySelector("#msg_update").innerHTML = "Airport NAME is missing"; }
	else if (document.querySelector("#upd_city").value == ''){
		document.querySelector("#msg_update").innerHTML = "Airport CITY is missing"; }
	else if (document.querySelector("#upd_country").value == ''){
		document.querySelector("#msg_update").innerHTML = "Airport COUNTRY is missing"; }
	else
        {
			document.getElementById("f_updap").submit();
		}
}

function update_airport()
{
	document.querySelector("#todo").value = "update";
	submit_airport();
}

function get_ap_info(x)
{	
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			// if ERROE is returned
			if (xhttp.responseText[0] == "E"){
				document.querySelector("#msg_update").style.color = 'red';
				document.querySelector("#msg_update").innerHTML = xhttp.responseText; }
			else{
				let ap_inf = (xhttp.responseText).slice(2,-2).split(',')
				//iata
				document.querySelector("#upd_iata").value = (ap_inf[0]).slice(1,-1);
				//icao
				document.querySelector("#upd_icao").value = (ap_inf[1]).slice(2,-1);
				//name
				document.querySelector("#upd_name").value = (ap_inf[2]).slice(2,-1);
				//city
				document.querySelector("#upd_city").value = (ap_inf[3]).slice(2,-1);
				//country
				document.querySelector("#upd_country").value = (ap_inf[4]).slice(2,-1);

				// enable update button
				document.querySelector("#b_update").disabled = false;
				}
		}
	};
	document.querySelector("#ap_id").value = x;

	xhttp.open("POST", "/airports", true);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send("todo=display&ap_id="+x);
}


function col_selected(x)
{
	x = "#row" + x;
	document.querySelector(x).style.color = 'blue';	
}
function col_norm(x)
{
	x = "#row" + x;
	document.querySelector(x).style.color = 'black';	
}

