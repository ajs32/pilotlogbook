function block_page()
{
	if (document.getElementById("cover").style.display == "block")
	{
		document.getElementById("cover").style.display="none";
	}
	else
	{
		document.getElementById("cover").style.display="block";
	}
}

function min_to_time(x)
{
	if (x%60 < 10){	return String((x-x%60)/60) + ":0" + String(x%60)}
	else {return String((x-x%60)/60) + ":" + String(x%60)}
}

function pdf()
{
	// disable the page
	block_page();

	let opt = {
		margin: 0,
		filename: 'test.pdf',
		image: {type: 'jpeg', quality: 0.98},
		html2canvas: {scale: 2},
		jsPDF: {unit: 'mm', format: 'a5', orientation: 'landscape', width: 210}
	};

	let doc = html2pdf().set(opt).from(document.getElementById("l1")).toPdf();

		doc = doc.get('pdf').then(
			pdf => {pdf.addPage()}
		).from(document.getElementById("r1")).toContainer().toCanvas().toPdf();

	for (let j = 2; j <= document.querySelector("#nr_pages").innerHTML; j++)
	{
		doc = doc.get('pdf').then(
			pdf => {pdf.addPage()}
		).from(document.getElementById("l"+j)).toContainer().toCanvas().toPdf();

		doc = doc.get('pdf').then(
			pdf => {pdf.addPage()}
		).from(document.getElementById("r"+j)).toContainer().toCanvas().toPdf();
	}

	// enable the page
	block_page();

	doc.save();
}



