function land_curr(x)
{
	// get msec from date
	var msec = Date.parse(x);
	// add 90 days in msecs
	msec = msec + (90 * 86400000);
	// get date out of msecs
	let curr_date = new Date(msec);
	let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

	if (curr_date > Date.now())
	{ 	document.querySelector("#land_cur").style.color = 'black';

//		FUNCTION a0 is in SCRIPT.JS
		document.querySelector("#land_cur").innerHTML = a0(curr_date.getDate()) + " " + months[curr_date.getMonth()] + " " + a0(curr_date.getFullYear()); }
	else
	{ 	document.querySelector("#land_cur").style.color = 'red';
		if (isNaN(curr_date.getDate()))
		{
			document.querySelector("#land_cur").innerHTML = "Not enough data to calculate";
		}
		else
		{
			document.querySelector("#land_cur").innerHTML = "Landing currency expired on " + a0(curr_date.getDate()) + " " + months[curr_date.getMonth()] + " " + a0(curr_date.getFullYear());
		}
	}
}
