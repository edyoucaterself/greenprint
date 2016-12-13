//Function to update date inpute if semi monthly cycle is chosen
function autoDate(date_input,cycle_input) {
    //Get cycle name and test for semi monthly
    var cycle = $("#id_payCycle option:selected").text()

    //Get current day
    var d = new Date();
    var currentday = d.getDate();
    var currentmonth = d.getMonth()+1;
    var currentyear = d.getFullYear();
    var newday = currentday;

    console.log(cycle, currentday, currentmonth, currentyear);

    if (cycle == "Semi-Monthly 1st/15th") {
        //If current day > 15 then set date_input day to 1st, else set to 15th
        if (currentday > 15){
            newday = "01";
        } else {
            newday = "15";
        }
        //Build date and set input text
        newdate = currentmonth + "/" + newday + "/" + currentyear;
        console.log(newdate);
        $('#id_nextDueDate').val(newdate);

    } else if (cycle == "Semi-Monthly 15th/Last") {
        //If current day is > 15 set to last, else set to 15th
        if (currentday > 15){
            //Find last day of month
            var lastday = new Date(currentyear, currentmonth, 0);
            newday = lastday.getDate();
        } else {
            newday = "15";
        } 
        //Build date and set input text
        newdate = currentmonth + "/" + newday + "/" + currentyear;
        $('#id_nextDueDate').val(newdate);
    }
    

}

//Function to show tooltips one at a time
function showToast(row) {
    var toast_str = row.attr("data-note");
    console.log(toast_str)
    //if toast_str empty return from script
    //test for div with class of toast-container
    if ($('#toast-container')) {
        //Remove other containers, call toast
        $('#toast-container').remove()
        Materialize.toast(toast_str, 4000);
 
    } else {
        //open toast
        Materialize.toast(toast_str, 4000);
        console.log('Container Not Found: ' + $(this));
    };
}


//Function to load form on modal with info from table row
function loadModalForm(modalform, row) { 
    //Get itemid from tr id budget-line-itemid then use name for istoday
    var rowid = row.attr("id");
    var itemid = rowid.match(/\d+/);

    //Set form path with itemid
    var formpath = "/config/" + itemid + "/";
    $(modalform).attr("action", formpath);

    //Get cycle, if single set #radios attr style to "display:none;"
    var cycle = $('[name="' + itemid +'_header"]').attr('data-cycle');
    console.log(cycle)
    if (cycle == "Single"){
        $('#radios').attr("style","display:none");
    } else {
        $('#radios').attr("style","");
    }

    //Pass values to header
    var header = $('[name="' + itemid + '_header"]').text();
    console.log(header);        
    $("#subhead").text(header);

    //Get parentItem and pass
    //find each td element and populate form 
    row.find("td").each(function(){ 
        var data=$(this).text(); 
        var line_id=$(this).attr("name");  
        //put value into form 
        var form_input=modalform + " input[id=" + line_id + "]"; 
        $(form_input).val(data); 
    }); 
    
}

//Format budget table for small screens
function mobileformat(table) {
    //Reduce padding and text size in table rows 
    $("[id^='budget-line-']").css('padding', '3');
    $("[id^='budget-line-']").css('font-size','small');
    //Remove text from buttons in head
    $("[data-tooltip='Add Expense']").text("-");
    $("[data-tooltip='Add Income']").text("+");
    //cycle through all tds with budget-line-date and change text - NOT WORKING
   //$("[name='id_itemDate']").each(function(i, obj) {
   //    var d Date($(this).text());
   //    var numdate = d.toString(MM-dd-YY);
   //    $(this).text(numdate);
   //}
   //Drop running total column
   $("[name='id_runningTotal']").remove();
   $(".tcol-total").remove();
   //format header

   //Resize text
    $("#page_header").css('font-size','medium');
   
   //Reduce padding on header card
   
    $("#header_content").css(
    {
      'padding':'2',
      'height': '30px'
    });
    

    $("#header_action").css('padding', '18');
   //Bring header and content closer together
    $("#header_row").css('margin-bottom', '2');

   //Format login page
   $("#login_form").css(
   {
     'height': '244px',
     'padding': '20px'
   });
   //Move title up
   $("#page_header").css(
   {
     'position': 'relative',
     'top': '-12px'
   });

   //Move FAB to the right
   $(".fixed-action-btn").css(
   {
     'right': '-1px',
     //'width': '8px',
     //'height': '8px'
   });
   $("#fab_lnk").removeClass('btn-large');
   $("#fab_lnk").addClass('btn');
}