function generate(x)
{
	let json = eval(x);

	let tbl_start_l = '<table class="print_table" id="log_tbl" name="log_tbl"><tr><th class="td" style="width: 60px;">Date</th><th class="td" style="width: 50px;">Departure Airport</th><th class="td" style="width: 50px;">Departure Time</th><th class="td" style="width: 50px;">Arrival Airport</th><th class="td" style="width: 50px;">Arrival Time</th><th class="td" style="width: 60px;">Aircraft Type</th><th class="td" style="width: 70px;">Aircraft Registration</th><th class="td" style="width: 60px;">Total Flight Time</th><th class="td" style="width: 190px;">Name PIC</th><th class="td" style="width: 20px;">PF</th></tr>';
	let tbl_start_r = '<table class="print_table" id="log_tbl" name="log_tbl"><tr><th class="td" style="width: 50px;">Night</th><th class="td" style="width: 50px;">IFR</th><th class="td" style="width: 50px;">PIC</th><th class="td" style="width: 50px;">Co-Pilot</th><th class="td" style="width: 50px;">DUAL</th><th class="td" style="width: 50px;">Instructor Examiner</th><th class="td" style="width: 70px;">SIM date</th><th class="td" style="width: 110px;">SIM Type</th><th class="td" style="width: 50px;">SIM time</th><th class="td" style="width: 140px;">Remarks</th></tr>';

	let tbl_rows_l = '';
	let tbl_rows_r = '';

	let page_nr = 1;

	let final_row_page_l = '';
	let final_row_l = '';

	let final_row_page_r = '';
	let final_row_r = '';

	let tbl_end = '</table>';
	let rem_length = json.length;

	let page_div_l = '<div class="page_left" id="';
	let page_div_r = '<div class="page_right" id="';
	let spacer_div='<div class="spacer"></div>';
	let div_end = "</div>"
	let tot_time_page = 0, tot_time = 0, land_page = 0, land = 0, night = 0, tot_night = 0, ifr = 0, tot_ifr = 0, pic = 0, tot_pic = 0, fo = 0, tot_fo = 0, dual = 0, tot_dual = 0, instr = 0, tot_instr = 0;

	let i = 0;
	let page_i = 0;
	let tot_lines = 21;
//	let tot_lines = 5;

	document.querySelector("#sheets").innerHTML = "";

	// run while remaining length is more than total length	
	while (rem_length > 0)
	{
		// zero page counters. Total counters are untouched
		page_i = 0;
		tot_time_page = 0, land_page = 0, night = 0, ifr = 0, pic = 0, fo = 0, dual = 0, instr = 0;		
		tbl_rows_l = '';
		tbl_rows_r = '';
		// reset page final rows
		final_row_page_l = '<tr><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td><td class="td">Total page</td>';
		final_row_l = '<tr><td style="border: none; text-align: left;">Page '+page_nr+'-L</td><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td><td class="td">Total</td>';		
		final_row_page_r = '';		
		final_row_r = '';		

		//Fill in the page until page counter is less than remaining length
		for (; page_i < rem_length; page_i++, i++)
		{
			// if page counter equals to max lines per page, break to start new page and reset page counters
			if (page_i == tot_lines) {break;}
			// else insert next flight data onto the page
			tbl_rows_l += '<tr><td class="td">'+json[i]["date"]+'</td><td class="td">'+json[i]["iata1"]+'</td><td class="td">'+json[i]["dep_time"].slice(-8,-3)+'</td><td class="td">'+json[i]["iata2"]+'</td><td class="td">'+json[i]["arr_time"].slice(-8,-3)+'</td><td class="td">'+json[i]["type"]+'</td><td class="td">'+json[i]["tail"]+'</td><td class="td">'+min_to_time(json[i]["tot_time"])+'</td><td class="td">'+json[i]["name"]+'</td><td class="td">'+json[i]["to_land"]+'</td></tr>';

			tot_time_page += json[i]["tot_time"];
			if (json[i]["to_land"] == 'Y') {land_page += 1;}

			tbl_rows_r += '<tr><td class="td">'+min_to_time(json[i]["night"])+'</td><td class="td">'+min_to_time(json[i]["ifr"])+'</td><td class="td">'+min_to_time(json[i]["pic_time"])+'</td><td class="td">'+min_to_time(json[i]["fo_time"])+'</td><td class="td">'+min_to_time(json[i]["dual"])+'</td><td class="td">'+min_to_time(json[i]["instructor"]+json[i]["examiner"])+'</td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td">'+json[i]["res1"]+'</td></tr>';

			night += json[i]["night"];
			ifr += json[i]["ifr"];
			pic += json[i]["pic_time"];
			fo += json[i]["fo_time"];
			dual += json[i]["dual"];
			instr += json[i]["instructor"];
		}

		// add page counters to total counters
		tot_time += tot_time_page;
		tot_night += night;
		tot_ifr += ifr;
		tot_pic += pic;
		tot_fo += fo;
		tot_dual += dual;
		tot_instr += instr;
		land += land_page

		// include final rows
		final_row_page_l += '<td class="td">'+min_to_time(tot_time_page)+'</td><td class="td">TO/Landings on page</td><td class="td">'+land_page+'</td></tr>';
		final_row_l += '<td class="td">'+min_to_time(tot_time)+'</td><td class="td">Total TO/Landings</td><td class="td">'+land+'</td></tr>';

		final_row_page_r = '<tr><td class="td">'+min_to_time(night)+'</td><td class="td">'+min_to_time(ifr)+'</td><td class="td">'+min_to_time(pic)+'</td><td class="td">'+min_to_time(fo)+'</td><td class="td">'+min_to_time(dual)+'</td><td class="td">'+min_to_time(instr)+'</td><td style="border: none;"></td style="border: none;"><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td></tr>';
		final_row_r += '<tr><td class="td">'+min_to_time(tot_night)+'</td><td class="td">'+min_to_time(tot_ifr)+'</td><td class="td">'+min_to_time(tot_pic)+'</td><td class="td">'+min_to_time(tot_fo)+'</td><td class="td">'+min_to_time(tot_dual)+'</td><td class="td">'+min_to_time(tot_instr)+'</td><td style="border: none;"></td><td style="border: none;"></td><td style="border: none;"></td><td style="border: none; text-align:right;">Page '+page_nr+'-R</td></tr>';

		// if page line counter is less than total lines, but rem_length is 0, fill the page with empty lines
		if (page_i < tot_lines)
		{
			for (let j = 0; j < (tot_lines - page_i); j++)
			{
				tbl_rows_l += '<tr><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td></tr>';
				tbl_rows_r += '<tr><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td class="td"><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td><td class="td"></td></tr>';
			}
		}	

		// create final tables
		final_tbl_l = tbl_start_l + tbl_rows_l + final_row_page_l + final_row_l + tbl_end;
		final_tbl_r = tbl_start_r + tbl_rows_r + final_row_page_r + final_row_r + tbl_end;

		// write final tables
		document.querySelector("#sheets").innerHTML += spacer_div + page_div_l + "l" + page_nr + '">' + final_tbl_l + div_end + spacer_div + page_div_r + 'r' + page_nr + '">'  + final_tbl_r+ div_end;

		// reduce remaining length and add number of pages
		rem_length -= page_i;
		page_nr += 1;;
	}
	// announce ammount of pages (required for print) and enable print button
	document.querySelector("#pages").innerHTML = "Total pages generated: ";
	document.querySelector("#nr_pages").innerHTML = page_nr - 1;
	document.querySelector("#b_print").disabled = false;
}


function req_logbook()
{
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	    if (this.readyState == 4 && this.status == 200) {
	       // If ERROR is returned
			if (xhttp.responseText[0] == "E"){
				document.querySelector("#msg_logbook").style.color = 'red';
				document.getElementById("msg_logbook").innerHTML = xhttp.responseText; }
			else{
				generate(xhttp.responseText);
				}
	    }
	};
	
	xhttp.open("POST", "/print", true);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send("todo=logbook");

}

