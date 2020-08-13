
function check_inputs()
{
	let inp = document.querySelector("#date").value;
	if (inp.length != 10) {alert("Date is of invalid format"); return false;}
	else if (inp.split('-').length != 3) {alert("Date is of invalid format"); return false;}
	inp = document.querySelector("#dep_time").value;
	if (inp.length != 19) {alert("Departure Date/Time is of invalid format"); return false;}
	else if (inp.split('-').length != 3) {alert("Departure Date/Time is of invalid format"); return false;}
	else if (inp.split(':').length != 3) {alert("Departure Date/Time is of invalid format"); return false;}
	else if (inp.split(' ').length != 2) {alert("Departure Date/Time is of invalid format"); return false;}
	else if (inp.split(' ')[0] != document.querySelector("#date").value) {alert("Date does not match Departure Date"); return false;}
	inp = document.querySelector("#arr_time").value;
	if (inp.length != 19) {"Arrival Date/Time is of invalid format"; return false;}
	else if (inp.split('-').length != 3) {alert("Arrival Date/Time is of invalid format"); return false;}
	else if (inp.split(':').length != 3) {alert("Arrival Date/Time is of invalid format"); return false;}
	else if (inp.split(' ').length != 2) {alert("Arrival Date/Time is of invalid format"); return false;}
	else {return true;}
}

// Radio buttons PF and PM----------------------------------------------------------------
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

// DELETE FLight---------------------------------------------------------------------------
function del_flt(){
	let a = confirm("Are you sure you want to delete that flight?");
	if (a)
	{
		document.querySelector("#todo").value = "delete";
		document.querySelector("#f_edit").submit();}
	}
	
// SAVE flight-------------------------------------------------------------------------------
function save_flt(){
//	check_inputs();
	if (check_inputs()){
		document.querySelector("#todo").value = "save";
		document.querySelector("#f_edit").submit();}}

// Calculate TOTAL FLIGHT TIME----------------------------------------------------------------
function calc_tot_time()
{	// check all dep/arr info present
	if (document.querySelector("#dep_time").value != "" && document.querySelector("#arr_time").value != "")
	{	// get DEP and ARR date objects
		dep_time = new Date(document.querySelector("#dep_time").value);
		arr_time = new Date(document.querySelector("#arr_time").value);
		// Get total minutes and from there minutes and hours. 1min = 60000mSec
		tot_minutes = (arr_time.getTime() - dep_time.getTime()) / 60000;
		if (tot_minutes < 0)
		{
			document.querySelector("#tot_time").value = "Error with Date/Time";
		}
		else
		{
			minutes = tot_minutes % 60;
			if (minutes < 10) {minutes = "0" + minutes;}

			hours = (tot_minutes - minutes) / 60;
			if (hours < 10) {hours = "0" + hours;}

			document.querySelector("#tot_time").value = hours + ":" + minutes;
			document.querySelector("#tot_minutes").value = tot_minutes;
		}}}

