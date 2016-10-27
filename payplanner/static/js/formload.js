//Function to highlight first row of today
function isToday(table) {
    $('[id^="budget-line"]').each(function(){ 
        //get istoday in id  
        if ($(this).attr("name") == "True"){; 
            var rowclass=$(this).attr("class");
            rowclass = rowclass + ' orange lighten-4';
            console.log(rowclass);
            $(this).attr("class", rowclass);
            exit();
        };
    });
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
    var cycle = $('[name="' + itemid +'_cycle"]').text();
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
