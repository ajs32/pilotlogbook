
// Radio buttons PF and PM
document.querySelector("#pf").onclick = function()
{
	if (document.querySelector("#pm").checked == true)
	{document.querySelector("#pm").checked = false;}
}
document.querySelector("#pm").onclick = function()
{
	if (document.querySelector("#pf").checked == true)
	{document.querySelector("#pf").checked = false;}
}

function print()
{
	alert("This option is under development");
}

function set_id(x)
{	
	document.querySelector("#flt_id").value = x;
	document.getElementById("f_edit").submit();
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

function print_selected()
{
	document.querySelector("#print").style.color = 'red';	
	document.querySelector("#print").style.textDecoration = "underline";
}
function print_norm()
{
	document.querySelector("#print").style.color = 'blue';	
	document.querySelector("#print").style.textDecoration = "none";
}


// Get PF/PM and Name of the user from DB for Autolog
function get_settings()
{
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() 
	{
	    if (this.readyState == 4 && this.status == 200) 
			{
			   // if no settings were saved yet, NIL is returned
				if (xhttp.responseText != "nil") {
					let a = (xhttp.responseText).split(',')

					if (a[1] == "PIC")
					{
						document.querySelector("#pic_name").value = a[0];
						document.querySelector("#pic_time").value = document.querySelector("#tot_time").value; 
					}
					else if (a[1] == "FO")
					{
						document.querySelector("#fo_name").value = a[0];
						document.querySelector("#fo_time").value = document.querySelector("#tot_time").value; 
					}

				}
			}
	};	
	xhttp.open("POST", "/", true);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send("todo=get_settings");	
}



// Copy TOTAL TIME
document.querySelector("#pic_time").onclick = function()
{
	document.querySelector("#fo_time").value = "";
	document.querySelector("#dual_time").value = "";
	document.querySelector("#pic_time").value = document.querySelector("#tot_time").value; }
document.querySelector("#fo_time").onclick = function()
{
	document.querySelector("#pic_time").value = "";
	document.querySelector("#dual_time").value = "";
	document.querySelector("#fo_time").value = document.querySelector("#tot_time").value; }
document.querySelector("#dual_time").onclick = function()
{
	document.querySelector("#fo_time").value = "";
	document.querySelector("#pic_time").value = "";
	document.querySelector("#dual_time").value = document.querySelector("#tot_time").value; }
document.querySelector("#instr_time").onclick = function()
{
	document.querySelector("#instr_time").value = document.querySelector("#tot_time").value; }
document.querySelector("#exam_time").onclick = function()
{
	document.querySelector("#exam_time").value = document.querySelector("#tot_time").value; }
document.querySelector("#night_time").onclick = function()
{
	document.querySelector("#night_time").value = document.querySelector("#tot_time").value; }
document.querySelector("#ifr_time").onclick = function()
{
	document.querySelector("#vfr_time").value = "";
	document.querySelector("#ifr_time").value = document.querySelector("#tot_time").value; }
document.querySelector("#vfr_time").onclick = function()
{
	document.querySelector("#ifr_time").value = "";
	document.querySelector("#vfr_time").value = document.querySelector("#tot_time").value; }


// Display RED warning message
function flt_msg_red(x)
{
	document.querySelector("#flt_msg").style.color = 'red';
	document.querySelector("#flt_msg").innerHTML = x;	
}

// Check required inputs for adding flight are present and SEND
document.querySelector("#b_addflt").onclick = function()
{
//	alert(ran_key()); return;
	if (document.querySelector("#flt_nr").value == '')
		{ 
			flt_msg_red("Flight number is missing"); document.querySelector("#flt_nr").focus(); return; }
	else if (document.querySelector("#dep_ap").value == '')
		{ 
			flt_msg_red("Departure airport code is missing"); document.querySelector("#dep_ap").focus(); return; }
	else if (document.querySelector("#dep_date").value == '')
		{ 
			flt_msg_red("Departure date is missing"); document.querySelector("#dep_date").focus(); return; }
	else if (document.querySelector("#dep_time").value == '')
		{ 
			flt_msg_red("Departure time is missing"); document.querySelector("#dep_time").focus(); return; }
	else if (document.querySelector("#arr_ap").value == '')
		{ 
			flt_msg_red("Arrival airport code is missing"); document.querySelector("#arr_ap").focus(); return; }
	else if (document.querySelector("#arr_date").value == '')
		{ 
			flt_msg_red("Arrival date is missing"); document.querySelector("#arr_date").focus(); return; }
	else if (document.querySelector("#arr_time").value == '')
		{ 
			flt_msg_red("Arrival time is missing"); document.querySelector("#arr_time").focus(); return; }
	else if (document.querySelector("#reg").value == '')
		{ 
			flt_msg_red("Aircraft registration is missing"); document.querySelector("#reg").focus(); return; }
	else if (document.querySelector("#pic_name").value == '')
		{ 
			flt_msg_red("Name of Pilot-In-Command is missing"); document.querySelector("#pic_name").focus(); return; }
	else if (document.querySelector("#tot_time").value == "Error with Date/Time")
		{ 
			flt_msg_red("Check departure and arrival dates and time"); return; }
	else
        {
			document.querySelector("#key").value = ran_key();
			document.querySelector("#f_addflt").submit(); }
}

function set_arr_date()
{
	if (document.querySelector("#dep_date").value != "" && document.querySelector("#dep_time").value != "")
	{
		if (document.querySelector("#dep_time").value < document.querySelector("#arr_time").value)
		{
			document.querySelector("#arr_date").value = document.querySelector("#dep_date").value;
		}
		else
		{
			arr_date = new Date(document.querySelector("#dep_date").value)
			document.querySelector("#arr_date").value = arr_date.getFullYear() + "-" + a0((arr_date.getMonth()+1)) + "-" + a0((arr_date.getDate()+1));
		}		
		calc_tot_time();
	}
}

// Calculate TOTAL FLIGHT TIME
function calc_tot_time()
{	// check all dep/arr info present
	if (document.querySelector("#dep_date").value != "" && document.querySelector("#dep_time").value != "" && document.querySelector("#arr_date").value != "" && document.querySelector("#arr_time").value != "")
	{	// get DEP and ARR date objects
		dep_date = new Date(document.querySelector("#dep_date").value + " " + document.querySelector("#dep_time").value + ":00");
		arr_date = new Date(document.querySelector("#arr_date").value + " " + document.querySelector("#arr_time").value + ":00");
		// Get total minutes and from there minutes and hours. 1min = 60000mSec
		tot_minutes = (arr_date.getTime() - dep_date.getTime()) / 60000;
		if (tot_minutes < 0)
		{
			document.querySelector("#tot_time").style.color = 'red';
			document.querySelector("#tot_time").value = "Error with Date/Time";
		}
		else
		{
			minutes = tot_minutes % 60;
			if (minutes < 10) {minutes = "0" + minutes;}

			hours = (tot_minutes - minutes) / 60;
			if (hours < 10) {hours = "0" + hours;}

			document.querySelector("#tot_time").style.color = 'black';
			document.querySelector("#tot_time").value = hours + ":" + minutes;
			document.querySelector("#tot_minutes").value = tot_minutes;
			get_settings();
		}
	}
}

